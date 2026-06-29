from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from UI.interface2 import *
from Custom_Widgets.Widgets import *
from utils.database import *
from utils.main_dashboard import *


class ToastNotification(QtWidgets.QWidget):
    """A small floating notification widget."""
    def __init__(self, parent, message, duration=2000):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.ToolTip)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)

        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)

        label = QtWidgets.QLabel(message)
        label.setStyleSheet("color: #FFF; font-size: 13px;")
        layout.addWidget(label)

        self.setStyleSheet("background-color: rgba(0, 180, 216, 180); border-radius: 10px;")

        # Fade animation
        self.opacity = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.anim = QtCore.QPropertyAnimation(self.opacity, b"opacity")
        self.anim.setDuration(1000)

        # Position the toast in the center of parent
        geo = parent.geometry()
        self.adjustSize()
        x = geo.x() + (geo.width() - self.width()) // 2
        y = geo.y() + geo.height() - 100
        self.move(x, y)

        # Show and animate
        self.show()
        self.fade_in_out(duration)

    def fade_in_out(self, duration):
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setDuration(300)
        self.anim.finished.connect(lambda: QtCore.QTimer.singleShot(duration, self.fade_out))
        self.anim.start()

    def fade_out(self):
        self.anim.stop()
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.setDuration(800)
        self.anim.finished.connect(self.close)
        self.anim.start()

