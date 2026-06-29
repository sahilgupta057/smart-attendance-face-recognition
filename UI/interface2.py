from PyQt5 import QtCore, QtGui, QtWidgets
from Custom_Widgets.Widgets import *
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QPropertyAnimation, QSize, QEasingCurve
import os as _os


class Ui_MainWindow(object):

        def tinted_icon(self, path, color):
                pixmap = QtGui.QPixmap(path)
                painter = QtGui.QPainter(pixmap)
                painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceIn)
                painter.fillRect(pixmap.rect(), color)
                painter.end()
                return QtGui.QIcon(pixmap)
        
        def apply_theme_icons(self):
                if self.is_dark_mode:
                        color = QtGui.QColor("white")
                else:
                        color = QtGui.QColor("black")

                # sidebar buttons
                self.home.setIcon(self.tinted_icon(":/icon/icon/home.svg", color))
                self.facerecognition.setIcon(self.tinted_icon(":/icon/icon/face-recognition.svg", color))
                self.studentmanagement.setIcon(self.tinted_icon(":/icon/icon/users.svg", color))
                self.attendancerecords.setIcon(self.tinted_icon(":/icon/icon/server.svg", color))
                self.reports.setIcon(self.tinted_icon(":/icon/icon/printer.svg", color))
                self.chatbot.setIcon(self.tinted_icon(":/icon/icon/message-circle.svg", color))
                self.setting.setIcon(self.tinted_icon(":/icon/icon/settings.svg", color))
                self.logout.setIcon(self.tinted_icon(":/icon/icon/log-out.svg", color))
                self.help.setIcon(self.tinted_icon(":/icon/icon/help-circle.svg", color))
                self.information.setIcon(self.tinted_icon(":/icon/icon/info.svg", color))

                # header icons
                self.moreMenu.setIcon(self.tinted_icon(":/icon/icon/more-horizontal.svg", color))
                self.profile.setIcon(self.tinted_icon(":/icon/icon/user.svg", color))

        def create_card(self, title, subtitle, icon_path):
                card = QFrame()
                card.setStyleSheet("""
                        QFrame {
                        background-color: #FFFFFF;
                        border-radius: 16px;
                        border: 1px solid #E5E7EB;
                        }
                        QFrame:hover {
                        background-color: #F3F4F6;
                        border: 1px solid #2563EB;
                        }
                """)
                layout = QVBoxLayout(card)
                layout.setContentsMargins(20, 20, 20, 20)
                layout.setSpacing(10)

                shadow = QGraphicsDropShadowEffect()
                shadow.setBlurRadius(15)
                shadow.setXOffset(0)
                shadow.setYOffset(5)
                shadow.setColor(QColor(0, 0, 0, 80))
                card.setGraphicsEffect(shadow)

                icon = QLabel()
                icon.setPixmap(QtGui.QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                icon.setAlignment(Qt.AlignCenter)

                title_lbl = QLabel(title)
                title_lbl.setAlignment(Qt.AlignCenter)
                title_lbl.setStyleSheet("font-size: 18px; font-weight: 600; color: #111827;")

                subtitle_lbl = QLabel(subtitle)
                subtitle_lbl.setAlignment(Qt.AlignCenter)
                subtitle_lbl.setStyleSheet("font-size: 13px; color: #6B7280;")

                layout.addWidget(icon)
                layout.addWidget(title_lbl)
                layout.addWidget(subtitle_lbl)

                return card 

        def setupUi(self, MainWindow):
                MainWindow.setObjectName("MainWindow")
                self.is_dark_mode = False
                MainWindow.resize(1280, 720)
                MainWindow.setMinimumSize(QtCore.QSize(900, 600))
                MainWindow.setStyleSheet("*{\n"
        "   border-color: #E0E0E0;\n"
        "  \n"
        "   border:none;\n"
        "   background:none;\n"
        "   padding: 0;\n"
        "   margin: 0;\n"
        "   color:black;\n"
        "}\n"
        "\n"
        "#leftMenuSubContainer QPushButton{\n"
        "    padding: 5px 10px;\n"
        "    border: none;\n"
        "    text-align: left;\n"
        "     border-top-left-radius: 10px;\n"
        "      border-bottom-left-radius: 10px;\n"
        "    \n"
        "}\n"
        "\n"
        "#leftMenuSubContainer{\n"
        "  background-color: #F2F2F2;\n"
        " \n"
        "}\n"
        "\n"
        "QPushButton:hover{\n"
        "  background-color:#FFFCFB;\n"
        "   color: #1976D2;\n"
        "  \n"
        "}\n"
        "\n"
        "#centerMenuSubContainer{\n"
        "  \n"
        "  background-color:#F5F5F0;\n"
        "}\n"
        "\n"
        "#frame_8{\n"
        "  border-radius: 20px;\n"
        "}\n"
        "\n"
        "#frame_4{\n"
        "  border-radius: 20px;\n"
        "}\n"
        "")
                MainWindow.setIconSize(QtCore.QSize(30, 30))
                self.centralwidget = QtWidgets.QWidget(MainWindow)
                self.centralwidget.setStyleSheet("")
                self.centralwidget.setObjectName("centralwidget")
                self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
                self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
                self.horizontalLayout.setSpacing(0)
                self.horizontalLayout.setObjectName("horizontalLayout")
                self.leftMenuContainer = QCustomSlideMenu(self.centralwidget)
                self.leftMenuContainer.setMaximumSize(QtCore.QSize(65, 16777215))
                self.leftMenuContainer.setObjectName("leftMenuContainer")
                self.verticalLayout = QtWidgets.QVBoxLayout(self.leftMenuContainer)
                self.verticalLayout.setContentsMargins(0, 0, 0, 0)
                self.verticalLayout.setSpacing(0)
                self.verticalLayout.setObjectName("verticalLayout")
                self.leftMenuSubContainer = QtWidgets.QWidget(self.leftMenuContainer)
                self.leftMenuSubContainer.setObjectName("leftMenuSubContainer")
                self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.leftMenuSubContainer) 
                self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
                self.verticalLayout_2.setSpacing(0)
                self.verticalLayout_2.setObjectName("verticalLayout_2")
                self.frame = QtWidgets.QFrame(self.leftMenuSubContainer)
                self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
                self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
                self.frame.setObjectName("frame")
                self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame)
                self.verticalLayout_3.setContentsMargins(10, 6, 0, 10)
                self.verticalLayout_3.setSpacing(0)
                self.verticalLayout_3.setObjectName("verticalLayout_3")
                
                self.menu = QtWidgets.QPushButton(self.frame)
                self.menu.setLayoutDirection(QtCore.Qt.LeftToRight)
                self.menu.setStyleSheet("")
                self.menu.setText("")
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(":/icon/icon/align-justify.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.menu.setIcon(icon)
                self.menu.setIconSize(QtCore.QSize(40, 40))
                self.menu.setObjectName("menu")
                self.verticalLayout_3.addWidget(self.menu)
                self.verticalLayout_2.addWidget(self.frame)

                self.frame_2 = QtWidgets.QFrame(self.leftMenuSubContainer)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
                self.frame_2.setSizePolicy(sizePolicy)
                font = QtGui.QFont()
                font.setPointSize(10)
                self.frame_2.setFont(font)
                self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
                self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
                self.frame_2.setObjectName("frame_2")

                self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frame_2)
                self.verticalLayout_4.setContentsMargins(10, 0, 0, 100)
                self.verticalLayout_4.setSpacing(0)
                self.verticalLayout_4.setObjectName("verticalLayout_4")

                # ── Home ──────────────────────────────────────────────────────
                self.home = QtWidgets.QPushButton(self.frame_2)
                font = QtGui.QFont()
                font.setPointSize(10)
                font.setBold(False)
                font.setWeight(50)
                self.home.setFont(font)
                self.home.setStyleSheet("background-color:#FFFCFB")
                icon1 = QtGui.QIcon()
                icon1.addPixmap(QtGui.QPixmap(":/icon/icon/home.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                self.home.setIcon(icon1)
                self.home.setIconSize(QtCore.QSize(30, 30))
                self.home.setObjectName("home")
                self.verticalLayout_4.addWidget(self.home)

                # ── Face Recognition ──────────────────────────────────────────
                self.facerecognition = QtWidgets.QPushButton(self.frame_2)
                font = QtGui.QFont()
                font.setPointSize(10)
                self.facerecognition.setFont(font)
                icon2 = QtGui.QIcon()
                icon2.addPixmap(QtGui.QPixmap(":/icon/icon/face-recognition.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.facerecognition.setIcon(icon2)
                self.facerecognition.setIconSize(QtCore.QSize(35, 35))
                self.facerecognition.setObjectName("facerecognition")
                self.verticalLayout_4.addWidget(self.facerecognition)

                # ── Student Management ────────────────────────────────────────
                self.studentmanagement = QtWidgets.QPushButton(self.frame_2)
                font = QtGui.QFont()
                font.setPointSize(10)
                self.studentmanagement.setFont(font)
                icon3 = QtGui.QIcon()
                icon3.addPixmap(QtGui.QPixmap(":/icon/icon/users.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.studentmanagement.setIcon(icon3)
                self.studentmanagement.setIconSize(QtCore.QSize(30, 30))
                self.studentmanagement.setObjectName("studentmanagement")
                self.verticalLayout_4.addWidget(self.studentmanagement)

                # ── Attendance Records ────────────────────────────────────────
                self.attendancerecords = QtWidgets.QPushButton(self.frame_2)
                font = QtGui.QFont()
                font.setPointSize(10)
                self.attendancerecords.setFont(font)
                icon4 = QtGui.QIcon()
                icon4.addPixmap(QtGui.QPixmap(":/icon/icon/server.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.attendancerecords.setIcon(icon4)
                self.attendancerecords.setIconSize(QtCore.QSize(30, 30))
                self.attendancerecords.setObjectName("attendancerecords")
                self.verticalLayout_4.addWidget(self.attendancerecords)

                # ── Reports ───────────────────────────────────────────────────
                self.reports = QtWidgets.QPushButton(self.frame_2)
                font = QtGui.QFont()
                font.setPointSize(10)
                self.reports.setFont(font)
                icon5 = QtGui.QIcon()
                icon5.addPixmap(QtGui.QPixmap(":/icon/icon/printer.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.reports.setIcon(icon5)
                self.reports.setIconSize(QtCore.QSize(30, 30))
                self.reports.setObjectName("reports")
                self.verticalLayout_4.addWidget(self.reports)

                # ── Chatbot (NEW) ─────────────────────────────────────────────
                self.chatbot = QtWidgets.QPushButton(self.frame_2)
                font = QtGui.QFont()
                font.setPointSize(10)
                self.chatbot.setFont(font)
                icon_chat = QtGui.QIcon()
                icon_chat.addPixmap(QtGui.QPixmap(":/icon/icon/message-circle.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.chatbot.setIcon(icon_chat)
                self.chatbot.setIconSize(QtCore.QSize(30, 30))
                self.chatbot.setObjectName("chatbot")
                self.verticalLayout_4.addWidget(self.chatbot)

                spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
                self.verticalLayout_4.addItem(spacerItem)
                self.verticalLayout_2.addWidget(self.frame_2)

                # ── Bottom frame (settings / logout / help / info) ────────────
                self.frame_3 = QtWidgets.QFrame(self.leftMenuSubContainer)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
                self.frame_3.setSizePolicy(sizePolicy)
                font = QtGui.QFont()
                font.setPointSize(10)
                self.frame_3.setFont(font)
                self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
                self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
                self.frame_3.setObjectName("frame_3")

                self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.frame_3)
                self.verticalLayout_5.setContentsMargins(10, 0, 0, 10)
                self.verticalLayout_5.setSpacing(0)
                self.verticalLayout_5.setObjectName("verticalLayout_5")

                self.setting = QtWidgets.QPushButton(self.frame_3)
                font = QtGui.QFont()
                font.setPointSize(10)
                self.setting.setFont(font)
                icon6 = QtGui.QIcon()
                icon6.addPixmap(QtGui.QPixmap(":/icon/icon/settings.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.setting.setIcon(icon6)
                self.setting.setIconSize(QtCore.QSize(30, 30))
                self.setting.setObjectName("setting")
                self.verticalLayout_5.addWidget(self.setting)

                self.logout = QtWidgets.QPushButton(self.frame_3)
                font = QtGui.QFont()
                font.setPointSize(10)
                self.logout.setFont(font)
                icon7 = QtGui.QIcon()
                icon7.addPixmap(QtGui.QPixmap(":/icon/icon/log-out.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.logout.setIcon(icon7)
                self.logout.setIconSize(QtCore.QSize(30, 30))
                self.logout.setObjectName("logout")
                self.verticalLayout_5.addWidget(self.logout)

                self.help = QtWidgets.QPushButton(self.frame_3)
                font = QtGui.QFont()
                font.setPointSize(10)
                self.help.setFont(font)
                icon8 = QtGui.QIcon()
                icon8.addPixmap(QtGui.QPixmap(":/icon/icon/help-circle.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.help.setIcon(icon8)
                self.help.setIconSize(QtCore.QSize(30, 30))
                self.help.setObjectName("help")
                self.verticalLayout_5.addWidget(self.help)

                self.information = QtWidgets.QPushButton(self.frame_3)
                font = QtGui.QFont()
                font.setPointSize(10)
                self.information.setFont(font)
                icon9 = QtGui.QIcon()
                icon9.addPixmap(QtGui.QPixmap(":/icon/icon/info.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.information.setIcon(icon9)
                self.information.setIconSize(QtCore.QSize(30, 30))
                self.information.setObjectName("information")
                self.verticalLayout_5.addWidget(self.information)
                self.verticalLayout_2.addWidget(self.frame_3, 0, QtCore.Qt.AlignBottom)
                self.verticalLayout.addWidget(self.leftMenuSubContainer, 0, QtCore.Qt.AlignLeft)
                self.horizontalLayout.addWidget(self.leftMenuContainer)
                
                # ── Main Body ─────────────────────────────────────────────────
                self.mainBodyContainer = QtWidgets.QWidget(self.centralwidget)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(self.mainBodyContainer.sizePolicy().hasHeightForWidth())
                self.mainBodyContainer.setSizePolicy(sizePolicy)
                font = QtGui.QFont()
                font.setKerning(False)
                self.mainBodyContainer.setFont(font)
                self.mainBodyContainer.setStyleSheet("background-color:white;")
                self.mainBodyContainer.setObjectName("mainBodyContainer")
                self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.mainBodyContainer)
                self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
                self.verticalLayout_11.setSpacing(0)
                self.verticalLayout_11.setObjectName("verticalLayout_11")

                # ── Header ────────────────────────────────────────────────────
                self.headerContainer = QtWidgets.QWidget(self.mainBodyContainer)
                self.headerContainer.setStyleSheet("background-color: white;")
                self.headerContainer.setObjectName("headerContainer")
                self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.headerContainer)
                self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
                self.horizontalLayout_4.setSpacing(0)
                self.horizontalLayout_4.setObjectName("horizontalLayout_4")

                self.frame_5 = QtWidgets.QFrame(self.headerContainer)
                self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
                self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
                self.frame_5.setObjectName("frame_5")
                self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.frame_5)
                self.horizontalLayout_6.setObjectName("horizontalLayout_6")
                self.label_5 = QtWidgets.QLabel(self.frame_5)
                self.label_5.setMinimumSize(QtCore.QSize(80, 75))
                self.label_5.setMaximumSize(QtCore.QSize(80, 75))
                self.label_5.setText("")
                _logo = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "images", "system_logo.png")
                self.label_5.setPixmap(QtGui.QPixmap(_logo))
                self.label_5.setScaledContents(True)
                self.label_5.setObjectName("label_5")
                self.horizontalLayout_6.addWidget(self.label_5)
                self.label_6 = QtWidgets.QLabel(self.frame_5)
                font = QtGui.QFont()
                font.setPointSize(16)
                font.setBold(True)
                font.setWeight(75)
                self.label_6.setFont(font)
                self.label_6.setObjectName("label_6")
                self.horizontalLayout_6.addWidget(self.label_6)
                self.horizontalLayout_4.addWidget(self.frame_5, 0, QtCore.Qt.AlignLeft)
                self.horizontalLayout_6.setSpacing(10)
                self.label_6.setStyleSheet("""
                        QLabel{
                        font-size: 22px;
                        font-weight: 800;
                        color: #6366F1;
                        padding: 8px;
                        letter-spacing: 1px;
                        }
                """)

                self.frame_6 = QtWidgets.QFrame(self.headerContainer)
                self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
                self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
                self.frame_6.setObjectName("frame_6")
                self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_6)
                self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
                self.horizontalLayout_5.setSpacing(15)
                self.horizontalLayout_5.setObjectName("horizontalLayout_5")

                self.moreMenu = QtWidgets.QPushButton(self.frame_6)
                self.moreMenu.setText("")
                icon11 = QtGui.QIcon()
                icon11.addPixmap(QtGui.QPixmap(":/icon/icon/more-horizontal.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.moreMenu.setIcon(icon11)
                self.moreMenu.setIconSize(QtCore.QSize(30, 30))
                self.moreMenu.setObjectName("pushButton_5")
                self.horizontalLayout_5.addWidget(self.moreMenu)

                self.profile = QtWidgets.QPushButton(self.frame_6)
                self.profile.setText("")
                icon12 = QtGui.QIcon()
                icon12.addPixmap(QtGui.QPixmap(":/icon/icon/user.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.profile.setIcon(icon12)
                self.profile.setIconSize(QtCore.QSize(30, 30))
                self.profile.setObjectName("pushButton_6")
                self.horizontalLayout_5.addWidget(self.profile)

                self.horizontalLayout_4.addWidget(self.frame_6, 0, QtCore.Qt.AlignHCenter)
                self.verticalLayout_11.addWidget(self.headerContainer)

                # ── Main body / stacked pages ─────────────────────────────────
                self.mainBodyContainer_2 = QtWidgets.QWidget(self.mainBodyContainer)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(self.mainBodyContainer_2.sizePolicy().hasHeightForWidth())
                self.mainBodyContainer_2.setSizePolicy(sizePolicy)
                self.mainBodyContainer_2.setLayoutDirection(QtCore.Qt.LeftToRight)
                self.mainBodyContainer_2.setStyleSheet("background-color: white;")
                self.mainBodyContainer_2.setObjectName("mainBodyContainer_2")
                self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.mainBodyContainer_2)
                self.horizontalLayout_7.setContentsMargins(0, 0, 9, 0)
                self.horizontalLayout_7.setSpacing(0)
                self.horizontalLayout_7.setObjectName("horizontalLayout_7")

                self.mainContentContainer = QtWidgets.QWidget(self.mainBodyContainer_2)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(self.mainContentContainer.sizePolicy().hasHeightForWidth())
                self.mainContentContainer.setSizePolicy(sizePolicy)
                self.mainContentContainer.setObjectName("mainContentContainer")
                self.verticalLayout_16 = QtWidgets.QVBoxLayout(self.mainContentContainer)
                self.verticalLayout_16.setContentsMargins(0, 0, 0, 0)
                self.verticalLayout_16.setSpacing(0)
                self.verticalLayout_16.setObjectName("verticalLayout_16")

                self.stackedWidget_3 = QCustomStackedWidget(self.mainContentContainer)
                self.stackedWidget_3.setObjectName("stackedWidget_3")

                # ── Index 0 : Home ────────────────────────────────────────────
                self.home_page = QtWidgets.QWidget()
                self.home_page.setObjectName("home_page")
                self.home_vertical_layout = QtWidgets.QVBoxLayout(self.home_page)
                self.home_vertical_layout.setContentsMargins(20, 20, 20, 20)
                self.home_vertical_layout.setSpacing(30)
                self.home_vertical_layout.setAlignment(QtCore.Qt.AlignTop)

                self.home_scroll = QtWidgets.QScrollArea(self.mainContentContainer)
                self.home_scroll.setWidgetResizable(True)
                self.home_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
                self.home_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
                self.home_scroll.setWidget(self.home_page)

                font = QtGui.QFont()
                font.setPointSize(20)
                self.stackedWidget_3.addWidget(self.home_scroll)   # index 0

                self.card1 = self.create_card("Face Recognition",   "Start scanning",    ":/icon/icon/face-recognition.svg")
                self.card2 = self.create_card("Student Management", "Manage database",   ":/icon/icon/users.svg")
                self.card3 = self.create_card("Attendance Records", "View logs",         ":/icon/icon/server.svg")
                self.card4 = self.create_card("Reports",            "Generate reports",  ":/icon/icon/printer.svg")

                self.cards_layout = QtWidgets.QHBoxLayout()
                self.cards_layout.setSpacing(20)
                self.cards_layout.setAlignment(QtCore.Qt.AlignCenter)
                self.cards_layout.addWidget(self.card1)
                self.cards_layout.addWidget(self.card2)
                self.cards_layout.addWidget(self.card3)
                self.cards_layout.addWidget(self.card4)
                self.home_vertical_layout.addLayout(self.cards_layout)

                # ── Index 1 : Face Recognition ────────────────────────────────
                self.face_page = QtWidgets.QWidget()
                self.face_page.setObjectName("face_page")
                self.face_layout = QtWidgets.QVBoxLayout(self.face_page)
                self.face_layout.setContentsMargins(40, 40, 40, 40)
                self.face_layout.setSpacing(30)
                self.face_layout.setAlignment(Qt.AlignTop)

                self.face_label = QtWidgets.QLabel("Face Recognition", self.face_page)
                self.face_label.setAlignment(Qt.AlignCenter)
                font = QtGui.QFont()
                font.setPointSize(22)
                font.setBold(True)
                self.face_label.setFont(font)
                self.face_label.setStyleSheet("color: #0F172A;")
                self.face_layout.addWidget(self.face_label)

                self.camera_frame = QtWidgets.QFrame(self.face_page)
                self.camera_frame.setMinimumSize(QtCore.QSize(800, 450))
                self.camera_frame.setStyleSheet("""
                QFrame {
                        background-color: #F3F4F6;
                        border-radius: 20px;
                        border: 2px dashed #9CA3AF;
                }
                """)
                self.camera_frame_layout = QtWidgets.QVBoxLayout(self.camera_frame)
                self.camera_preview = QtWidgets.QLabel("Camera Preview")
                self.camera_preview.setObjectName("camera_label")
                self.camera_preview.setAlignment(Qt.AlignCenter)
                self.camera_preview.setStyleSheet("color: #6B7280; font-size: 18px;")
                self.camera_frame_layout.addWidget(self.camera_preview)
                self.face_layout.addWidget(self.camera_frame, alignment=Qt.AlignCenter)

                self.face_button_layout = QtWidgets.QHBoxLayout()
                self.face_button_layout.setSpacing(20)
                self.face_button_layout.setAlignment(Qt.AlignCenter)

                self.start_camera_btn = QtWidgets.QPushButton("Start Camera")
                self.start_camera_btn.setStyleSheet("""
                QPushButton {
                        background-color: #2563EB; color: white;
                        border-radius: 10px; padding: 12px 24px; font-size: 14px;
                }
                QPushButton:hover { background-color: #1D4ED8; }
                """)

                self.stop_camera_btn = QtWidgets.QPushButton("Stop Camera")
                self.stop_camera_btn.setStyleSheet("""
                QPushButton {
                        background-color: #DC2626; color: white;
                        border-radius: 10px; padding: 12px 24px; font-size: 14px;
                }
                QPushButton:hover { background-color: #B91C1C; }
                """)
                self.face_button_layout.addWidget(self.start_camera_btn)
                self.face_button_layout.addWidget(self.stop_camera_btn)
                self.face_layout.addLayout(self.face_button_layout)

                self.status_label = QtWidgets.QLabel("Status: Waiting to start camera...")
                self.status_label.setAlignment(Qt.AlignCenter)
                self.status_label.setStyleSheet("color: #4B5563; font-size: 14px;")
                self.face_layout.addWidget(self.status_label)

                self.stackedWidget_3.addWidget(self.face_page)           # index 1

                # ── Index 2 : Student Management ─────────────────────────────
                self.student_page = QtWidgets.QWidget()
                self.student_page.setObjectName("student_page")
                self.student_layout = QtWidgets.QVBoxLayout(self.student_page)
                self.student_layout.setContentsMargins(40, 40, 40, 40)
                self.student_layout.setSpacing(20)

                self.student_label = QtWidgets.QLabel("Student Management")
                self.student_label.setAlignment(Qt.AlignCenter)
                font = QtGui.QFont()
                font.setPointSize(22)
                font.setBold(True)
                self.student_label.setFont(font)
                self.student_label.setStyleSheet("color: #0F172A;")
                self.student_layout.addWidget(self.student_label)

                form_frame = QtWidgets.QFrame()
                form_frame.setStyleSheet("""
                QFrame {
                        background-color: #F9FAFB; border-radius: 10px; border: 1px solid #E5E7EB;
                }
                QLabel { font-size: 14px; color: #374151; }
                QLineEdit, QComboBox {
                        background-color: white; border: 1px solid #D1D5DB;
                        border-radius: 6px; padding: 6px; font-size: 13px;
                }
                QPushButton {
                        background-color: #2563EB; color: white;
                        border-radius: 8px; padding: 8px 16px; font-size: 14px;
                }
                QPushButton:hover { background-color: #1D4ED8; }
                """)
                form_layout = QtWidgets.QGridLayout(form_frame)
                form_layout.setSpacing(15)

                self.name_input       = QtWidgets.QLineEdit()
                self.email_input      = QtWidgets.QLineEdit()
                self.id_input         = QtWidgets.QLineEdit()
                self.department_input = QtWidgets.QComboBox()
                self.department_input.addItems(["Computer Science", "IT", "Electronics", "Mechanical", "Civil"])
                self.year_input = QtWidgets.QComboBox()
                self.year_input.addItems(["1st Year", "2nd Year", "3rd Year", "4th Year"])
                self.add_image_btn = QtWidgets.QPushButton("Add Image")
                self.add_image_btn.setCursor(QtCore.Qt.PointingHandCursor)

                form_layout.addWidget(QtWidgets.QLabel("Student Name:"), 0, 0)
                form_layout.addWidget(self.name_input, 0, 1)
                form_layout.addWidget(QtWidgets.QLabel("Student ID:"), 0, 2)
                form_layout.addWidget(self.id_input, 0, 3)
                form_layout.addWidget(QtWidgets.QLabel("Email:"), 1, 0)
                form_layout.addWidget(self.email_input, 1, 1)
                form_layout.addWidget(QtWidgets.QLabel("Department:"), 2, 0)
                form_layout.addWidget(self.department_input, 2, 1)
                form_layout.addWidget(QtWidgets.QLabel("Year:"), 2, 2)
                form_layout.addWidget(self.year_input, 2, 3)
                form_layout.addWidget(self.add_image_btn)

                self.add_student_btn = QtWidgets.QPushButton("Add Student")
                self.add_student_btn.setCursor(QtCore.Qt.PointingHandCursor)
                form_layout.addWidget(self.add_student_btn, 3, 3, 1, 1)
                self.student_layout.addWidget(form_frame)

                self.search_bar = QtWidgets.QLineEdit()
                self.search_bar.setStyleSheet("""
                        QLineEdit {
                        background-color: white; border: 1px solid #D1D5DB;
                        border-radius: 10px; padding: 8px 12px; font-size: 13px;
                        }
                        QLineEdit:focus { border: 1px solid #2563EB; }
                """)
                self.search_bar.setPlaceholderText("Search by name or ID...")
                self.student_layout.addWidget(self.search_bar)
                search_icon = QtWidgets.QAction(QtGui.QIcon(":/icon/icon/search.svg"), "", self.search_bar)
                self.search_bar.addAction(search_icon, QtWidgets.QLineEdit.LeadingPosition)

                self.student_table = QtWidgets.QTableWidget()
                self.student_table.setStyleSheet("""
                QTableWidget {
                background-color: #FFFFFF; alternate-background-color: #F9FAFB;
                border: 1px solid #E5E7EB; gridline-color: #E5E7EB;
                font-size: 13px; color: #111827;
                selection-background-color: #DBEAFE; selection-color: #111827;
                }
                QHeaderView::section {
                background-color: #F9FAFB; color: #374151; font-weight: 600;
                border: none; border-bottom: 1px solid #E5E7EB; padding: 8px;
                }
                QTableWidget::item { padding: 6px; }
                QTableWidget::item:hover { background-color: #F3F4F6; color: black; }
                QTableWidget::item:selected { background-color: #DBEAFE; color: #111827; }
                QScrollBar:vertical { background: #F9FAFB; width: 8px; }
                QScrollBar::handle:vertical { background: #D1D5DB; border-radius: 4px; }
                QScrollBar::handle:vertical:hover { background: #9CA3AF; }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
                """)
                self.student_table.setAlternatingRowColors(True)
                self.student_table.verticalHeader().setVisible(False)
                self.student_table.setShowGrid(True)
                self.student_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
                self.student_table.setColumnCount(6)
                self.student_table.setHorizontalHeaderLabels(["Name", "ID", "Department", "Year", "Email", "Actions"])
                self.student_table.horizontalHeader().setStretchLastSection(True)
                self.student_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
                self.student_layout.addWidget(self.student_table)

                self.stackedWidget_3.addWidget(self.student_page)        # index 2

                # ── Index 3 : Attendance Records ──────────────────────────────
                self.attendance_page = QtWidgets.QWidget()
                self.attendance_page.setObjectName("attendance_page")
                self.attendance_layout = QtWidgets.QVBoxLayout(self.attendance_page)

                self.attendance_label = QtWidgets.QLabel("Attendance Records", self.attendance_page)
                self.attendance_label.setAlignment(QtCore.Qt.AlignCenter)
                self.attendance_label.setFont(font)
                self.attendance_layout.addWidget(self.attendance_label)

                self.attendance_table = QtWidgets.QTableWidget()
                self.attendance_table.setColumnCount(6)
                self.attendance_table.setHorizontalHeaderLabels(
                        ["Name", "Department", "Year", "Date", "Time", "Status"]
                )
                self.attendance_table.horizontalHeader().setStretchLastSection(True)
                self.attendance_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
                self.attendance_table.setStyleSheet("""
                        QTableWidget {
                        background-color: #FFFFFF; alternate-background-color: #F9FAFB;
                        border: 1px solid #E5E7EB; gridline-color: #E5E7EB;
                        font-size: 13px; color: #111827;
                        selection-background-color: #DBEAFE;
                        }
                        QHeaderView::section {
                        background-color: #F9FAFB; color: #374151; font-weight: 600;
                        padding: 8px; border: none; border-bottom: 1px solid #E5E7EB;
                        }
                        QTableWidget::item:hover { background-color: #F3F4F6; color: black; }
                        QTableWidget::item:selected { background-color: #DBEAFE; color: #111827; }
                        QScrollBar:vertical { background: #F9FAFB; width: 8px; }
                        QScrollBar::handle:vertical { background: #D1D5DB; border-radius: 4px; }
                """)
                self.attendance_table.setAlternatingRowColors(True)
                self.attendance_table.verticalHeader().setVisible(False)
                self.attendance_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
                self.attendance_layout.addWidget(self.attendance_table)

                self.stackedWidget_3.addWidget(self.attendance_page)     # index 3

                # ── Index 4 : Reports ─────────────────────────────────────────
                self.reports_page = QtWidgets.QWidget()
                self.reports_page.setObjectName("reports_page")
                self.reports_layout = QtWidgets.QVBoxLayout(self.reports_page)
                self.reports_label = QtWidgets.QLabel("Reports", self.reports_page)
                self.reports_label.setAlignment(QtCore.Qt.AlignCenter)
                self.reports_label.setFont(font)
                self.reports_layout.addWidget(self.reports_label)
                self.stackedWidget_3.addWidget(self.reports_page)        # index 4

                # ── Index 5 : Chatbot (embedded) ──────────────────────────────
                # ChatbotWidget is created here as a placeholder container.
                # main.py will call setup_chatbot_page() after login to inject
                # the real ChatbotWidget with live db / attendance_manager refs.
                self.chatbot_page = QtWidgets.QWidget()
                self.chatbot_page.setObjectName("chatbot_page")
                self.chatbot_page.setStyleSheet("background-color: #0D1117;")
                self.chatbot_page_layout = QtWidgets.QVBoxLayout(self.chatbot_page)
                self.chatbot_page_layout.setContentsMargins(0, 0, 0, 0)
                self.chatbot_page_layout.setSpacing(0)

                # Placeholder shown before login / before setup_chatbot_page() is called
                _placeholder = QtWidgets.QLabel("🤖  Loading Attendance AI…")
                _placeholder.setAlignment(Qt.AlignCenter)
                _placeholder.setStyleSheet("color: #8B949E; font-size: 16px;")
                self.chatbot_page_layout.addWidget(_placeholder)
                self._chatbot_placeholder = _placeholder

                self.stackedWidget_3.addWidget(self.chatbot_page)        # index 5

                # ── Index 6 : page_11 ─────────────────────────────────────────
                self.page_11 = QtWidgets.QWidget()
                self.page_11.setObjectName("page_11")
                self.verticalLayout_22 = QtWidgets.QVBoxLayout(self.page_11)
                self.verticalLayout_22.setObjectName("verticalLayout_22")
                self.stackedWidget_3.addWidget(self.page_11)             # index 6

                self.verticalLayout_16.addWidget(self.stackedWidget_3)
                self.horizontalLayout_7.addWidget(self.mainContentContainer)

                # ── Profile / More-menu placeholder pages ────────────────────
                self.page_4 = QtWidgets.QWidget()
                self.page_4.setObjectName("page_4")
                self.verticalLayout_14 = QtWidgets.QVBoxLayout(self.page_4)
                self.verticalLayout_14.setObjectName("verticalLayout_14")
                self.label_8 = QtWidgets.QLabel(self.page_4)
                font = QtGui.QFont()
                font.setPointSize(20)
                self.label_8.setFont(font)
                self.label_8.setLayoutDirection(QtCore.Qt.LeftToRight)
                self.label_8.setStyleSheet("background-color: rgb(255, 255, 255);")
                self.label_8.setAlignment(QtCore.Qt.AlignCenter)
                self.label_8.setObjectName("label_8")
                self.verticalLayout_14.addWidget(self.label_8)
                self.stackedWidget_3.addWidget(self.page_4)

                self.page_5 = QtWidgets.QWidget()
                self.page_5.setObjectName("page_5")
                self.verticalLayout_15 = QtWidgets.QVBoxLayout(self.page_5)
                self.verticalLayout_15.setObjectName("verticalLayout_15")
                self.label_9 = QtWidgets.QLabel(self.page_5)
                font = QtGui.QFont()
                font.setPointSize(20)
                self.label_9.setFont(font)
                self.label_9.setLayoutDirection(QtCore.Qt.LeftToRight)
                self.label_9.setStyleSheet("background-color: rgb(255, 255, 255);")
                self.label_9.setAlignment(QtCore.Qt.AlignCenter)
                self.label_9.setObjectName("label_9")
                self.verticalLayout_15.addWidget(self.label_9)

                self.verticalLayout_11.addWidget(self.mainBodyContainer_2)
                self.horizontalLayout.addWidget(self.mainBodyContainer)
                MainWindow.setCentralWidget(self.centralwidget)
                self.statusbar = QtWidgets.QStatusBar(MainWindow)
                self.statusbar.setObjectName("statusbar")
                MainWindow.setStatusBar(self.statusbar)

                self.retranslateUi(MainWindow)
                self.apply_theme_icons()
                self.stackedWidget_3.setCurrentIndex(0)
                QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # ── Called by main.py after login to inject the live ChatbotWidget ──

        def setup_chatbot_page(self, db, attendance_manager, teacher_account_id, current_user):
                """
                Replace the placeholder in chatbot_page with the real ChatbotWidget.
                Call this from MainWindow.__init__ after the user has logged in.
                """
                from popups.chatbot_popup import ChatbotWidget

                # Remove placeholder
                if hasattr(self, "_chatbot_placeholder") and self._chatbot_placeholder:
                        self._chatbot_placeholder.deleteLater()
                        self._chatbot_placeholder = None

                # Remove any existing widgets from the layout
                while self.chatbot_page_layout.count():
                        item = self.chatbot_page_layout.takeAt(0)
                        if item.widget():
                                item.widget().deleteLater()

                # Create and embed the real widget
                self.chatbot_widget = ChatbotWidget(
                        db=db,
                        attendance_manager=attendance_manager,
                        teacher_account_id=teacher_account_id,
                        current_user=current_user,
                        parent=self.chatbot_page,
                )
                self.chatbot_page_layout.addWidget(self.chatbot_widget)

        # ── load_attendance_records (unchanged) ──────────────────────────────

        def load_attendance_records(self, parent=None):
                try:
                        main_window = parent
                        if not main_window:
                                main_window = self.stackedWidget_3.parent()
                                while main_window and not hasattr(main_window, 'teacher_account_id'):
                                        main_window = main_window.parent()

                        if not main_window or not hasattr(main_window, 'teacher_account_id'):
                                print("Error: Could not find MainWindow with teacher_account_id")
                                return

                        main_window.db.initialize_today_attendance(main_window.teacher_account_id)
                        records = main_window.db.get_today_attendance_sheet(main_window.teacher_account_id)
                        self.attendance_table.setRowCount(0)

                        for row_idx, record in enumerate(records):
                                self.attendance_table.insertRow(row_idx)
                                self.attendance_table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(record.get("name", "")))
                                self.attendance_table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(record.get("dept", "")))
                                self.attendance_table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(record.get("year", "")))
                                self.attendance_table.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(record.get("date", "")))
                                self.attendance_table.setItem(row_idx, 4, QtWidgets.QTableWidgetItem(record.get("time", "")))

                                status      = record.get("status", "")
                                status_item = QtWidgets.QTableWidgetItem(status)

                                if status == "Present":
                                        status_item.setBackground(QtGui.QColor("#DCFCE7"))
                                        status_item.setForeground(QtGui.QColor("#166534"))
                                elif status == "Absent":
                                        status_item.setBackground(QtGui.QColor("#FEE2E2"))
                                        status_item.setForeground(QtGui.QColor("#991B1B"))
                                elif status == "Late":
                                        status_item.setBackground(QtGui.QColor("#FEF3C7"))
                                        status_item.setForeground(QtGui.QColor("#92400E"))

                                self.attendance_table.setItem(row_idx, 5, status_item)

                        print(f"✅ Loaded {len(records)} students for today's attendance")
                except Exception as e:
                        print(f"❌ Error loading attendance records: {e}")
                        import traceback
                        traceback.print_exc()

        def retranslateUi(self, MainWindow):
                _translate = QtCore.QCoreApplication.translate
                MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
                self.menu.setToolTip(_translate("MainWindow", "Menu"))
                self.home.setToolTip(_translate("MainWindow", "Home"))
                self.home.setText(_translate("MainWindow", "Home"))
                self.facerecognition.setToolTip(_translate("MainWindow", "Face Recognition"))
                self.facerecognition.setText(_translate("MainWindow", "Face Recognition"))
                self.studentmanagement.setToolTip(_translate("MainWindow", "Student Management"))
                self.studentmanagement.setText(_translate("MainWindow", "Student Management"))
                self.attendancerecords.setToolTip(_translate("MainWindow", "Attendance Records"))
                self.attendancerecords.setText(_translate("MainWindow", "Attendance Records"))
                self.reports.setToolTip(_translate("MainWindow", "View Reports"))
                self.reports.setText(_translate("MainWindow", "Reports"))
                self.chatbot.setToolTip(_translate("MainWindow", "AI Chat Assistant"))
                self.chatbot.setText(_translate("MainWindow", "Chatbot"))
                self.setting.setToolTip(_translate("MainWindow", "Go to settings"))
                self.setting.setText(_translate("MainWindow", "setting"))
                self.logout.setToolTip(_translate("MainWindow", "Logout"))
                self.logout.setText(_translate("MainWindow", "Logout"))
                self.help.setToolTip(_translate("MainWindow", "Help"))
                self.help.setText(_translate("MainWindow", "Help"))
                self.information.setToolTip(_translate("MainWindow", "Information about the App"))
                self.information.setText(_translate("MainWindow", "Information"))
                self.moreMenu.setToolTip(_translate("MainWindow", "More Menu"))
                self.profile.setToolTip(_translate("MainWindow", "Profile"))
                self.face_label.setText(_translate("MainWindow", "Face Recognition"))
                self.student_label.setText(_translate("MainWindow", "Student Management"))
                self.attendance_label.setText(_translate("MainWindow", "Attendance records"))
                self.reports_label.setText(_translate("MainWindow", "Reports"))
                self.label_6.setText(_translate("MainWindow", "Face Recognition"))
                self.label_8.setText(_translate("MainWindow", "Profile"))
                self.label_9.setText(_translate("MainWindow", "More...."))

import utils.resources_rc as resources_rc