# gui.py
import markdown
import re
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextBrowser, QLineEdit, QFrame, QLabel, 
                             QPushButton, QStackedWidget, QApplication, QTabBar, QHBoxLayout, 
                             QTreeView, QHeaderView, QDialog, QMenu, QScrollArea, QListWidget, QListWidgetItem)
from PyQt6.QtGui import QFileSystemModel, QAction, QColor, QFont, QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QUrl, QDir, QSize, QPropertyAnimation, QEasingCurve
from styles import (OMNI_STYLESHEET, USER_MSG_HTML, AI_MSG_HTML, CODE_BLOCK_STYLE, 
                    HELP_MSG_HTML, ACCENT, ACCENT_LOW, TEXT_PRIMARY, TEXT_SECONDARY, BG_CARD, BORDER_COLOR)
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_FLAGS

class OmniModal(QDialog):
    """ Modal informativo con estética moderna y limpia. """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(450, 480)
        layout = QVBoxLayout(self)
        container = QFrame()
        container.setObjectName("MainContainer")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(30, 30, 30, 30)
        c_layout.setSpacing(15)
        
        header = QHBoxLayout()
        title = QLabel("OMNI CORE")
        title.setStyleSheet(f"color: {ACCENT}; font-weight: 800; font-size: 22px; border: none;")
        ver = QLabel("v1.0.2")
        ver.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: bold; font-size: 12px; border: none;")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(ver)
        
        desc = QLabel("Advanced neural-link HUD for real-time information processing and LPU-powered AI interaction.")
        desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px; border: none; line-height: 1.5;")
        desc.setWordWrap(True)
        
        hk_box = QFrame()
        hk_box.setStyleSheet("background-color: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 15px;")
        hk_layout = QVBoxLayout(hk_box)
        hks = [("CTRL + SPACE", "Toggle HUD Visibility"), ("CTRL + SHIFT + R", "System Audio Capture"), 
               ("CTRL + SHIFT + M", "Microphone Capture"), ("ESC", "Navigate Back / Hide")]
        for key, d in hks:
            row = QHBoxLayout()
            k = QLabel(key)
            k.setStyleSheet(f"color: {ACCENT}; font-size: 11px; font-weight: 800; border: none; background: {ACCENT_LOW}; padding: 2px 6px; border-radius: 4px;")
            v = QLabel(d)
            v.setStyleSheet("color: #777; font-size: 11px; border: none;")
            row.addWidget(k)
            row.addStretch()
            row.addWidget(v)
            hk_layout.addLayout(row)
            
        close_btn = QPushButton("GOT IT")
        close_btn.setFixedHeight(45)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        
        c_layout.addLayout(header)
        c_layout.addWidget(desc)
        c_layout.addWidget(hk_box)
        c_layout.addStretch()
        c_layout.addWidget(close_btn)
        layout.addWidget(container)

class ChatItemWidget(QWidget):
    """ Widget de chat refinado con iconos estándar. """
    delete_clicked = pyqtSignal()
    rename_requested = pyqtSignal(str)
    
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 4, 8, 4)
        self.layout.setSpacing(10)
        
        self.icon_lbl = QLabel("💬")
        self.icon_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px; border: none;")
        
        self.label = QLabel(title)
        self.label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; background: transparent; border: none;")
        
        self.edit_input = QLineEdit(title)
        self.edit_input.hide()
        self.edit_input.returnPressed.connect(self._finish_rename)
        
        self.btn_edit = QPushButton("✏")
        self.btn_edit.setObjectName("IconButton")
        self.btn_edit.setFixedSize(28, 28)
        self.btn_edit.clicked.connect(self._start_rename)
        
        self.btn_del = QPushButton("🗑")
        self.btn_del.setObjectName("IconButton")
        self.btn_del.setFixedSize(28, 28)
        self.btn_del.setStyleSheet("color: #ef4444;")
        self.btn_del.clicked.connect(self.delete_clicked.emit)
        
        self.layout.addWidget(self.icon_lbl)
        self.layout.addWidget(self.label, 1)
        self.layout.addWidget(self.edit_input, 1)
        self.layout.addWidget(self.btn_edit)
        self.layout.addWidget(self.btn_del)

    def set_selected(self, selected: bool):
        color = ACCENT if selected else TEXT_SECONDARY
        self.label.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: {'800' if selected else '400'}; border: none;")
        self.icon_lbl.setStyleSheet(f"color: {color}; font-size: 14px; border: none;")

    def _start_rename(self):
        self.label.hide()
        self.btn_edit.hide()
        self.edit_input.show()
        self.edit_input.setFocus()
        self.edit_input.selectAll()

    def _finish_rename(self):
        new_title = self.edit_input.text().strip()
        if new_title:
            self.rename_requested.emit(new_title)
            self.label.setText(new_title)
        self.edit_input.hide()
        self.label.show()
        self.btn_edit.show()

class OmniUI(QWidget):
    submission_requested = pyqtSignal(str)
    chat_cleared = pyqtSignal()
    config_saved = pyqtSignal(str)
    chat_selected = pyqtSignal(int)
    chat_delete_requested = pyqtSignal(int)
    chat_rename_requested = pyqtSignal(int, str)
    new_chat_requested = pyqtSignal()
    file_selected = pyqtSignal(str)
    login_requested = pyqtSignal(str, str)
    activation_requested = pyqtSignal(str)
    tool_selected = pyqtSignal(str)
    update_requested = pyqtSignal()
    logout_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.chat_history = []
        self._drag_pos = QPoint()
        self.sidebar_expanded = False
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        self.setWindowFlags(WINDOW_FLAGS)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(950, 700)
        self.center_window()
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(0)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(15, 30, 15, 30)
        self.sidebar_layout.setSpacing(12)
        
        self.new_chat_btn = QPushButton("➕ NEW SESSION")
        self.new_chat_btn.setObjectName("SideBtnMain")
        self.new_chat_btn.setFixedHeight(45)
        self.new_chat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.new_chat_btn.clicked.connect(self.new_chat_requested.emit)
        
        side_label = QLabel("HISTORY")
        side_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: 800; font-size: 10px; letter-spacing: 2px; margin-top: 20px; margin-left: 5px;")
        
        self.chat_list = QListWidget()
        self.chat_list.setObjectName("ChatList")
        self.chat_list.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chat_list.currentRowChanged.connect(self._handle_row_changed)
        
        self.sidebar_layout.addWidget(self.new_chat_btn)
        self.sidebar_layout.addWidget(side_label)
        self.sidebar_layout.addWidget(self.chat_list)
        self.sidebar_layout.addStretch()
        
        self.profile_btn = QPushButton("👤 PROFILE")
        self.profile_btn.setObjectName("IconButton")
        self.profile_btn.setFixedHeight(38)
        self.logout_btn = QPushButton("🚪 LOGOUT")
        self.logout_btn.setObjectName("IconButton")
        self.logout_btn.setFixedHeight(38)
        self.logout_btn.setStyleSheet("color: #ef4444;")
        
        self.profile_btn.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        self.logout_btn.clicked.connect(self.logout_requested.emit)
        
        self.sidebar_layout.addWidget(self.profile_btn)
        self.sidebar_layout.addWidget(self.logout_btn)

        # Content Area
        self.content_area = QFrame()
        self.content_area.setObjectName("MainContainer")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        self.top_bar = QHBoxLayout()
        self.top_bar.setContentsMargins(15, 12, 20, 12)
        
        self.hamburger_btn = QPushButton("☰")
        self.hamburger_btn.setObjectName("IconButton")
        self.hamburger_btn.setFixedSize(40, 40)
        self.hamburger_btn.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.hamburger_btn.clicked.connect(self.toggle_sidebar)
        
        self.drag_handle = QFrame()
        self.drag_handle.setObjectName("DragHandle")
        
        self.info_btn = QPushButton("ⓘ")
        self.info_btn.setObjectName("IconButton")
        self.info_btn.setFixedSize(40, 40)
        self.info_btn.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        self.info_btn.clicked.connect(self._show_info_modal)
        
        self.close_app_btn = QPushButton("✕")
        self.close_app_btn.setObjectName("IconButton")
        self.close_app_btn.setFixedSize(40, 40)
        self.close_app_btn.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        self.close_app_btn.clicked.connect(QApplication.quit)
        
        self.top_bar.addWidget(self.hamburger_btn)
        self.top_bar.addWidget(self.drag_handle, 1)
        self.top_bar.addWidget(self.info_btn)
        self.top_bar.addWidget(self.close_app_btn)
        
        self.stack = QStackedWidget()
        self._build_pages()
        
        self.content_layout.addLayout(self.top_bar)
        self.content_layout.addWidget(self.stack)
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area)

    def _build_pages(self):
        self.login_page = QWidget(); self._build_login_page()
        self.activation_page = QWidget(); self._build_activation_page()
        self.config_page = QWidget(); self._build_config_page()
        self.chat_page = QWidget(); self._build_chat_page()
        self.file_page = QWidget(); self._build_file_page()
        self.profile_page = QWidget(); self._build_profile_page()
        for p in [self.login_page, self.activation_page, self.config_page, self.chat_page, self.file_page, self.profile_page]:
            self.stack.addWidget(p)

    def _build_activation_page(self):
        layout = QVBoxLayout(self.activation_page)
        layout.setContentsMargins(120, 80, 120, 80)
        layout.setSpacing(20)
        
        icon = QLabel("🔐")
        icon.setStyleSheet("font-size: 60px; margin-bottom: 10px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("System Activation")
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 28px; font-weight: 900;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        desc = QLabel("Enter your neural access key to link this device to your workspace.")
        desc.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px; margin-bottom: 20px;")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("OMNI-XXXX-XXXX-XXXX")
        self.key_input.setFixedHeight(55)
        self.key_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.key_input.setStyleSheet(f"font-family: 'JetBrains Mono'; font-size: 18px; font-weight: bold; color: {ACCENT};")
        
        self.activate_btn = QPushButton("ACTIVATE OMNI")
        self.activate_btn.setFixedHeight(55)
        self.activate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.activate_btn.setStyleSheet(f"background: {ACCENT}; color: #000; font-weight: 800; border-radius: 14px;")
        
        self.activation_error = QLabel("")
        self.activation_error.setStyleSheet("color: #ef4444; font-size: 12px; font-weight: 600;")
        self.activation_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addWidget(self.key_input)
        layout.addWidget(self.activation_error)
        layout.addWidget(self.activate_btn)
        layout.addStretch()

    def set_activation_loading(self, loading: bool):
        if loading:
            self.activate_btn.setText("VALIDATING KEY...")
            self.activate_btn.setEnabled(False)
        else:
            self.activate_btn.setText("ACTIVATE OMNI")
            self.activate_btn.setEnabled(True)

    def _build_login_page(self):
        layout = QVBoxLayout(self.login_page)
        layout.setContentsMargins(120, 80, 120, 80)
        layout.setSpacing(20)
        
        logo = QLabel("🤖")
        logo.setStyleSheet(f"color: {ACCENT}; font-size: 80px; margin-bottom: 20px;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Welcome to Omni")
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 32px; font-weight: 900; letter-spacing: -1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("Sign in to your neural workspace")
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px; margin-bottom: 30px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email address")
        self.email_input.setFixedHeight(50)
        self.email_input.returnPressed.connect(self._trigger_login)
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setFixedHeight(50)
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.returnPressed.connect(self._trigger_login)
        
        self.login_btn = QPushButton("SIGN IN")
        self.login_btn.setFixedHeight(55)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT}, stop:1 #059669);
                color: #000;
                font-size: 14px;
                font-weight: 800;
                border-radius: 14px;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #34d399, stop:1 #10b981);
            }}
            QPushButton:disabled {{
                background: #222;
                color: #555;
            }}
        """)
        self.login_btn.clicked.connect(self._trigger_login)
        
        self.login_error = QLabel("")
        self.login_error.setStyleSheet("color: #ef4444; font-size: 12px; font-weight: 600;")
        self.login_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.email_input)
        layout.addWidget(self.pass_input)
        layout.addWidget(self.login_error)
        layout.addWidget(self.login_btn)
        layout.addStretch()

    def _trigger_login(self):
        if not self.email_input.text().strip() or not self.pass_input.text().strip():
            self.login_error.setText("ERROR: MISSING CREDENTIALS")
            return
        self.set_login_loading(True)
        self.login_requested.emit(self.email_input.text(), self.pass_input.text())

    def set_login_loading(self, loading: bool):
        if loading:
            self.login_btn.setText("AUTHENTICATING...")
            self.login_btn.setEnabled(False)
        else:
            self.login_btn.setText("SIGN IN")
            self.login_btn.setEnabled(True)

    def _build_config_page(self):
        layout = QVBoxLayout(self.config_page)
        layout.setContentsMargins(120, 100, 120, 100)
        layout.setSpacing(25)
        title = QLabel("ENGINE CONFIG")
        title.setStyleSheet(f"color: {ACCENT}; font-size: 26px; font-weight: 900; letter-spacing: 1px;")
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter Groq API Key")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        btn = QPushButton("INITIALIZE SYSTEM")
        btn.setFixedHeight(50)
        btn.clicked.connect(lambda: self.config_saved.emit(self.key_input.text().strip()))
        layout.addWidget(title)
        layout.addWidget(self.key_input)
        layout.addWidget(btn)
        layout.addStretch()

    def _build_chat_page(self):
        layout = QVBoxLayout(self.chat_page)
        layout.setContentsMargins(25, 10, 25, 25)
        
        self.chat_display = QTextBrowser()
        self.chat_display.setOpenExternalLinks(False)
        
        input_container = QFrame()
        input_container.setStyleSheet(f"background: {BG_CARD}; border: 1px solid {BORDER_COLOR}; border-radius: 18px;")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(12, 6, 12, 6)
        
        self.tools_btn = QPushButton("+")
        self.tools_btn.setObjectName("IconButton")
        self.tools_btn.setFixedSize(38, 38)
        self.tools_btn.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")
        self._build_tools_menu()
        self.tools_btn.clicked.connect(self._show_tools_menu)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Send a message to Omni...")
        self.input_field.setStyleSheet("background: transparent; border: none; padding: 10px; font-size: 14px;")
        self.input_field.returnPressed.connect(self.handle_submission)
        
        self.clip_btn = QPushButton("📎")
        self.clip_btn.setObjectName("IconButton")
        self.clip_btn.setFixedSize(38, 38)
        self.clip_btn.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        self.clip_btn.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        
        input_layout.addWidget(self.tools_btn)
        input_layout.addWidget(self.input_field, 1)
        input_layout.addWidget(self.clip_btn)
        
        layout.addWidget(self.chat_display)
        layout.addWidget(input_container)

    def _build_file_page(self):
        layout = QVBoxLayout(self.file_page)
        layout.setContentsMargins(25, 15, 25, 25)
        layout.setSpacing(15)
        
        header = QHBoxLayout()
        title = QLabel("SYSTEM_FILES")
        title.setStyleSheet(f"color: {ACCENT}; font-weight: 800; font-size: 15px; letter-spacing: 1px;")
        back_btn = QPushButton("BACK")
        back_btn.setObjectName("IconButton")
        back_btn.setFixedSize(80, 35)
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        header.addWidget(title)
        header.addStretch()
        header.addWidget(back_btn)
        
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.rootPath())
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setRootIndex(self.file_model.index(QDir.homePath()))
        self.tree_view.setColumnWidth(0, 400)
        self.tree_view.setColumnHidden(1, True)
        self.tree_view.setColumnHidden(2, True)
        self.tree_view.setColumnHidden(3, True)
        self.tree_view.doubleClicked.connect(self._handle_file_double_click)

        self.analyze_btn = QPushButton("ANALYZE SELECTED FILE")
        self.analyze_btn.setFixedHeight(50)
        self.analyze_btn.clicked.connect(lambda: self._handle_file_double_click(self.tree_view.currentIndex()))

        layout.addLayout(header)
        layout.addWidget(self.tree_view)
        layout.addWidget(self.analyze_btn)

    def _build_profile_page(self):
        layout = QVBoxLayout(self.profile_page)
        layout.setContentsMargins(80, 60, 80, 60)
        layout.setSpacing(30)
        
        header = QHBoxLayout()
        title = QLabel("USER PROFILE")
        title.setStyleSheet(f"color: {ACCENT}; font-size: 32px; font-weight: 900; letter-spacing: 1px;")
        header.addWidget(title)
        header.addStretch()
        
        back_btn = QPushButton("✕")
        back_btn.setFixedSize(40, 40)
        back_btn.setObjectName("IconButton")
        back_btn.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        header.addWidget(back_btn)
        
        card = QFrame()
        card.setStyleSheet(f"background: {BG_CARD}; border: 1px solid {BORDER_COLOR}; border-radius: 25px; padding: 40px;")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)
        
        self.profile_name = QLabel("Name: Loading...")
        self.profile_email = QLabel("Email: Loading...")
        self.profile_plan = QLabel("Plan: Loading...")
        self.profile_expiry = QLabel("Expires: Loading...")
        
        for lbl in [self.profile_name, self.profile_email, self.profile_plan, self.profile_expiry]:
            lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 18px; border: none; font-family: 'Segoe UI';")
            card_layout.addWidget(lbl)
            
        layout.addLayout(header)
        layout.addWidget(card)
        layout.addStretch()
        
        logout_btn = QPushButton("🚪 LOGOUT FROM SYSTEM")
        logout_btn.setFixedHeight(55)
        logout_btn.setStyleSheet("background: #1a0505; color: #ef4444; border: 1px solid #301010; border-radius: 14px; font-weight: 800; font-size: 13px;")
        logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout_btn)

    def update_profile_info(self, data):
        self.profile_name.setText(f"Name: {data.get('first_name', '')} {data.get('last_name', '')}")
        self.profile_email.setText(f"Email: {data.get('email', '')}")
        self.profile_plan.setText(f"Plan: {data.get('plan', '').upper()}")
        expiry = data.get('plan_expires_at', 'N/A')
        self.profile_expiry.setText(f"Expires: {expiry[:10] if expiry else 'N/A'}")

    def handle_submission(self):
        text = self.input_field.text().strip()
        if text:
            self.chat_display.append(USER_MSG_HTML.format(content=text))
            self.input_field.clear()
            self.chat_history.append({"role": "user", "content": text})
            self.submission_requested.emit(text)

    def start_ai_response(self):
        self.chat_display.append(AI_MSG_HTML.format(content="<span id='streaming'>...</span>"))
        self.chat_history.append({"role": "model", "content": ""})

    def display_ai_chunk(self, chunk):
        # Esta función ahora solo actualiza el contenido interno para el streaming suave
        self.chat_history[-1]["content"] += chunk
        html = markdown.markdown(self.chat_history[-1]["content"], extensions=['fenced_code', 'codehilite'])
        # Actualizamos el último bloque de mensaje AI
        self.load_chat_content(self.chat_history)

    def display_ai_response(self, text, is_new=True):
        if is_new: self.chat_history[-1]["content"] = text
        self.load_chat_content(self.chat_history)

    def load_chat_content(self, messages):
        self.chat_display.clear()
        self.chat_history = messages
        for msg in messages:
            if msg["role"] == "user":
                self.chat_display.append(USER_MSG_HTML.format(content=msg["content"]))
            else:
                html = markdown.markdown(msg["content"], extensions=['fenced_code', 'codehilite'])
                self.chat_display.append(AI_MSG_HTML.format(content=html))

    def _build_tools_menu(self):
        self.tools_menu = QMenu(self)
        self.tools_menu.setStyleSheet(f"QMenu {{ background-color: #111; border: 1px solid {BORDER_COLOR}; border-radius: 12px; color: white; padding: 8px; }} QMenu::item {{ padding: 10px 25px; border-radius: 8px; font-size: 13px; }} QMenu::item:selected {{ background-color: {ACCENT}; color: black; font-weight: bold; }}")
        screen_read = QAction("📸 Read Screen", self)
        screen_read.triggered.connect(lambda: self.tool_selected.emit("screen_read"))
        clip_analyze = QAction("📋 Clipboard", self)
        clip_analyze.triggered.connect(lambda: self.tool_selected.emit("clipboard"))
        self.tools_menu.addAction(screen_read)
        self.tools_menu.addAction(clip_analyze)

    def _show_tools_menu(self):
        self.tools_menu.exec(self.tools_btn.mapToGlobal(QPoint(0, -self.tools_menu.sizeHint().height() - 15)))

    def apply_styles(self): self.setStyleSheet(OMNI_STYLESHEET)
    
    def _handle_row_changed(self, row):
        for i in range(self.chat_list.count()):
            item = self.chat_list.item(i); widget = self.chat_list.itemWidget(item)
            if isinstance(widget, ChatItemWidget): widget.set_selected(i == row)

    def update_chat_list(self, titles, current_index):
        self.chat_list.blockSignals(True); self.chat_list.clear()
        for i, t in enumerate(titles):
            item = QListWidgetItem(self.chat_list); widget = ChatItemWidget(t)
            widget.delete_clicked.connect(lambda idx=i: self.chat_delete_requested.emit(idx))
            widget.rename_requested.connect(lambda name, idx=i: self.chat_rename_requested.emit(idx, name))
            item.setSizeHint(QSize(0, 52)); self.chat_list.addItem(item)
            self.chat_list.setItemWidget(item, widget); widget.set_selected(i == current_index)
        self.chat_list.setCurrentRow(current_index); self.chat_list.blockSignals(False)

    def toggle_sidebar(self):
        target = 280 if not self.sidebar_expanded else 0
        self.anim = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.anim.setDuration(400); self.anim.setEndValue(target); self.anim.setEasingCurve(QEasingCurve.Type.OutQuart)
        self.anim2 = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.anim2.setDuration(400); self.anim2.setEndValue(target); self.anim2.setEasingCurve(QEasingCurve.Type.OutQuart)
        self.anim.start(); self.anim2.start(); self.sidebar_expanded = not self.sidebar_expanded

    def _show_info_modal(self): OmniModal(self).exec()
    
    def mousePressEvent(self, event):
        # Permitir arrastrar desde el handle o cualquier parte vacía de la barra superior
        if event.button() == Qt.MouseButton.LeftButton:
            # Si el click es en la parte superior (barra de herramientas)
            if event.position().y() < 65: 
                self._drag_pos = event.globalPosition().toPoint()
                event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = QPoint()
        event.accept()
    
    def show_and_focus(self):
        if not self.isVisible():
            self.setWindowOpacity(0.0); self.show()
            geo = self.geometry()
            self.op_anim = QPropertyAnimation(self, b"windowOpacity")
            self.op_anim.setDuration(300); self.op_anim.setStartValue(0.0); self.op_anim.setEndValue(1.0)
            self.pos_anim = QPropertyAnimation(self, b"pos")
            self.pos_anim.setDuration(400); self.pos_anim.setStartValue(QPoint(geo.x(), geo.y() + 40)); self.pos_anim.setEndValue(geo.topLeft()); self.pos_anim.setEasingCurve(QEasingCurve.Type.OutQuart)
            self.op_anim.start(); self.pos_anim.start()
        else: self.show()
        self.raise_(); self.activateWindow(); self.input_field.setFocus()

    def center_window(self):
        geo = self.screen().availableGeometry()
        self.move((geo.width() - self.width()) // 2, (geo.height() - self.height()) // 2)

    def _handle_file_double_click(self, index):
        if not self.file_model.isDir(index):
            self.file_selected.emit(self.file_model.filePath(index))
            self.stack.setCurrentIndex(2)
