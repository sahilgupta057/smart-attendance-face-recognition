import os
import cv2
import numpy as np

from PyQt5 import QtWidgets, QtCore, QtGui
from camera.camera_thread import CameraThread


class CameraCapturePopup(QtWidgets.QDialog):

    captured = QtCore.pyqtSignal(str)   # emits saved image path on success

    def __init__(self, student_name: str, save_dir: str, parent=None):
        super().__init__(parent)
        self.student_name = student_name
        self.save_dir     = save_dir
        self.cam_thread   = None
        self._saved_path  = None

        self._build_ui()
        self._start_camera()

    # ── UI ────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.setWindowTitle(f"Capture Face – {self.student_name}")
        self.setFixedSize(680, 540)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # outer card
        card = QtWidgets.QFrame(self)
        card.setGeometry(0, 0, 680, 540)
        card.setObjectName("card")
        card.setStyleSheet("""
            QFrame#card {
                background: #1a1f2e;
                border-radius: 16px;
                border: 1px solid #2d3452;
            }
        """)

        root = QtWidgets.QVBoxLayout(card)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(10)

        # ── title bar ────────────────────────────────────────────────
        title_row = QtWidgets.QHBoxLayout()

        icon = QtWidgets.QLabel("📸")
        icon.setStyleSheet("font-size:20px;")

        title = QtWidgets.QLabel(f"Capture face for <b>{self.student_name}</b>")
        title.setStyleSheet("color:#dde4ff; font-size:14px;")

        close_btn = QtWidgets.QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background:#2d3452; color:#99a; border-radius:14px;
                font-size:13px; font-weight:bold; border:none;
            }
            QPushButton:hover { background:#c0392b; color:white; }
        """)
        close_btn.clicked.connect(self._on_cancel)

        title_row.addWidget(icon)
        title_row.addSpacing(6)
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(close_btn)
        root.addLayout(title_row)

        # ── camera preview ────────────────────────────────────────────
        self.preview = QtWidgets.QLabel("Starting camera…")
        self.preview.setFixedSize(644, 400)
        self.preview.setAlignment(QtCore.Qt.AlignCenter)
        self.preview.setStyleSheet("""
            background:#0d1117;
            border-radius:10px;
            border:2px solid #2d3452;
            color:#555; font-size:13px;
        """)
        root.addWidget(self.preview, alignment=QtCore.Qt.AlignHCenter)

        # ── bottom bar ────────────────────────────────────────────────
        bottom = QtWidgets.QHBoxLayout()

        self.status_lbl = QtWidgets.QLabel("📷 Position face in frame")
        self.status_lbl.setStyleSheet("color:#7ecfff; font-size:12px;")

        self.capture_btn = QtWidgets.QPushButton("📷  Capture Now")
        self.capture_btn.setFixedSize(150, 36)
        self.capture_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.capture_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #0ea5e9, stop:1 #6366f1);
                color: white; border-radius: 8px;
                font-size: 13px; font-weight: 600; border: none;
            }
            QPushButton:hover { background: #0284c7; }
            QPushButton:disabled { background: #2d3452; color: #555; }
        """)
        self.capture_btn.clicked.connect(self._force_capture)

        bottom.addWidget(self.status_lbl)
        bottom.addStretch()
        bottom.addWidget(self.capture_btn)
        root.addLayout(bottom)

    # ── camera ────────────────────────────────────────────────────────

    def _start_camera(self):
        self.cam_thread = CameraThread(
            student_name=self.student_name,
            save_dir=self.save_dir
        )
        self.cam_thread.frame_ready.connect(self._show_frame)
        self.cam_thread.capture_finished.connect(self._on_captured)
        self.cam_thread.status.connect(self._on_status)
        self.cam_thread.error.connect(self._on_error)
        self.cam_thread.start()

    def _show_frame(self, frame: np.ndarray):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_img  = QtGui.QImage(rgb.data, w, h, ch * w, QtGui.QImage.Format_RGB888)
        pixmap  = QtGui.QPixmap.fromImage(qt_img).scaled(
            self.preview.width(), self.preview.height(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )
        self.preview.setPixmap(pixmap)

    def _on_status(self, msg: str):
        self.status_lbl.setText(msg)
        # green on success, yellow on warning
        if "✅" in msg:
            self.status_lbl.setStyleSheet("color:#22c55e; font-size:12px;")
        elif "⚠️" in msg:
            self.status_lbl.setStyleSheet("color:#f59e0b; font-size:12px;")
        else:
            self.status_lbl.setStyleSheet("color:#7ecfff; font-size:12px;")

    def _on_error(self, msg: str):
        self.status_lbl.setText(msg)
        self.status_lbl.setStyleSheet("color:#ef4444; font-size:12px;")
        self.capture_btn.setEnabled(False)
        # Show retry button
        self.capture_btn.setText("🔄  Retry Camera")
        self.capture_btn.setEnabled(True)
        self.capture_btn.clicked.disconnect()
        self.capture_btn.clicked.connect(self._retry_camera)
        QtWidgets.QMessageBox.warning(
    self,
    "Camera Error",
    f"{msg}\n\nMake sure no other app is using the camera,\nthen click Retry Camera."
)

    def _on_captured(self, path: str):
        """Called by CameraThread when auto-capture succeeds."""
        self._saved_path = path
        self._stop_camera()

        # show thumbnail
        if os.path.exists(path) and os.path.getsize(path) > 0:
            pix = QtGui.QPixmap(path).scaled(
                self.preview.width(), self.preview.height(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            self.preview.setPixmap(pix)
        else:
            print("⚠️ Invalid captured image path:", path)
        self.status_lbl.setText("✅ Face captured! Closing…")
        self.status_lbl.setStyleSheet("color:#22c55e; font-size:13px; font-weight:600;")
        self.capture_btn.setEnabled(False)

        # emit signal then close after short delay so user sees thumbnail
        self.captured.emit(path)
        QtCore.QTimer.singleShot(1200, self.accept)

    def _force_capture(self):
        """
        Manual capture button — lowers quality thresholds and saves
        the current frame immediately using OpenCV Haar detection.
        """
        self.capture_btn.setEnabled(False)
        self.status_lbl.setText("📸 Capturing…")

        if self.cam_thread and self.cam_thread.isRunning():
            # Lower the blur threshold temporarily so it passes
            self.cam_thread.blur_threshold = 20
            self.cam_thread.dark_threshold = 20

    def _retry_camera(self):
        """Stop existing thread and restart camera."""
        self._stop_camera()
        self.capture_btn.setText("📷  Capture Now")
        self.capture_btn.clicked.disconnect()
        self.capture_btn.clicked.connect(self._force_capture)
        self.capture_btn.setEnabled(True)
        self.status_lbl.setText("📷 Position face in frame")
        self.status_lbl.setStyleSheet("color:#7ecfff; font-size:12px;")
        self.preview.setText("Starting camera…")
        self._start_camera()

    # ── cleanup ───────────────────────────────────────────────────────

    def _stop_camera(self):
        if self.cam_thread and self.cam_thread.isRunning():
            self.cam_thread.running = False
            self.cam_thread.quit()
            self.cam_thread.wait(2000)

    def _on_cancel(self):
        self._stop_camera()
        self.reject()

    def closeEvent(self, event):
        self._stop_camera()
        super().closeEvent(event)
