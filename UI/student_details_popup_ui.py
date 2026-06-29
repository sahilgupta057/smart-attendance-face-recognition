from PyQt5 import QtWidgets, QtCore, QtGui

class Ui_StudentDetailsPopup(object):
    def setupUi(self, Dialog):
        Dialog.resize(800, 550) # Slightly wider for better table proportions
        Dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        Dialog.setModal(True)
        
        # Professional Dark Theme Base
        Dialog.setStyleSheet("""
            QDialog {
                background-color: #121212; 
                border: 1px solid #333;
                border-radius: 15px;
            }
            QWidget {
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            }
        """)

        # ================= MAIN LAYOUT =================
        self.main_layout = QtWidgets.QHBoxLayout(Dialog)
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        self.main_layout.setSpacing(25)

        # ================= LEFT SIDE (Profile & Info) =================
        self.left_frame = QtWidgets.QFrame()
        self.left_layout = QtWidgets.QVBoxLayout(self.left_frame)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(20)

        # --- CIRCULAR IMAGE SECTION ---
        # Container for the image to allow for the camera icon overlay
        self.image_container = QtWidgets.QWidget()
        self.image_container.setFixedSize(180, 180)
        self.image_container_layout = QtWidgets.QVBoxLayout(self.image_container)
        self.image_container_layout.setContentsMargins(0, 0, 0, 0)

        self.image_label = QtWidgets.QLabel(self.image_container)
        self.image_label.setFixedSize(180, 180)
        self.image_label.setCursor(QtCore.Qt.PointingHandCursor)
        self.image_label.setToolTip("Click to upload student photo")
        # Pro-level circular styling with border
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                border: 3px solid #00b4d8;
                border-radius: 90px;
            }
            QLabel:hover {
                border: 3px solid #90e0ef;
                background-color: #333;
            }
        """)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Camera Icon Overlay (Visual hint for the user)
        self.camera_icon_label = QtWidgets.QLabel(self.image_label)
        self.camera_icon_label.setText("📷") # You can replace with a QPixmap icon later
        self.camera_icon_label.setFixedSize(40, 40)
        self.camera_icon_label.move(130, 130) # Bottom right of the circle
        self.camera_icon_label.setStyleSheet("""
            background-color: #00b4d8;
            color: white;
            border-radius: 20px;
            font-size: 18px;
            border: 2px solid #121212;
        """)
        self.camera_icon_label.setAlignment(QtCore.Qt.AlignCenter)

        self.left_layout.addWidget(self.image_container, alignment=QtCore.Qt.AlignCenter)

        # --- INFO CARD ---
        self.info_frame = QtWidgets.QFrame()
        self.info_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 12px;
            }
        """)
        self.info_layout = QtWidgets.QVBoxLayout(self.info_frame)
        self.info_layout.setContentsMargins(20, 20, 20, 20)
        self.info_layout.setSpacing(12)

        # Add your dynamic info labels here as you usually do in backend
        self.left_layout.addWidget(self.info_frame)

        self.close_btn = QtWidgets.QPushButton("✕ Close")
        self.close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.close_btn.setFixedHeight(45)
        self.close_btn.setFixedWidth(200)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid #ef4444;
                border-radius: 10px;
                color: #ef4444;
                font-weight: bold;
                font-size: 14px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #ef4444;
                color: white;
            }
            QPushButton:pressed {
                background-color: #991b1b;
            }
        """)
        self.left_layout.addWidget(self.close_btn, alignment=QtCore.Qt.AlignCenter)

        self.main_layout.addWidget(self.left_frame, 1)

        # ================= RIGHT SIDE (Table) =================
        self.right_frame = QtWidgets.QFrame()
        self.right_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 12px;
            }
        """)
        self.right_layout = QtWidgets.QVBoxLayout(self.right_frame)
        self.right_layout.setContentsMargins(15, 15, 15, 15)
        self.right_layout.setSpacing(15)

        self.att_label = QtWidgets.QLabel("Attendance History")
        self.att_label.setStyleSheet("""
            color: #00b4d8; 
            font-size: 20px; 
            font-weight: bold;
            letter-spacing: 1px;
        """)
        self.right_layout.addWidget(self.att_label, alignment=QtCore.Qt.AlignLeft)

        self.att_table = QtWidgets.QTableWidget()
        self.att_table.setColumnCount(3)
        self.att_table.setHorizontalHeaderLabels(["Date", "Check-in", "Status"])
        self.att_table.setShowGrid(False) # Modern look
        self.att_table.setFocusPolicy(QtCore.Qt.NoFocus)
        self.att_table.setAlternatingRowColors(True)
        
        self.att_table.horizontalHeader().setStretchLastSection(True)
        self.att_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.att_table.verticalHeader().setVisible(False)
        
        # Professional Table Styling
        self.att_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #252525;
                color: #ddd;
                border: none;
                font-size: 13px;
                selection-background-color: #00b4d8;
                gridline-color: transparent;
            }
            QHeaderView::section {
                background-color: #1e1e1e;
                color: #888;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #333;
                font-weight: bold;
                text-transform: uppercase;
                font-size: 11px;
            }
            QScrollBar:vertical {
                border: none;
                background: #1e1e1e;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #444;
                min-height: 20px;
                border-radius: 4px;
            }
        """)

        self.right_layout.addWidget(self.att_table)
        self.main_layout.addWidget(self.right_frame, 2) # Right side gets more space (ratio 1:2)