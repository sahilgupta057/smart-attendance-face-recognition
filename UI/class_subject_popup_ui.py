from PyQt5 import QtWidgets, QtCore


class Ui_ClassSubjectPopup(object):
    def setupUi(self, Dialog):
        Dialog.setFixedSize(420, 260)
        Dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)

        # ================= ROOT =================
        self.root = QtWidgets.QVBoxLayout(Dialog)
        self.root.setContentsMargins(24, 20, 24, 24)
        self.root.setSpacing(18)

        # ================= TITLE =================
        self.title = QtWidgets.QLabel("Select Teaching Account")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setStyleSheet("""
            color:#00b4d8;
            font-size:22px;
            font-weight:600;
        """)

        self.subtitle = QtWidgets.QLabel("Choose class & subject")
        self.subtitle.setAlignment(QtCore.Qt.AlignCenter)
        self.subtitle.setStyleSheet("""
            color:#888;
            font-size:13px;
        """)

        self.root.addWidget(self.title)
        self.root.addWidget(self.subtitle)

        # ================= COMBO =================
        self.combo = QtWidgets.QComboBox()
        self.combo.setCursor(QtCore.Qt.PointingHandCursor)
        self.root.addWidget(self.combo)

        # ================= BUTTON =================
        self.continue_btn = QtWidgets.QPushButton("Continue")
        self.root.addWidget(self.continue_btn)

        # ================= STYLE =================
        Dialog.setStyleSheet("""
            QDialog {
                background-color:#121212;
                border-radius:16px;
            }
            QComboBox {
                background-color:#1c1c1c;
                border-radius:12px;
                padding:10px;
                color:#eee;
                font-size:16px;
            }
            QPushButton {
                background-color:#00b4d8;
                color:black;
                font-size:17px;
                font-weight:700;
                border-radius:12px;
                padding:12px;
            }
        """)
