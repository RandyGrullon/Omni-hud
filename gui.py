# gui.py
import markdown
import re
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextBrowser, QLineEdit, QFrame, QLabel, 
                             QPushButton, QStackedWidget, QApplication, QTabBar, QHBoxLayout, 
                             QTreeView, QHeaderView, QDialog, QMenu, QScrollArea, QListWidget, QListWidgetItem)
from PyQt6.QtGui import QFileSystemModel, QAction, QColor
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QUrl, QDir, QSize, QPropertyAnimation, QEasingCurve
from styles import OMNI_STYLESHEET, USER_MSG_HTML, AI_MSG_HTML, CODE_BLOCK_STYLE, HELP_MSG_HTML
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_FLAGS

class OmniModal(QDialog):
    """ Modal informativo con estética Cyberpunk profesional. """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(450, 480)
        
        layout = QVBoxLayout(self)
        container = QFrame()
        container.setStyleSheet("background-color: #050505; border: 1px solid #00FF41; border-radius: 20px;")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(30, 30, 30, 30)
        c_layout.setSpacing(15)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("OMNI_SYSTEM_CORE"); title.setStyleSheet("color: #00FF41; font-weight: 900; font-size: 18px; border: none;")
        ver = QLabel("v1.0.2"); ver.setStyleSheet("color: #333; font-weight: bold; font-size: 12px; border: none;")
        header.addWidget(title); header.addStretch(); header.addWidget(ver)
        
        description = QLabel("Advanced neural-link HUD for real-time information processing and LPU-powered AI interaction.")
        description.setStyleSheet("color: #888; font-size: 11px; border: none;")
        description.setWordWrap(True)

        # Hotkeys Box
        hk_box = QFrame(); hk_box.setStyleSheet("background-color: #0a0a0a; border: 1px solid #111; border-radius: 10px;")
        hk_layout = QVBoxLayout(hk_box)
        hk_title = QLabel("GLOBAL_CONTROLS"); hk_title.setStyleSheet("color: #00FF41; font-size: 9px; font-weight: bold; border: none; margin-bottom: 5px;")
        hk_layout.addWidget(hk_title)
        
        hks = [("CTRL + SPACE", "Toggle HUD Visibility"), ("CTRL + SHIFT + R", "System Audio Capture"), 
               ("CTRL + SHIFT + M", "Microphone Capture"), ("ESC", "Navigate Back / Hide")]
        for key, desc in hks:
            row = QHBoxLayout()
            k_lbl = QLabel(key); k_lbl.setStyleSheet("color: white; font-size: 10px; font-weight: bold; border: none;")
            d_lbl = QLabel(desc); d_lbl.setStyleSheet("color: #555; font-size: 10px; border: none;")
            row.addWidget(k_lbl); row.addStretch(); row.addWidget(d_lbl)
            hk_layout.addLayout(row)

        # Links
        links = QHBoxLayout()
        web_btn = QPushButton("OFFICIAL_WEB"); web_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        web_btn.setStyleSheet("color: #00FF41; font-size: 10px; border: none; text-decoration: underline; background: transparent;")
        web_btn.clicked.connect(lambda: os.startfile("https://omni-web-nine.vercel.app"))
        links.addWidget(web_btn); links.addStretch()

        close_btn = QPushButton("ACKNOWLEDGE_SYSTEM"); close_btn.setFixedHeight(45)
        close_btn.setStyleSheet("background-color: #00FF41; color: black; font-weight: 900; border-radius: 10px; font-size: 12px;")
        close_btn.clicked.connect(self.close)
        
        c_layout.addLayout(header); c_layout.addWidget(description); c_layout.addWidget(hk_box); c_layout.addLayout(links); c_layout.addStretch(); c_layout.addWidget(close_btn)
        layout.addWidget(container)

class ChatItemWidget(QWidget):
    delete_clicked = pyqtSignal()
    def __init__(self, title, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self); layout.setContentsMargins(10, 5, 10, 5); layout.setSpacing(10)
        self.label = QLabel(title); self.label.setStyleSheet("color: inherit; font-size: 12px; background: transparent; border: none;")
        self.del_btn = QPushButton("×"); self.del_btn.setFixedSize(20, 20)
        self.del_btn.setStyleSheet("QPushButton { background: transparent; color: #555; font-size: 16px; font-weight: bold; border: none; } QPushButton:hover { color: #ff4444; }")
        self.del_btn.clicked.connect(self.delete_clicked.emit)
        layout.addWidget(self.label, 1); layout.addWidget(self.del_btn)

class OmniUI(QWidget):
    submission_requested = pyqtSignal(str)
    chat_cleared = pyqtSignal()
    config_saved = pyqtSignal(str)
    chat_selected = pyqtSignal(int)
    chat_delete_requested = pyqtSignal(int)
    new_chat_requested = pyqtSignal()
    file_selected = pyqtSignal(str)
    login_requested = pyqtSignal(str, str)
    tool_selected = pyqtSignal(str)
    update_requested = pyqtSignal()
    logout_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.chat_history = []; self._drag_pos = QPoint(); self.sidebar_expanded = False
        self.init_ui(); self.apply_styles()

    def init_ui(self):
        self.setWindowFlags(WINDOW_FLAGS); self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(950, 700); self.center_window()
        self.main_layout = QHBoxLayout(self); self.main_layout.setContentsMargins(0, 0, 0, 0); self.main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame(); self.sidebar.setObjectName("Sidebar"); self.sidebar.setFixedWidth(0)
        self.sidebar_layout = QVBoxLayout(self.sidebar); self.sidebar_layout.setContentsMargins(10, 20, 10, 20); self.sidebar_layout.setSpacing(15)
        side_title = QLabel("OMNI_CHATS"); side_title.setStyleSheet("color: #00FF41; font-weight: bold; font-size: 10px; letter-spacing: 2px;")
        self.chat_list = QListWidget(); self.chat_list.setObjectName("ChatList")
        self.new_chat_btn = QPushButton("+ NEW_CHAT"); self.new_chat_btn.setObjectName("SideBtn")
        self.new_chat_btn.clicked.connect(self.new_chat_requested.emit)
        self.profile_btn = QPushButton("👤 MY_PROFILE"); self.profile_btn.setObjectName("SideBtn")
        self.profile_btn.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        self.logout_btn = QPushButton("🚪 LOGOUT"); self.logout_btn.setObjectName("SideBtnLogout")
        self.logout_btn.clicked.connect(self.logout_requested.emit)
        self.sidebar_layout.addWidget(side_title); self.sidebar_layout.addWidget(self.chat_list)
        self.sidebar_layout.addWidget(self.new_chat_btn); self.sidebar_layout.addStretch()
        self.sidebar_layout.addWidget(self.profile_btn); self.sidebar_layout.addWidget(self.logout_btn)

        # Content
        self.content_area = QFrame(); self.content_area.setObjectName("MainContainer")
        self.content_layout = QVBoxLayout(self.content_area); self.content_layout.setContentsMargins(0, 0, 0, 0); self.content_layout.setSpacing(0)
        
        self.top_bar = QHBoxLayout(); self.top_bar.setContentsMargins(10, 5, 15, 5)
        self.hamburger_btn = QPushButton("☰"); self.hamburger_btn.setFixedSize(35, 35)
        self.hamburger_btn.setStyleSheet("background: transparent; color: #00FF41; font-size: 20px; border: none;")
        self.hamburger_btn.clicked.connect(self.toggle_sidebar)
        self.drag_handle = QFrame(); self.drag_handle.setObjectName("DragHandle"); self.drag_handle.setFixedHeight(35)
        self.info_btn = QPushButton("ⓘ"); self.info_btn.setFixedSize(24, 24); self.info_btn.setStyleSheet("background: transparent; color: #555; border: none; font-size: 16px;")
        self.info_btn.clicked.connect(self._show_info_modal)
        self.close_app_btn = QPushButton("×"); self.close_app_btn.setFixedSize(35, 35)
        self.close_app_btn.setStyleSheet("background: transparent; color: #555; font-size: 22px; border: none; font-weight: bold;")
        self.close_app_btn.clicked.connect(QApplication.quit)
        self.top_bar.addWidget(self.hamburger_btn); self.top_bar.addWidget(self.drag_handle, 1); self.top_bar.addWidget(self.info_btn); self.top_bar.addWidget(self.close_app_btn)
        
        self.stack = QStackedWidget()
        self.login_page = QWidget(); self._build_login_page()
        self.config_page = QWidget(); self._build_config_page()
        self.chat_page = QWidget(); self._build_chat_page()
        self.file_page = QWidget(); self._build_file_page()
        self.profile_page = QWidget(); self._build_profile_page()
        for p in [self.login_page, self.config_page, self.chat_page, self.file_page, self.profile_page]: self.stack.addWidget(p)
        
        self.content_layout.addLayout(self.top_bar); self.content_layout.addWidget(self.stack)
        self.main_layout.addWidget(self.sidebar); self.main_layout.addWidget(self.content_area)

    def _show_info_modal(self):
        modal = OmniModal(self); modal.exec()

    def toggle_sidebar(self):
        target = 240 if not self.sidebar_expanded else 0
        self.anim = QPropertyAnimation(self.sidebar, b"minimumWidth"); self.anim.setDuration(300); self.anim.setEndValue(target); self.anim.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.anim2 = QPropertyAnimation(self.sidebar, b"maximumWidth"); self.anim2.setDuration(300); self.anim2.setEndValue(target); self.anim2.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.anim.start(); self.anim2.start(); self.sidebar_expanded = not self.sidebar_expanded

    def update_chat_list(self, titles, current_index):
        self.chat_list.clear()
        for i, t in enumerate(titles):
            item = QListWidgetItem(self.chat_list); widget = ChatItemWidget(t)
            widget.delete_clicked.connect(lambda idx=i: self.chat_delete_requested.emit(idx))
            item.setSizeHint(QSize(0, 45)); self.chat_list.addItem(item); self.chat_list.setItemWidget(item, widget)
        self.chat_list.setCurrentRow(current_index)

    def _build_login_page(self):
        layout = QVBoxLayout(self.login_page); layout.setContentsMargins(80, 80, 80, 80)
        title = QLabel("NEURAL_ID AUTHENTICATION"); title.setStyleSheet("color: #00FF41; font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        self.email_input = QLineEdit(); self.email_input.setPlaceholderText("PROTOCOL_EMAIL")
        self.pass_input = QLineEdit(); self.pass_input.setPlaceholderText("SECURITY_KEY"); self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_btn = QPushButton("AUTHORIZE ACCESS"); self.login_btn.setFixedHeight(45)
        self.login_btn.clicked.connect(lambda: self.login_requested.emit(self.email_input.text(), self.pass_input.text()))
        self.login_error = QLabel(""); self.login_error.setStyleSheet("color: red; font-size: 10px;")
        layout.addWidget(title); layout.addWidget(self.email_input); layout.addWidget(self.pass_input); layout.addWidget(self.login_error); layout.addWidget(self.login_btn); layout.addStretch()

    def set_login_loading(self, loading: bool):
        if loading: self.login_btn.setText("VALIDATING_IDENTITY..."); self.login_btn.setEnabled(False)
        else: self.login_btn.setText("AUTHORIZE ACCESS"); self.login_btn.setEnabled(True)

    def _build_config_page(self):
        layout = QVBoxLayout(self.config_page); layout.setContentsMargins(60, 60, 60, 60); layout.setSpacing(20)
        title = QLabel("CORE_ENGINE INITIALIZATION"); title.setStyleSheet("color: #00FF41; font-size: 24px; font-weight: bold;")
        self.key_input = QLineEdit(); self.key_input.setPlaceholderText("PASTE_GROQ_API_KEY_HERE"); self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        btn = QPushButton("INITIALIZE_SYSTEM"); btn.clicked.connect(lambda: self.config_saved.emit(self.key_input.text().strip()))
        self.update_btn = QPushButton("CHECK_FOR_UPDATES"); self.update_btn.setObjectName("SideBtn")
        self.update_btn.clicked.connect(lambda: self.update_requested.emit())
        layout.addWidget(title); layout.addWidget(self.key_input); layout.addWidget(btn); layout.addWidget(self.update_btn); layout.addStretch()

    def _build_chat_page(self):
        layout = QVBoxLayout(self.chat_page); layout.setContentsMargins(10, 2, 10, 10)
        self.chat_display = QTextBrowser(); self.chat_display.setOpenExternalLinks(False)
        input_bar = QHBoxLayout(); input_bar.setSpacing(5)
        self.clip_btn = QPushButton("📎"); self.clip_btn.setFixedSize(35, 35)
        self.clip_btn.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        self.tools_btn = QPushButton("+"); self.tools_btn.setFixedSize(35, 35)
        self._build_tools_menu(); self.tools_btn.clicked.connect(self._show_tools_menu)
        self.input_field = QLineEdit(); self.input_field.setPlaceholderText("> Query system..."); self.input_field.setFixedHeight(35)
        self.input_field.returnPressed.connect(self.handle_submission)
        input_bar.addWidget(self.clip_btn); input_bar.addWidget(self.tools_btn); input_bar.addWidget(self.input_field)
        layout.addWidget(self.chat_display); layout.addLayout(input_bar)

    def _build_file_page(self):
        layout = QVBoxLayout(self.file_page); layout.setContentsMargins(15, 15, 15, 15)
        header = QHBoxLayout(); header.addWidget(QLabel("FILE_EXPLORER")); header.addStretch()
        btn = QPushButton("BACK"); btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        header.addWidget(btn)
        self.file_model = QFileSystemModel(); self.file_model.setRootPath(QDir.rootPath())
        self.tree_view = QTreeView(); self.tree_view.setModel(self.file_model); self.tree_view.setRootIndex(self.file_model.index(QDir.homePath()))
        layout.addLayout(header); layout.addWidget(self.tree_view)

    def _build_profile_page(self):
        layout = QVBoxLayout(self.profile_page); layout.setContentsMargins(60, 60, 60, 60); layout.setSpacing(20)
        title = QLabel("USER_PROFILE_DATA"); title.setStyleSheet("color: #00FF41; font-size: 24px; font-weight: bold;")
        self.profile_name = QLabel("Name: Loading..."); self.profile_email = QLabel("Email: Loading...")
        self.profile_plan = QLabel("Plan: Loading..."); self.profile_expiry = QLabel("Expires: Loading...")
        for lbl in [self.profile_name, self.profile_email, self.profile_plan, self.profile_expiry]:
            lbl.setStyleSheet("color: white; font-size: 14px; font-family: 'Consolas';"); layout.addWidget(lbl)
        back_btn = QPushButton("BACK_TO_CHAT"); back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        layout.addStretch(); layout.addWidget(back_btn)

    def _build_tools_menu(self):
        self.tools_menu = QMenu(self)
        web_search = QAction("🌐 Search Internet", self); web_search.triggered.connect(lambda: self.tool_selected.emit("web_search"))
        screen_read = QAction("📸 Read Screen", self); screen_read.triggered.connect(lambda: self.tool_selected.emit("screen_read"))
        clip_analyze = QAction("📋 Clipboard", self); clip_analyze.triggered.connect(lambda: self.tool_selected.emit("clipboard"))
        self.tools_menu.addAction(web_search); self.tools_menu.addAction(screen_read); self.tools_menu.addAction(clip_analyze)

    def _show_tools_menu(self):
        self.tools_menu.exec(self.tools_btn.mapToGlobal(QPoint(0, -self.tools_menu.sizeHint().height())))

    def update_profile_info(self, data):
        self.profile_name.setText(f"Name: {data.get('first_name', '')} {data.get('last_name', '')}")
        self.profile_email.setText(f"Email: {data.get('email', '')}")
        self.profile_plan.setText(f"Plan: {data.get('plan', '').upper()}")
        expiry = data.get('plan_expires_at', 'N/A'); self.profile_expiry.setText(f"Expires: {expiry[:10] if expiry else 'N/A'}")

    def handle_submission(self):
        text = self.input_field.text().strip()
        if text:
            self.chat_display.append(USER_MSG_HTML.format(content=text))
            self.input_field.clear(); self.chat_history.append({"role": "user", "content": text})
            self.submission_requested.emit(text)

    def display_ai_response(self, text, is_new=True):
        html = markdown.markdown(text, extensions=['fenced_code', 'codehilite'])
        self.chat_display.append(AI_MSG_HTML.format(content=html))
        if is_new: self.chat_history.append({"role": "model", "content": text})

    def apply_styles(self): 
        self.setStyleSheet(OMNI_STYLESHEET + """
            #Sidebar { background-color: #080808; border-right: 1px solid #1a1a1a; }
            #ChatList { background: transparent; border: none; color: #888; }
            #ChatList::item:selected { background-color: #00FF41; color: black; font-weight: bold; border-radius: 5px; }
            #SideBtn { background-color: #111; color: #00FF41; border: 1px solid #222; border-radius: 8px; padding: 10px; font-size: 10px; font-weight: bold; }
            #SideBtnLogout { background-color: #1a0505; color: #ff4444; border: 1px solid #301010; border-radius: 8px; padding: 10px; font-size: 10px; font-weight: bold; }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drag_handle.underMouse():
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft(); event.accept()
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self._drag_pos); event.accept()
    def mouseReleaseEvent(self, event): self._drag_pos = QPoint()
    def show_and_focus(self): self.show(); self.raise_(); self.activateWindow(); self.input_field.setFocus()
    def center_window(self): geo = self.screen().availableGeometry(); self.move((geo.width() - self.width()) // 2, (geo.height() - self.height()) // 2)
    def load_chat_content(self, messages):
        self.chat_display.clear(); self.chat_history = messages
        for msg in messages:
            if msg["role"] == "user": self.chat_display.append(USER_MSG_HTML.format(content=msg["content"]))
            else: self.display_ai_response(msg["content"], is_new=False)
