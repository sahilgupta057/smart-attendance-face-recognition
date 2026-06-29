from PyQt5.QtWidgets import QWidget, QGraphicsBlurEffect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter

class BlurOverlay(QWidget):
    """
    Semi-transparent blur overlay to highlight popups.
    Usage:
        overlay = BlurOverlay(parent_widget)
        overlay.show()
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.setGeometry(parent.rect())
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # Pass clicks through
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_StyledBackground)

        # Semi-transparent dark background
        self.bg_color = QColor(0, 0, 0, 120)  # RGBA

        # Blur effect
        blur_effect = QGraphicsBlurEffect(self)
        blur_effect.setBlurRadius(15)
        self.setGraphicsEffect(blur_effect)

        self.show()

    def paintEvent(self, event):
        """Paint semi-transparent dark layer over parent."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), self.bg_color)
