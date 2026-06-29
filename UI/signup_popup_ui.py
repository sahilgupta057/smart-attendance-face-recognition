from PyQt5 import QtWidgets, QtCore, QtGui

class Ui_SignupPopup(object):
    def setupUi(self, Dialog):
        # Professional Window Sizing & Flags
        Dialog.setFixedWidth(480)
        Dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        # Root layout
        self.root_layout = QtWidgets.QVBoxLayout(Dialog)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # ================= TOP BAR =================
        self.top_bar_container = QtWidgets.QWidget()
        self.top_bar = QtWidgets.QHBoxLayout(self.top_bar_container)
        self.top_bar.setContentsMargins(15, 10, 15, 0)
        self.top_bar.addStretch()

        self.close_btn = QtWidgets.QPushButton("✕") # Clean multiplication symbol
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.close_btn.setObjectName("closeButton")
        self.top_bar.addWidget(self.close_btn)
        self.root_layout.addWidget(self.top_bar_container)

        # ================= CONTENT LAYOUT =================
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_layout.setContentsMargins(45, 0, 45, 40)
        self.content_layout.setSpacing(14)

        # Title & Subtitle
        self.title_container = QtWidgets.QVBoxLayout()
        self.title_container.setSpacing(4)
        
        self.title = QtWidgets.QLabel("Create Account")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setObjectName("titleLabel")
        
        self.subtitle = QtWidgets.QLabel("Join our smart attendance system today")
        self.subtitle.setAlignment(QtCore.Qt.AlignCenter)
        self.subtitle.setObjectName("subtitleLabel")
        
        self.title_container.addWidget(self.title)
        self.title_container.addWidget(self.subtitle)
        self.content_layout.addLayout(self.title_container)
        self.content_layout.addSpacing(15)

        # Inputs
        input_font = QtGui.QFont("Inter", 10) # Modern font face
        
        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("Email Address")
        self.mobile_input = QtWidgets.QLineEdit()
        self.mobile_input.setPlaceholderText("Mobile Number")
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_password_input = QtWidgets.QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        # Applying shared styling
        self.input_fields = [self.name_input, self.email_input, self.mobile_input,
                             self.password_input, self.confirm_password_input]
        
        for field in self.input_fields:
            field.setFont(input_font)
            field.setFixedHeight(48) # Professional height
            self.content_layout.addWidget(field)

        # ================= CLASS/SUBJECT SECTION =================
        self.class_subject_label = QtWidgets.QLabel("Assign Classes & Subjects")
        self.class_subject_label.setObjectName("sectionLabel")
        self.content_layout.addSpacing(10)
        self.content_layout.addWidget(self.class_subject_label)
        
        self.class_subject_container = QtWidgets.QVBoxLayout()
        self.class_subject_container.setSpacing(8)
        self.content_layout.addLayout(self.class_subject_container)

        # Add button (styled as a Ghost/Text button)
        self.add_class_subject_btn = QtWidgets.QPushButton("+ Add New Assignment")
        self.add_class_subject_btn.setFixedHeight(30)
        self.add_class_subject_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.add_class_subject_btn.setObjectName("addBtn")
        self.content_layout.addWidget(self.add_class_subject_btn)

        self.content_layout.addSpacing(10)

        # Signup button
        self.signup_btn = QtWidgets.QPushButton("Get Started")
        self.signup_btn.setFixedHeight(50)
        self.signup_btn.setObjectName("primaryButton")
        self.signup_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.content_layout.addWidget(self.signup_btn)

        # Finalizing Layout
        self.root_layout.addLayout(self.content_layout)

        # ================= PRO STYLESHEET =================
        Dialog.setStyleSheet("""
            QDialog { 
                background-color: #0B0E14; 
                border-radius: 20px; 
                border: 1px solid #1F2937; 
            }
            
            /* Inputs */
            QLineEdit { 
                background-color: #161B22; 
                border: 1px solid #30363D; 
                border-radius: 12px;
                padding: 0px 18px; 
                color: #F0F6FC; 
            }
            QLineEdit:focus { 
                border: 1px solid #00D4FF; 
                background-color: #0D1117;
            }
            QLineEdit::placeholder { color: #484F58; }

            /* Primary Button */
            QPushButton#primaryButton { 
                background-color: #00D4FF; 
                color: #050505; 
                font-size: 15px; 
                font-weight: 700; 
                border: none; 
                border-radius: 12px;
            }
            QPushButton#primaryButton:hover { 
                background-color: #33E0FF; 
            }
            QPushButton#primaryButton:pressed { 
                background-color: #00A3C2; 
            }

            /* Section Labels */
            QLabel#titleLabel { 
                color: #F0F6FC; 
                font-size: 26px; 
                font-weight: 800; 
            }
            QLabel#subtitleLabel { 
                color: #8B949E; 
                font-size: 13px; 
            }
            QLabel#sectionLabel { 
                color: #00D4FF; 
                font-size: 12px; 
                font-weight: 700; 
                text-transform: uppercase; 
                letter-spacing: 1px;
            }

            /* Add Button */
            QPushButton#addBtn { 
                background: transparent; 
                color: #58A6FF; 
                font-size: 13px; 
                font-weight: 600; 
                border: none; 
                text-align: left;
            }
            QPushButton#addBtn:hover { color: #79C0FF; }

            /* Close Button */
            QPushButton#closeButton { 
                background: transparent; 
                border: none; 
                color: #484F58; 
                font-size: 16px; 
                font-weight: bold; 
            }
            QPushButton#closeButton:hover { 
                color: #FF4D4D; 
                background-color: rgba(255, 77, 77, 0.1); 
                border-radius: 16px; 
            }
        """)