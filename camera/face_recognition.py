import os
import cv2
import numpy as np
import dlib
import face_recognition
import time
from concurrent.futures import ThreadPoolExecutor
from scipy.spatial import distance as scipy_dist
from scipy.spatial import cKDTree

from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtMultimedia import QSoundEffect

from attendance_manager import AttendanceManager


# ── tuneable ──────────────────────────────────────────────────────────────────
PROCESS_EVERY     = 2       # ↓ was 4 — inference every N frames (faster response)
SCALE             = 0.25    # detection downscale
EAR_THRESH        = 0.22    # eye aspect ratio blink threshold (slightly more sensitive)
EAR_CONSEC        = 1       # frames eye must be closed to count as blink
BLINK_CHECK_EVERY = 1       # ↓ was 2 — run dlib EVERY frame per face (no throttle)
MIN_HITS_TO_BLINK = 2       # ↓ was 3 — min consecutive matches before enabling blink
# ──────────────────────────────────────────────────────────────────────────────


def _ear(pts):
    A = scipy_dist.euclidean(pts[1], pts[5])
    B = scipy_dist.euclidean(pts[2], pts[4])
    C = scipy_dist.euclidean(pts[0], pts[3])
    return (A + B) / (2.0 * C)


class FaceRecognitionThread(QThread):

    frame_updated     = pyqtSignal(np.ndarray)
    status_message    = pyqtSignal(str)
    attendance_marked = pyqtSignal(str, str)    # roll, name
    stats_updated     = pyqtSignal(float, float)

    def __init__(self, username, account_id, known_faces, known_names,
                 settings=None):
        super().__init__()

        self.settings    = settings or {}
        self.username    = username
        self.account_id  = account_id
        self.known_faces = list(known_faces)
        self.known_names = list(known_names)
        self.running     = True

        # ── settings ──────────────────────────────────────────────────
        self.camera_index = int(self.settings.get("camera_index", 0))
        self.max_faces    = int(self.settings.get("max_faces", 5))
        conf              = float(self.settings.get("confidence", 45))
        self.threshold    = round(1.0 - conf / 100.0, 3)

        # ── KD-tree (float64 required) ────────────────────────────────
        if self.known_faces:
            arr        = np.array(self.known_faces, dtype=np.float64)
            self._tree = cKDTree(arr)
        else:
            self._tree = None

        # ── attendance state ──────────────────────────────────────────
        self.att_manager  = AttendanceManager(self.username)
        self.marked_rolls = set()
        self.hit_counts   = {}          # roll → consecutive match count
        self.blink_ctrs   = {}          # roll → frames eye was closed
        self.blinked      = set()       # rolls that confirmed a blink

        # ── blink throttle ────────────────────────────────────────────
        self._blink_frame_count = {}

        # ── dlib landmark predictor ───────────────────────────────────
        self.predictor = dlib.shape_predictor(
            "shape_predictor_68_face_landmarks.dat"
        )

        # ── inference state ───────────────────────────────────────────
        self._faces: list[dict] = []
        self._inference_running = False
        self._last_inf_ms       = 0.0
        self._last_acc          = 0.0
        self._executor          = ThreadPoolExecutor(max_workers=1)

        # ── sound ─────────────────────────────────────────────────────
        self._sound = QSoundEffect()
        wav = os.path.abspath(os.path.join("sounds", "success.wav"))
        if os.path.exists(wav):
            self._sound.setSource(QUrl.fromLocalFile(wav))
            self._sound.setVolume(1.0)

    # ── helpers ───────────────────────────────────────────────────────

    def _resolve(self, idx: int):
        """Return (name, roll) from known_names at position idx."""
        entry = self.known_names[idx]
        if isinstance(entry, (list, tuple)) and len(entry) >= 2:
            return str(entry[0]), str(entry[1])
        parts = str(entry).split("_")
        return parts[0], parts[-1]

    def _identify(self, enc: np.ndarray):
        """Return (name, roll, accuracy_pct) or (None, None, raw_acc)."""
        if self._tree is None:
            return None, None, 0.0

        enc64     = np.array(enc, dtype=np.float64)
        dist, idx = self._tree.query(enc64, k=1)
        dist      = float(dist)
        acc       = max(0.0, (1.0 - dist) * 100.0)

        if dist > self.threshold:
            return None, None, acc

        name, roll = self._resolve(int(idx))
        return name, roll, acc

    def _run_inference(self, frame: np.ndarray):
        """
        Heavy recognition — runs in ThreadPoolExecutor.
        Camera loop is never blocked.
        """
        try:
            t0    = time.perf_counter()
            small = cv2.resize(frame, (0, 0), fx=SCALE, fy=SCALE)
            rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

            locs = face_recognition.face_locations(rgb, model="hog")
            locs = locs[: self.max_faces]

            encs = face_recognition.face_encodings(
                rgb, locs, num_jitters=0, model="small"
            ) if locs else []

            new_faces = []
            best_acc  = 0.0
            for enc, (top, right, bottom, left) in zip(encs, locs):
                x1 = int(left   / SCALE)
                y1 = int(top    / SCALE)
                x2 = int(right  / SCALE)
                y2 = int(bottom / SCALE)

                name, roll, acc = self._identify(enc)
                if acc > best_acc:
                    best_acc = acc
                new_faces.append(dict(
                    name=name, roll=roll,
                    accuracy=acc, box=(x1, y1, x2, y2)
                ))

            self._faces       = new_faces
            self._last_inf_ms = (time.perf_counter() - t0) * 1000
            self._last_acc    = best_acc
            self.stats_updated.emit(self._last_inf_ms / 1000.0, best_acc)

        except Exception:
            pass
        finally:
            self._inference_running = False

    def _blink_check(self, roll: str, frame: np.ndarray, box) -> bool:
        """
        Fast blink detection on a small cropped face region.
        Returns True the moment a blink is confirmed.

        Optimised:
          - No per-face frame throttle (BLINK_CHECK_EVERY=1, runs every frame)
          - Grayscale conversion BEFORE resize saves compute on larger crops
          - Uses cached gray frame across multiple face calls in same frame
        """
        if roll in self.blinked:
            return True

        # ── optional throttle (BLINK_CHECK_EVERY=1 disables it) ──────
        if BLINK_CHECK_EVERY > 1:
            cnt = self._blink_frame_count.get(roll, 0) + 1
            self._blink_frame_count[roll] = cnt
            if cnt % BLINK_CHECK_EVERY != 0:
                return False

        try:
            x1, y1, x2, y2 = [int(v) for v in box]

            pad = 20
            fx1 = max(0, x1 - pad)
            fy1 = max(0, y1 - pad)
            fx2 = min(frame.shape[1], x2 + pad)
            fy2 = min(frame.shape[0], y2 + pad)
            crop = frame[fy1:fy2, fx1:fx2]

            if crop.size == 0:
                return False

            # ── convert to gray FIRST (smaller color→gray conversion) ─
            gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

            # ── resize gray crop (faster than resizing BGR then converting)
            target_w = 160
            scale_f  = target_w / max(gray_crop.shape[1], 1)
            small    = cv2.resize(
                gray_crop,
                (target_w, max(1, int(gray_crop.shape[0] * scale_f))),
                interpolation=cv2.INTER_LINEAR   # fastest quality/speed trade-off
            )

            rect  = dlib.rectangle(0, 0, small.shape[1], small.shape[0])
            shape = self.predictor(small, rect)

            l_eye = [(shape.part(i).x, shape.part(i).y) for i in range(36, 42)]
            r_eye = [(shape.part(i).x, shape.part(i).y) for i in range(42, 48)]
            ear   = (_ear(l_eye) + _ear(r_eye)) / 2.0

            blink_cnt = self.blink_ctrs.get(roll, 0)
            if ear < EAR_THRESH:
                self.blink_ctrs[roll] = blink_cnt + 1
            else:
                if blink_cnt >= EAR_CONSEC:
                    self.blinked.add(roll)
                    return True
                self.blink_ctrs[roll] = 0

        except Exception:
            pass

        return False

    def _mark(self, name: str, roll: str):
        self.marked_rolls.add(roll)
        self.att_manager.mark_attendance(roll, self.account_id, "Present")
        if not self._sound.source().isEmpty():
            self._sound.play()
        self.status_message.emit(f"✅ {name} marked present")
        self.attendance_marked.emit(roll, name)

    # ── main loop ─────────────────────────────────────────────────────

    def run(self):
        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            self.status_message.emit("❌ Cannot open camera")
            return

        cap.set(cv2.CAP_PROP_FPS,          30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE,    1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        frame_idx = 0
        t_prev    = time.perf_counter()

        # ── per-frame gray cache: avoids redundant BGR→gray for multi-face frames
        _cached_gray_frame_idx = -1
        _cached_gray           = None

        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            frame_idx += 1

            # ── submit inference to thread pool (non-blocking) ─────────
            if frame_idx % PROCESS_EVERY == 0 and not self._inference_running:
                self._inference_running = True
                self._executor.submit(self._run_inference, frame.copy())

            # ── DRAW + BLINK + MARK every frame ───────────────────────
            for face in self._faces:
                name = face["name"]
                roll = face["roll"]
                acc  = face["accuracy"]
                x1, y1, x2, y2 = face["box"]

                # unknown face — red box
                if name is None:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 2)
                    cv2.putText(frame, f"Unknown {acc:.0f}%",
                                (x1, max(y1 - 8, 12)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 200), 2)
                    continue

                done = roll in self.marked_rolls
                hits = self.hit_counts.get(roll, 0) + 1
                self.hit_counts[roll] = hits

                # blink gate — needs MIN_HITS_TO_BLINK stable matches first
                if not done and hits >= MIN_HITS_TO_BLINK:
                    if self._blink_check(roll, frame, (x1, y1, x2, y2)):
                        self._mark(name, roll)
                        done = True

                # colour: orange=done  green=blink-ready  cyan=accumulating
                color = (0, 165, 255) if done else \
                        (0, 220, 0)   if hits >= MIN_HITS_TO_BLINK else \
                        (0, 200, 200)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                if done:
                    label = f"{name}  ✓ Present"
                elif hits >= MIN_HITS_TO_BLINK:
                    label = f"{name} {acc:.0f}%  — blink to confirm"
                else:
                    label = f"{name} {acc:.0f}%  hold still…"

                (tw, th), _ = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.52, 1)
                cv2.rectangle(frame,
                              (x1, max(y1 - th - 10, 0)),
                              (x1 + tw + 6, y1), color, cv2.FILLED)
                cv2.putText(frame, label, (x1 + 3, max(y1 - 5, 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 0, 0), 1)

            # ── HUD ───────────────────────────────────────────────────
            now    = time.perf_counter()
            delta  = now - t_prev
            t_prev = now
            fps    = 1.0 / delta if delta > 0 else 0

            cv2.putText(frame, f"FPS: {fps:.0f}",
                        (10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                        (255, 210, 0), 2)
            cv2.putText(frame, f"Faces: {len(self._faces)}",
                        (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                        (200, 200, 200), 1)
            cv2.putText(frame, f"Inf: {self._last_inf_ms:.0f}ms",
                        (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.50,
                        (180, 180, 180), 1)

            self.frame_updated.emit(frame)

        cap.release()
        self._executor.shutdown(wait=False)
        self.att_manager.close()

    def stop(self):
        self.running = False