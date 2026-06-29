import os
import cv2
import numpy as np
import face_recognition

from PyQt5 import QtCore
from PyQt5.QtCore import QSettings


# How many good frames to collect before finishing
CAPTURE_TARGET = 5
# Minimum frames between captures (avoids near-duplicate frames)
CAPTURE_INTERVAL = 8


class CameraThread(QtCore.QThread):

    frame_ready      = QtCore.pyqtSignal(np.ndarray)
    capture_finished = QtCore.pyqtSignal(str)   # emits save_dir path
    error            = QtCore.pyqtSignal(str)
    status           = QtCore.pyqtSignal(str)

    def __init__(self, student_name, save_dir):
        super().__init__()

        self.student_name = student_name
        self.save_dir     = save_dir
        self.running      = True

        self.settings         = QSettings("AI_Attendance_System", "AppSettings")
        self.camera_index     = self.settings.value("camera",          0,  type=int)
        self.blur_threshold   = self.settings.value("blur_threshold",  80, type=int)
        self.dark_threshold   = self.settings.value("dark_threshold",  50, type=int)

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    # ── quality helpers ───────────────────────────────────────────────

    def _is_blurry(self, gray):
        return cv2.Laplacian(gray, cv2.CV_64F).var() < self.blur_threshold

    def _is_dark(self, gray):
        return np.mean(gray) < self.dark_threshold

    def _improve_light(self, img):
        ycrcb     = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)
        y         = cv2.equalizeHist(y)
        return cv2.cvtColor(cv2.merge((y, cr, cb)), cv2.COLOR_YCrCb2BGR)

    # ── main loop ─────────────────────────────────────────────────────

    def run(self):
        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            self.error.emit("❌ Camera not available")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        os.makedirs(self.save_dir, exist_ok=True)
        safe_name = self.student_name.replace(" ", "_")

        # ── delete any previous images for this student ───────────────
        for f in os.listdir(self.save_dir):
            if f.startswith(safe_name + "_") or f == safe_name + ".jpg":
                os.remove(os.path.join(self.save_dir, f))

        captured    = 0          # good frames saved so far
        frame_count = 0          # total frames read
        last_cap_at = -CAPTURE_INTERVAL  # frame index of last capture

        self.status.emit("📷 Look straight at the camera…")

        while self.running and captured < CAPTURE_TARGET:
            ret, frame = cap.read()
            if not ret:
                continue

            frame_count += 1
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # ── live preview ──────────────────────────────────────────
            faces_haar = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100)
            )
            preview = frame.copy()
            for (fx, fy, fw, fh) in faces_haar:
                # progress bar colour: orange → green as captures increase
                progress = captured / CAPTURE_TARGET
                g = int(220 * progress)
                r = int(220 * (1 - progress))
                color = (0, g + 60, r)
                cv2.rectangle(preview, (fx, fy), (fx + fw, fy + fh), color, 2)
                cv2.putText(preview,
                            f"Captured {captured}/{CAPTURE_TARGET}",
                            (fx, fy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            self.frame_ready.emit(preview)

            # ── attempt capture every CAPTURE_INTERVAL frames ─────────
            if (frame_count - last_cap_at) < CAPTURE_INTERVAL:
                continue
            if len(faces_haar) == 0:
                self.status.emit("👤 No face detected – move closer")
                continue

            # largest detected face
            x, y, w, h = max(faces_haar, key=lambda f: f[2] * f[3])

            # crop with margin
            m  = int(0.25 * w)
            x1 = max(0, x - m)
            y1 = max(0, y - m)
            x2 = min(frame.shape[1], x + w + m)
            y2 = min(frame.shape[0], y + h + m)
            face_crop = frame[y1:y2, x1:x2]
            if face_crop.size == 0:
                continue

            # quality checks
            face_gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
            if self._is_dark(face_gray):
                face_crop = self._improve_light(face_crop)
                face_gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
            if self._is_blurry(face_gray):
                self.status.emit("⚠️ Blurry – hold still")
                continue

            # verify encodable
            rgb_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            locs     = face_recognition.face_locations(rgb_crop, model="hog")
            if not locs:
                self.status.emit("⚠️ Can't encode – try better lighting")
                continue
            encs = face_recognition.face_encodings(rgb_crop, locs)
            if not encs:
                self.status.emit("⚠️ Encoding failed – adjust position")
                continue

            # save
            face_out  = cv2.resize(face_crop, (400, 400))
            save_path = os.path.join(self.save_dir, f"{safe_name}_{captured}.jpg")
            cv2.imwrite(save_path, face_out)

            captured    += 1
            last_cap_at  = frame_count
            self.status.emit(f"✅ Captured {captured} / {CAPTURE_TARGET} — keep still…")

        cap.release()

        if captured == CAPTURE_TARGET:
            self.status.emit("🎉 All images captured successfully!")
            # Emit the directory so FaceRecognitionThread can load all images
            last_saved = os.path.join(self.save_dir, f"{safe_name}_{captured - 1}.jpg")
            self.capture_finished.emit(last_saved)
        else:
            self.status.emit("⚠️ Capture incomplete – please retry")

    def stop(self):
        self.running = False
