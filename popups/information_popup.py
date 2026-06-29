from PyQt5 import QtWidgets, QtCore, QtGui
from utils.open_popup_sound import PopupSound
from UI.information_popup_ui import Ui_InformationPopup


class InformationPopup(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_InformationPopup()
        self.ui.setupUi(self)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.radius      = 20
        self.popup_sound = PopupSound()
        self._connected_thread = None   # track which thread we're connected to
        self.setWindowMask()

        # ── Try to connect to whatever thread is already running ──────────────
        self._try_connect_thread()

        # ── Poll every second — reconnects if thread starts after popup opens ─
        self._poll_timer = QtCore.QTimer(self)
        self._poll_timer.timeout.connect(self._try_connect_thread)
        self._poll_timer.start(1000)

        # ── Connections ───────────────────────────────────────────────────────
        self.ui.close_btn.clicked.connect(self.close)

        self.installEventFilter(self)
        if parent:
            parent.installEventFilter(self)

    # ── Thread connection ─────────────────────────────────────────────────────

    def _try_connect_thread(self):
        """
        Find the active recognition thread on the parent window and connect
        its stats_updated signal.  Called on open and every second via timer.
        """
        parent = self.parent()
        if not parent:
            self._show_standby()
            return

        # Try attendance_thread first, then face_thread
        thread = getattr(parent, "attendance_thread", None) or \
                 getattr(parent, "face_thread", None)

        # Nothing running
        if not thread or not thread.isRunning():
            if self._connected_thread is not None:
                # Thread stopped since we last connected — go back to standby
                self._connected_thread = None
                self._show_standby()
            return

        # Already connected to this thread
        if thread is self._connected_thread:
            return

        # Disconnect old thread if any
        if self._connected_thread is not None:
            try:
                self._connected_thread.stats_updated.disconnect(self._on_stats)
            except Exception:
                pass

        # Connect new thread
        if hasattr(thread, "stats_updated"):
            thread.stats_updated.connect(self._on_stats)
            self._connected_thread = thread
            print("[InfoPopup] Connected to recognition thread ✅")
        else:
            self._show_standby()

    # ── Slot — receives (inference_time_sec, accuracy_pct) ───────────────────

    def _on_stats(self, inf_time: float, accuracy: float):
        """Called by FaceRecognitionThread.stats_updated signal."""
        v_time = self.ui.v_lab_time
        v_acc  = self.ui.v_lab_acc

        # ── Inference time ────────────────────────────────────────────────────
        if v_time:
            # Thread emits seconds; display as ms for readability
            ms = inf_time * 1000
            v_time.setText(f"{ms:.0f}ms")

            if ms < 50:
                col = "#00FFB3"   # green  — fast
            elif ms < 100:
                col = "#FFB300"   # amber  — acceptable
            else:
                col = "#FF6B6B"   # red    — slow

            v_time.setStyleSheet(
                f"color:{col}; font-size:26px; font-weight:700; font-family:'Consolas';")

        # ── Model accuracy ────────────────────────────────────────────────────
        if v_acc:
            if accuracy > 0:
                v_acc.setText(f"{accuracy:.1f}%")
                col = "#00FFB3" if accuracy >= 90 else \
                      "#FFB300" if accuracy >= 70 else "#FF6B6B"
                v_acc.setStyleSheet(
                    f"color:{col}; font-size:26px; font-weight:700; font-family:'Consolas';")
            else:
                v_acc.setText("Scanning…")
                v_acc.setStyleSheet(
                    "color:#555; font-size:26px; font-weight:700; font-family:'Consolas';")

    # ── Standby state ─────────────────────────────────────────────────────────

    def _show_standby(self):
        """Grey dashes when no thread is running."""
        style = "color:#333; font-size:26px; font-weight:700; font-family:'Consolas';"
        if self.ui.v_lab_time:
            self.ui.v_lab_time.setText("—")
            self.ui.v_lab_time.setStyleSheet(style)
        if self.ui.v_lab_acc:
            self.ui.v_lab_acc.setText("—")
            self.ui.v_lab_acc.setStyleSheet(style)

    # ── Cleanup on close ──────────────────────────────────────────────────────

    def closeEvent(self, event):
        self._poll_timer.stop()
        if self._connected_thread is not None:
            try:
                self._connected_thread.stats_updated.disconnect(self._on_stats)
            except Exception:
                pass
        super().closeEvent(event)

    # ── Rounded mask ─────────────────────────────────────────────────────────

    def setWindowMask(self):
        rect = QtCore.QRectF(self.rect())
        path = QtGui.QPainterPath()
        path.addRoundedRect(rect, self.radius, self.radius)
        region = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    # ── Sound ─────────────────────────────────────────────────────────────────

    def showEvent(self, event):
        super().showEvent(event)
        self.popup_sound.play_openPopup()

    # ── Close on outside click ────────────────────────────────────────────────

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if not self.geometry().contains(QtGui.QCursor.pos()):
                self.close()
                return True
        return super().eventFilter(obj, event)


# ── Helper ────────────────────────────────────────────────────────────────────

def open_information_popup(parent):
    dialog = InformationPopup(parent)

    parent_pos = parent.mapToGlobal(QtCore.QPoint(0, 0))
    x = parent_pos.x() + 10
    y = parent_pos.y() + parent.height() - dialog.height() - 10

    dialog.move(x, y)
    dialog.show()
