from PyQt5 import QtWidgets, QtCore, QtGui

class Ui_MoreMenuPopup(object):
    def setupUi(self, Dialog):
        # Adjusted for a sleek, vertical side-menu feel
        Dialog.setFixedSize(400, 520)
        Dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        
        # ROOT LAYOUT
        self.layout = QtWidgets.QVBoxLayout(Dialog)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # --- HEADER ---
        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setFixedHeight(70)
        self.header_widget.setStyleSheet("background-color: #161B22; border-top-left-radius: 12px; border-top-right-radius: 12px;")
        self.header_layout = QtWidgets.QHBoxLayout(self.header_widget)
        
        self.title = QtWidgets.QLabel("System Operations")
        self.title.setStyleSheet("color: #00D4FF; font-size: 18px; font-weight: 700; letter-spacing: 0.5px;")
        self.header_layout.addWidget(self.title)
        self.header_layout.addStretch()
        
        # Small close X in header
        self.close_btn = QtWidgets.QPushButton("✕")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.close_btn.setObjectName("headerClose")
        self.header_layout.addWidget(self.close_btn)
        
        self.layout.addWidget(self.header_widget)

        # --- CONTENT AREA ---
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background-color: #0B0E14;")

        self.scroll_content = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.scroll_content)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(12)

        # FEATURES / OPTIONS
        # We use a helper to maintain the professional look
        self.add_menu_option("📦 Cloud Backup", "Sync local data to secure cloud storage", self.content_layout)
        self.add_menu_option("📈 Analytics Export", "Download detailed PDF/CSV reports", self.content_layout)
        self.add_menu_option("👥 User Access", "Manage roles and system permissions", self.content_layout)
        self.add_menu_option("⚙️ Preferences", "Configure theme and system behavior", self.content_layout)
        self.add_menu_option("🔄 System Update", "Check for the latest software patches", self.content_layout)

        self.content_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        # --- STYLE SHEET ---
        Dialog.setStyleSheet("""
            QDialog { 
                background-color: #0B0E14; 
                border: 1px solid #30363D; 
                border-radius: 12px; 
            }
            
            /* Professional Menu Buttons */
            QPushButton#menuOption {
                background-color: #161B22;
                border: 1px solid #30363D;
                border-radius: 10px;
                color: #F0F6FC;
                text-align: left;
                padding: 15px;
            }
            QPushButton#menuOption:hover {
                background-color: #1C2128;
                border: 1px solid #00D4FF;
            }
            
            /* Sub-text labeling */
            QLabel#descLabel {
                color: #8B949E;
                font-size: 11px;
                background: transparent;
            }
            
            QPushButton#headerClose {
                background: transparent;
                border: none;
                color: #8B949E;
                font-size: 16px;
            }
            QPushButton#headerClose:hover {
                color: #FF4D4D;
            }
        """)

    def add_menu_option(self, title, description, layout):
        """Helper to create professional double-layered menu items"""
        btn = QtWidgets.QPushButton()
        btn.setObjectName("menuOption")
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        btn.setFixedHeight(70)
        
        btn_layout = QtWidgets.QVBoxLayout(btn)
        btn_layout.setContentsMargins(10, 5, 10, 5)
        btn_layout.setSpacing(2)
        
        t_label = QtWidgets.QLabel(title)
        t_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #eee; border:none;")
        
        d_label = QtWidgets.QLabel(description)
        d_label.setObjectName("descLabel")
        d_label.setStyleSheet("border:none;")
        
        btn_layout.addWidget(t_label)
        btn_layout.addWidget(d_label)
        
        layout.addWidget(btn)
        # You can connect your backend logic to 'btn.clicked' here