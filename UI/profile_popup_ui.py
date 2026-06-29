from PyQt5 import QtWidgets, QtCore, QtGui

class Ui_ProfilePopup(object):
    def setupUi(self, Dialog):
        Dialog.resize(480, 620)
        Dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        
        # Root layout
        self.main_layout = QtWidgets.QVBoxLayout(Dialog)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- HEADER SECTION (Profile Picture Area) ---
        self.header_frame = QtWidgets.QFrame()
        self.header_frame.setFixedHeight(220)
        self.header_frame.setStyleSheet("background-color: #222; border-top-left-radius: 12px; border-top-right-radius: 12px;")
        self.header_layout = QtWidgets.QVBoxLayout(self.header_frame)
        
        # Edit Button (Top Right)
        self.top_layout = QtWidgets.QHBoxLayout()
        self.top_layout.addStretch()
        self.edit_btn = QtWidgets.QPushButton("Edit Profile")
        self.edit_btn.setObjectName("editBtn")
        self.edit_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.top_layout.addWidget(self.edit_btn)
        self.header_layout.addLayout(self.top_layout)

        # Profile picture with "Pro" Glow
        self.profile_pic = QtWidgets.QLabel()
        self.profile_pic.setFixedSize(110, 110)
        self.profile_pic.setAlignment(QtCore.Qt.AlignCenter)
        # Using a mask-like stylesheet for a perfect circle
        self.profile_pic.setStyleSheet("""
            QLabel {
                border-radius: 55px; 
                background-color: #333; 
                border: 3px solid #00b4d8;
            }
        """)
        self.header_layout.addWidget(self.profile_pic, alignment=QtCore.Qt.AlignCenter)
        
        self.profile_name_title = QtWidgets.QLabel("User Profile")
        self.profile_name_title.setStyleSheet("color: #00b4d8; font-weight: bold; font-size: 16px; margin-top: 5px;")
        self.header_layout.addWidget(self.profile_name_title, alignment=QtCore.Qt.AlignCenter)
        
        self.main_layout.addWidget(self.header_frame)

        # --- FORM SECTION (Content Area) ---
        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(30, 20, 30, 20)
        self.content_layout.setSpacing(15)

        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setSpacing(15)
        self.form_layout.setLabelAlignment(QtCore.Qt.AlignLeft)

        # Inputs
        self.name_input = QtWidgets.QLineEdit()
        self.email_input = QtWidgets.QLineEdit()
        self.role_input = QtWidgets.QLineEdit()
        self.last_login_input = QtWidgets.QLineEdit()
        self.last_login_input.setReadOnly(True) # Usually read-only for pro apps

        # Add rows with modern spacing
        self.form_layout.addRow("Full Name", self.name_input)
        self.form_layout.addRow("Email Address", self.email_input)
        self.form_layout.addRow("Assigned Role", self.role_input)
        self.form_layout.addRow("Last Login", self.last_login_input)

        self.content_layout.addLayout(self.form_layout)
        self.content_layout.addStretch()

        # --- FOOTER BUTTONS ---
        self.btn_layout = QtWidgets.QHBoxLayout()
        self.btn_layout.setSpacing(10)
        
        self.save_btn = QtWidgets.QPushButton("Save Changes")
        self.save_btn.setFixedHeight(40)
        self.save_btn.setCursor(QtCore.Qt.PointingHandCursor)
        
        self.delete_btn = QtWidgets.QPushButton("Delete")
        self.delete_btn.setObjectName("deleteBtn")
        self.delete_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.delete_btn.setFixedWidth(100)
        self.delete_btn.setFixedHeight(40)
        
        self.ok_btn = QtWidgets.QPushButton("Close")
        self.ok_btn.setFixedWidth(100)
        self.ok_btn.setFixedHeight(40)
        self.ok_btn.setCursor(QtCore.Qt.PointingHandCursor)

        self.btn_layout.addWidget(self.save_btn, 1) # Give save button more weight
        self.btn_layout.addWidget(self.delete_btn)
        self.btn_layout.addWidget(self.ok_btn)

        self.content_layout.addLayout(self.btn_layout)
        self.main_layout.addWidget(self.content_widget)

        # --- STYLE SHEET ---
        Dialog.setStyleSheet("""
            QDialog { 
                background-color: #1a1a1a; 
                border: 1px solid #333; 
                border-radius: 12px; 
            }
            QLabel { 
                color: #888; 
                font-size: 12px; 
                font-weight: bold; 
                text-transform: uppercase;
            }
            QLineEdit { 
                background-color: #252525; 
                border: 1px solid #333; 
                border-radius: 6px; 
                padding: 10px; 
                color: #EEE; 
                font-size: 13px; 
            }
            QLineEdit:focus { 
                border: 1px solid #00b4d8; 
                background-color: #2a2a2a;
            }
            QPushButton { 
                background-color: #333; 
                border: none; 
                border-radius: 6px; 
                color: #fff; 
                font-weight: bold; 
                font-size: 12px; 
            }
            QPushButton:hover { 
                background-color: #444; 
            }
            QPushButton#editBtn { 
                background-color: transparent; 
                color: #00b4d8; 
                font-size: 11px; 
                text-decoration: none;
            }
            QPushButton#editBtn:hover { 
                color: #90e0ef; 
            }
            QPushButton#deleteBtn { 
                background-color: transparent; 
                border: 1px solid #e53935; 
                color: #e53935; 
            }
            QPushButton#deleteBtn:hover { 
                background-color: #e53935; 
                color: white; 
            }
            /* Styling for the Primary Action */
            QPushButton:pressed { 
                background-color: #00b4d8; 
            }
            QPushButton {
                background-color: #00b4d8;
                color: #000;
            }
            QPushButton#ok_btn, QPushButton#deleteBtn {
                background-color: #333;
                color: #fff;
            }
        """)