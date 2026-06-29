from PyQt5 import QtWidgets, QtGui, QtCore
from utils.open_popup_sound import PopupSound


class BasePopup(QtWidgets.QDialog):
    def __init__(self, parent=None, width=400, height=300, radius=15):
        super().__init__(parent)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        self.setModal(True)
        self.resize(width, height)
        self.radius = radius

        # Rounded corners
        self.setWindowMask()

        # Drop shadow
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QtGui.QColor(0, 0, 0, 150))
        self.setGraphicsEffect(shadow)

        # Popup sound (same for all popups)
        self.popup_sound = PopupSound()

        # Close popup when clicking outside
        self.installEventFilter(self)
        if parent:
            parent.installEventFilter(self)

    def setWindowMask(self):
        rect = QtCore.QRectF(self.rect())
        path = QtGui.QPainterPath()
        path.addRoundedRect(rect, self.radius, self.radius)
        region = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    # Play sound when popup opens
    def showEvent(self, event):
        super().showEvent(event)
        self.popup_sound.play_openPopup()

    # Close when clicking outside
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if not self.geometry().contains(event.globalPos()):
                self.close()
                return True
        return super().eventFilter(obj, event)
