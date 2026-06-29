from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon


class Ui_HelpPopup(object):

    # =================== star rating system ====================

    def set_rating(self, rating):
        emojis = {
            1: "😞 Confused / Not happy",
            2: "😐 Neutral / Meh",
            3: "🙂 Slightly happy / Okay",
            4: "😃 Happy / Good",
            5: "🤩 Very happy / Loved it"
        }
        for i, star in enumerate(self.stars):
            star.setText("⭐" if i < rating else "☆")
        self.emoji_label.setText(emojis.get(rating, "🙂"))

    # =====================================================
    # 🔧 ACCORDION CARD FACTORY
    # =====================================================
    def _make_accordion_card(self, title, body_text, accent="#1f4e79"):
        """
        Returns a QFrame that acts as a collapsible accordion card.
        Clicking the header button toggles the body label.
        """
        card = QtWidgets.QFrame()
        card.setObjectName("accordionCard")
        card.setStyleSheet(f"""
            QFrame#accordionCard {{
                background-color: #111;
                border: 1px solid #2a2a2a;
                border-left: 3px solid {accent};
                border-radius: 8px;
            }}
        """)
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # ── Header button ──────────────────────────────────────────────────
        header = QtWidgets.QPushButton("▶  " + title)
        header.setCheckable(True)
        header.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #E0E0E0;
                font-size: 13px;
                font-weight: bold;
                text-align: left;
                padding: 10px 14px;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: #1a1a1a;
            }
            QPushButton:checked {
                color: #7ec8e3;
            }
        """)

        # ── Body label ─────────────────────────────────────────────────────
        body = QtWidgets.QLabel(body_text)
        body.setWordWrap(True)
        body.setStyleSheet("""
            QLabel {
                color: #AAAAAA;
                font-size: 12px;
                padding: 0px 16px 12px 28px;
                line-height: 1.6;
            }
        """)
        body.hide()

        def toggle(checked, h=header, b=body):
            b.setVisible(checked)
            h.setText(("▼  " if checked else "▶  ") + title)

        header.toggled.connect(toggle)

        card_layout.addWidget(header)
        card_layout.addWidget(body)
        return card

    def setupUi(self, Dialog):
        Dialog.resize(780, 520)
        Dialog.setMinimumSize(720, 500)

        # ================= ROOT =================
        self.layout = QtWidgets.QVBoxLayout(Dialog)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(12)

        # ================= TITLE =================
        self.title = QtWidgets.QLabel("❓ Help & Support")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setObjectName("title")
        self.layout.addWidget(self.title)

        # ================= SEARCH =================
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("Search your issue...")
        self.layout.addWidget(self.search)

        # ================= MAIN SPLIT LAYOUT =================
        self.split_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.split_layout)

        # ================= LEFT MENU =================
        self.menu = QtWidgets.QListWidget()
        self.menu.setFixedWidth(150)
        self.menu.addItems([
            "Quick Help",
            "Troubleshooting",
            "Contact",
            "Feedback",
            "System Info"
        ])
        self.split_layout.addWidget(self.menu)

        # ================= RIGHT STACK =================
        self.stack = QtWidgets.QStackedWidget()
        self.split_layout.addWidget(self.stack)

        # =====================================================
        # 🧩 TAB 1 — QUICK HELP / FAQ  (accordion cards)
        # =====================================================
        self.tab_help = QtWidgets.QWidget()
        self.tab_help_layout = QtWidgets.QVBoxLayout(self.tab_help)
        self.tab_help_layout.setContentsMargins(4, 4, 4, 4)
        self.tab_help_layout.setSpacing(6)

        self.faq_scroll = QtWidgets.QScrollArea()
        self.faq_scroll.setWidgetResizable(True)
        self.faq_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.faq_scroll.setStyleSheet("QScrollArea { background: transparent; }")
        self.faq_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.faq_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.faq_inner = QtWidgets.QWidget()
        self.faq_inner.setStyleSheet("background: transparent;")
        self.faq_inner_layout = QtWidgets.QVBoxLayout(self.faq_inner)
        self.faq_inner_layout.setContentsMargins(2, 2, 2, 2)
        self.faq_inner_layout.setSpacing(6)

        faqs = [
            ("📋 How do I mark attendance?",
             "Go to the Face Recognition page from the left menu.\n"
             "Click Start Camera — the system will automatically detect\n"
             "and mark attendance for recognized students in real time."),

            ("💡 Face not detected — what should I do?",
             "• Make sure the room has sufficient lighting.\n"
             "• Remove masks, glasses, or anything covering your face.\n"
             "• Position your face directly in front of the camera.\n"
             "• Ensure the camera lens is clean and unobstructed."),

            ("🧑‍🎓 How do I add or update a student's face?",
             "Go to Student Management → click Add Image.\n"
             "A camera popup will open — capture a clear front-facing photo.\n"
             "The new image will be saved and used for future recognition."),

            ("📊 How do I view attendance records?",
             "Click Attendance Records in the left menu to see the full table.\n"
             "Use the Reports tab to generate filtered reports by date or student."),

            ("✏️ How do I correct a wrong attendance entry?",
             "Go to Attendance Records, locate the entry and edit it manually.\n"
             "If you lack permission, raise a request via the Contact tab here."),

            ("🔔 Will students get notified?",
             "Yes — when attendance is marked, an automatic email is sent\n"
             "to the student's registered email address."),

            ("📤 Can I export attendance data?",
             "Yes — go to the Reports tab and use the Export button\n"
             "to download records as an Excel (.xlsx) file."),
        ]

        self.faq_cards = []
        for question, answer in faqs:
            card = self._make_accordion_card(question, answer, accent="#1f4e79")
            self.faq_inner_layout.addWidget(card)
            self.faq_cards.append((question + " " + answer, card))

        self.faq_inner_layout.addStretch()
        self.faq_scroll.setWidget(self.faq_inner)
        self.tab_help_layout.addWidget(self.faq_scroll)
        self.stack.addWidget(self.tab_help)

        # =====================================================
        # 🧩 TAB 2 — TROUBLESHOOTING  (accordion cards)
        # =====================================================
        self.tab_trouble = QtWidgets.QWidget()
        self.trouble_layout = QtWidgets.QVBoxLayout(self.tab_trouble)
        self.trouble_layout.setContentsMargins(4, 4, 4, 4)
        self.trouble_layout.setSpacing(6)

        self.trouble_scroll = QtWidgets.QScrollArea()
        self.trouble_scroll.setWidgetResizable(True)
        self.trouble_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.trouble_scroll.setStyleSheet("QScrollArea { background: transparent; }")
        self.trouble_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.trouble_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.trouble_inner = QtWidgets.QWidget()
        self.trouble_inner.setStyleSheet("background: transparent;")
        self.trouble_inner_layout = QtWidgets.QVBoxLayout(self.trouble_inner)
        self.trouble_inner_layout.setContentsMargins(2, 2, 2, 2)
        self.trouble_inner_layout.setSpacing(6)

        issues = [
            ("🚫 Face not recognized even in good lighting",
             "Step 1 — Re-register the student's face via Student Management.\n"
             "Step 2 — Capture the photo in the same lighting as the classroom.\n"
             "Step 3 — Ensure no accessories (hat, scarf) block the face.\n"
             "Step 4 — Restart the camera from the Face Recognition page."),

            ("📷 Camera not opening or showing a black screen",
             "Step 1 — Check that no other app is using the camera.\n"
             "Step 2 — Go to system settings and grant camera permission.\n"
             "Step 3 — Try disconnecting and reconnecting an external webcam.\n"
             "Step 4 — Restart the application completely."),

            ("🌐 Network / email sending error",
             "Step 1 — Verify your internet connection is active.\n"
             "Step 2 — Confirm APP_EMAIL and APP_EMAIL_PASS env vars are set.\n"
             "Step 3 — Make sure Less Secure App Access is enabled in Gmail,\n"
             "          or use a Gmail App Password instead of your main password."),

            ("⏱️ Attendance marked but not showing in table",
             "Step 1 — Click the Refresh button on the Attendance Records page.\n"
             "Step 2 — Verify today's date matches the records filter.\n"
             "Step 3 — Check the database file is not locked by another process."),

            ("🔐 Login fails — password not accepted",
             "Step 1 — Double-check CAPS LOCK is off.\n"
             "Step 2 — Use the Forgot Password option to reset via OTP.\n"
             "Step 3 — If the problem persists, contact your system admin."),

            ("📁 Student data missing after restart",
             "Step 1 — Confirm the /data folder was not moved or deleted.\n"
             "Step 2 — Check that you are logged in with the correct account.\n"
             "Step 3 — Re-import student records if a backup is available."),

            ("🐢 Application running slowly",
             "Step 1 — Close other heavy applications running in the background.\n"
             "Step 2 — Reduce camera resolution in Settings.\n"
             "Step 3 — Ensure at least 4 GB RAM is free before starting."),
        ]

        self.trouble_cards = []
        for title, steps in issues:
            card = self._make_accordion_card(title, steps, accent="#7b2d00")
            self.trouble_inner_layout.addWidget(card)
            self.trouble_cards.append((title + " " + steps, card))

        self.trouble_inner_layout.addStretch()
        self.trouble_scroll.setWidget(self.trouble_inner)
        self.trouble_layout.addWidget(self.trouble_scroll)
        self.stack.addWidget(self.tab_trouble)

        # =====================================================
        # 🧩 TAB 3 — CONTACT SUPPORT  (Submit button at bottom-right)
        # =====================================================
        self.tab_contact = QtWidgets.QWidget()
        self.contact_outer = QtWidgets.QVBoxLayout(self.tab_contact)
        self.contact_outer.setContentsMargins(0, 0, 0, 0)
        self.contact_outer.setSpacing(8)

        # Form rows
        self.contact_form = QtWidgets.QFormLayout()
        self.issue_type = QtWidgets.QComboBox()
        self.issue_type.addItems(["Recognition", "Attendance", "Account", "Device"])
        self.priority = QtWidgets.QComboBox()
        self.priority.addItems(["Low", "Medium", "High"])
        self.message = QtWidgets.QTextEdit()

        self.contact_form.addRow("Issue Type:", self.issue_type)
        self.contact_form.addRow("Priority:",   self.priority)
        self.contact_form.addRow("Message:",    self.message)
        self.contact_outer.addLayout(self.contact_form)

        # Submit at bottom-right
        self.contact_outer.addStretch()
        self.contact_btn_row = QtWidgets.QHBoxLayout()
        self.contact_btn_row.addStretch()
        self.contact_submit_btn = QtWidgets.QPushButton("Submit")
        self.contact_submit_btn.setObjectName("submitBtn")
        self.contact_btn_row.addWidget(self.contact_submit_btn)
        self.contact_outer.addLayout(self.contact_btn_row)

        self.stack.addWidget(self.tab_contact)

        # =====================================================
        # 🧩 TAB 4 — FEEDBACK  (Submit button at bottom-right)
        # =====================================================
        self.tab_feedback = QtWidgets.QWidget()
        self.feedback_layout = QtWidgets.QVBoxLayout(self.tab_feedback)

        self.feedback_layout.addWidget(QtWidgets.QLabel("⭐ Rate your experience"))

        # Star row
        self.star_layout = QtWidgets.QHBoxLayout()
        self.stars = []
        for i in range(5):
            btn = QtWidgets.QPushButton("☆")
            btn.setFixedSize(40, 40)
            btn.setObjectName("star")
            btn.setStyleSheet("border: none; font-size: 28px; color: white;")
            btn.clicked.connect(lambda _, x=i: self.set_rating(x + 1))
            self.stars.append(btn)
            self.star_layout.addWidget(btn)
        self.star_layout.addStretch()
        self.feedback_layout.addLayout(self.star_layout)

        # Emoji label
        self.emoji_label = QtWidgets.QLabel("🙂")
        self.emoji_label.setAlignment(QtCore.Qt.AlignCenter)
        self.emoji_label.setStyleSheet("font-size: 28px;")
        self.feedback_layout.addWidget(self.emoji_label)

        # Suggestion box
        self.feedback_layout.addWidget(QtWidgets.QLabel("💡 Suggest a feature"))
        self.suggestion = QtWidgets.QTextEdit()
        self.feedback_layout.addWidget(self.suggestion)

        # Submit at bottom-right
        self.feedback_layout.addStretch()
        self.feedback_btn_row = QtWidgets.QHBoxLayout()
        self.feedback_btn_row.addStretch()
        self.feedback_submit_btn = QtWidgets.QPushButton("Submit")
        self.feedback_submit_btn.setObjectName("submitBtn")
        self.feedback_btn_row.addWidget(self.feedback_submit_btn)
        self.feedback_layout.addLayout(self.feedback_btn_row)

        self.stack.addWidget(self.tab_feedback)

        # =====================================================
        # 🧩 TAB 5 — SYSTEM INFO
        # =====================================================
        self.tab_system = QtWidgets.QWidget()
        self.system_layout = QtWidgets.QVBoxLayout(self.tab_system)

        self.system_layout.addWidget(QtWidgets.QLabel("🟢 Server Status: Operational"))
        self.system_layout.addWidget(QtWidgets.QLabel("🧠 AI Model Version: v1.2"))
        self.system_layout.addWidget(QtWidgets.QLabel("📅 Last Sync: Today"))
        self.system_layout.addWidget(QtWidgets.QLabel("💻 Device: Desktop"))

        self.system_layout.addStretch()
        self.stack.addWidget(self.tab_system)

        # ================= BOTTOM BAR (Close only) =================
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addStretch()

        self.close_btn = QtWidgets.QPushButton("Close")
        self.button_layout.addWidget(self.close_btn)

        self.layout.addLayout(self.button_layout)

        # ================= WIRING =================
        self.menu.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.menu.setCurrentRow(0)

        # Wire search bar to filter Quick Help + Troubleshooting cards
        self.search.textChanged.connect(self._filter_cards)

        # ================= STYLE =================
        Dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                border: 2px solid #333;
                border-radius: 12px;
            }
            QLabel {
                color: #EEE;
                font-size: 14px;
            }
            #title {
                font-size: 18px;
                font-weight: bold;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #000;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 6px;
                color: #fff;
            }
            QPushButton {
                background-color: #000;
                border: 1px solid #333;
                border-radius: 10px;
                padding: 8px 16px;
                color: #fff;
            }
            QPushButton:hover {
                background-color: #1a1a1a;
            }
            QPushButton#submitBtn {
                background-color: #1f4e79;
                border: 1px solid #2a6fa8;
                color: #fff;
                font-weight: bold;
                min-width: 90px;
            }
            QPushButton#submitBtn:hover {
                background-color: #2a6fa8;
            }
            QPushButton#star {
                background-color: transparent;
                border: none;
                padding: 0;
            }
            QPushButton#star:hover {
                color: #ffcc00;
            }
            QListWidget {
                background-color: #111;
                border: 1px solid #333;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 10px;
                color: #ccc;
            }
            QListWidget::item:selected {
                background-color: #1f4e79;
                color: white;
            }
        """)

    def _filter_cards(self, text):
        """Show/hide accordion cards in both tabs based on search text."""
        text = text.strip().lower()

        for search_str, card in getattr(self, "faq_cards", []):
            card.setVisible(not text or text in search_str.lower())

        for search_str, card in getattr(self, "trouble_cards", []):
            card.setVisible(not text or text in search_str.lower())

        # Auto-switch to the relevant tab if text is typed
        if text:
            faq_hits     = any(text in s.lower() for s, _ in getattr(self, "faq_cards", []))
            trouble_hits = any(text in s.lower() for s, _ in getattr(self, "trouble_cards", []))
            current = self.menu.currentRow()
            if trouble_hits and not faq_hits and current != 1:
                self.menu.setCurrentRow(1)
            elif faq_hits and current != 0:
                self.menu.setCurrentRow(0)

