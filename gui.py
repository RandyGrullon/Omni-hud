# gui.py
import markdown
import re
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextBrowser, QLineEdit, QFrame, QLabel, 
                             QPushButton, QStackedWidget, QApplication, QTabBar, QHBoxLayout, 
                             QTreeView, QHeaderView, QDialog)
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QUrl, QDir
from styles import OMNI_STYLESHEET, USER_MSG_HTML, AI_MSG_HTML, CODE_BLOCK_STYLE, HELP_MSG_HTML
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_FLAGS

class OmniModal(QDialog):
    """ Modal informativo con estética Cyberpunk. """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        container = QFrame()
        container.setStyleSheet("background-color: #111; border: 1px solid #00FF41; border-radius: 10px;")
        c_layout = QVBoxLayout(container)
        
        title = QLabel("OMNI_SYSTEM_CORE")
        title.setStyleSheet("color: #00FF41; font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        
        info = QLabel(
            "Omni is a high-performance HUD designed for engineers.\n\n"
            "• Invisible to capture software\n"
            "• Real-time system audio capture\n"
            "• Local neural persistence\n"
            "• Groq LPU powered"
        )
        info.setStyleSheet("color: #AAA; font-size: 12px;")
        info.setWordWrap(True)
        
        close_btn = QPushButton("CLOSE_INTERFACE")
        close_btn.clicked.connect(self.close)
        
        c_layout.addWidget(title); c_layout.addWidget(info); c_layout.addStretch(); c_layout.addWidget(close_btn)
        layout.addWidget(container)

class OmniUI(QWidget):
    submission_requested = pyqtSignal(str)
    chat_cleared = pyqtSignal()
    voice_requested = pyqtSignal()
    config_saved = pyqtSignal(str)
    tab_changed = pyqtSignal(int)
    tab_closed = pyqtSignal(int)
    tab_added = pyqtSignal()
    file_selected = pyqtSignal(str)
    login_requested = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.chat_history = []
        self._drag_pos = QPoint()
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        self.setWindowFlags(WINDOW_FLAGS)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(900, 700)
        self.center_window()

        self.main_layout = QVBoxLayout(self); self.container = QFrame()
        self.container.setObjectName("MainContainer"); self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        
        self._setup_drag_handle()
        self._setup_tabs()
        self._setup_stacked_pages()
        
        self.main_layout.addWidget(self.container)

    def _setup_drag_handle(self):
        self.drag_handle = QFrame(); self.drag_handle.setObjectName("DragHandle")
        self.drag_handle.setCursor(Qt.CursorShape.SizeAllCursor); self.drag_handle.setFixedHeight(12)
        self.container_layout.addWidget(self.drag_handle)

    def _setup_tabs(self):
        self.tabs_container = QHBoxLayout(); self.tabs_container.setContentsMargins(15, 5, 15, 0)
        self.tab_bar = QTabBar(); self.tab_bar.setTabsClosable(True)
        self.tab_bar.currentChanged.connect(self.tab_changed.emit); self.tab_bar.tabCloseRequested.connect(self.tab_closed.emit)
        
        self.add_tab_btn = QPushButton("+"); self.add_tab_btn.setFixedSize(24, 24)
        self.add_tab_btn.setStyleSheet("background-color: #1a1a1a; color: #00FF41; border: 1px solid #333;")
        self.add_tab_btn.clicked.connect(self.tab_added.emit)
        
        # Botón Info
        self.info_btn = QPushButton("ⓘ"); self.info_btn.setFixedSize(24, 24)
        self.info_btn.setStyleSheet("background-color: transparent; color: #555; border: none; font-size: 16px;")
        self.info_btn.clicked.connect(self._show_info_modal)
        
        self.tabs_container.addWidget(self.tab_bar); self.tabs_container.addWidget(self.add_tab_btn); 
        self.tabs_container.addStretch(); self.tabs_container.addWidget(self.info_btn)
        self.container_layout.addLayout(self.tabs_container)

    def _show_info_modal(self):
        modal = OmniModal(self)
        modal.exec()

    def _setup_stacked_pages(self):
        self.stack = QStackedWidget()
        self.login_page = QWidget(); self._build_login_page()
        self.config_page = QWidget(); self._build_config_page()
        self.chat_page = QWidget(); self._build_chat_page()
        self.file_page = QWidget(); self._build_file_page()
        self.stack.addWidget(self.login_page); self.stack.addWidget(self.config_page); 
        self.stack.addWidget(self.chat_page); self.stack.addWidget(self.file_page)
        self.container_layout.addWidget(self.stack)

    def _build_login_page(self):
        layout = QVBoxLayout(self.login_page); layout.setContentsMargins(80, 80, 80, 80)
        title = QLabel("NEURAL_ID AUTHENTICATION")
        self.email_input = QLineEdit(); self.email_input.setPlaceholderText("PROTOCOL_EMAIL")
        self.pass_input = QLineEdit(); self.pass_input.setPlaceholderText("SECURITY_KEY"); self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        btn = QPushButton("AUTHORIZE ACCESS")
        btn.clicked.connect(lambda: self.login_requested.emit(self.email_input.text(), self.pass_input.text()))
        self.login_error = QLabel(""); self.login_error.setStyleSheet("color: red; font-size: 10px;")
        layout.addWidget(title); layout.addWidget(self.email_input); layout.addWidget(self.pass_input); 
        layout.addWidget(self.login_error); layout.addWidget(btn); layout.addStretch()

    def _build_config_page(self):
        layout = QVBoxLayout(self.config_page); layout.setContentsMargins(60, 60, 60, 60); layout.setSpacing(20)
        
        title = QLabel("CORE_ENGINE INITIALIZATION")
        title.setStyleSheet("color: #00FF41; font-size: 24px; font-weight: bold; letter-spacing: 2px;")
        
        description = QLabel(
            "To activate the Neural Engine, you need a Groq LPU API Key.\n\n"
            "1. Visit the Groq Console (link below)\n"
            "2. Generate a new API Key\n"
            "3. Paste it here and click INITIALIZE"
        )
        description.setStyleSheet("color: #888; font-size: 13px; line-height: 1.5;")
        description.setWordWrap(True)

        link_btn = QPushButton("GET_FREE_API_KEY (console.groq.com)")
        link_btn.setStyleSheet("color: #00FF41; text-align: left; border: none; background: transparent; font-size: 11px; text-decoration: underline;")
        link_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        link_btn.clicked.connect(lambda: os.startfile("https://console.groq.com/keys"))

        self.key_input = QLineEdit(); self.key_input.setPlaceholderText("PASTE_GROQ_API_KEY_HERE")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password) # Por seguridad
        
        btn = QPushButton("INITIALIZE_SYSTEM")
        btn.setFixedHeight(50)
        btn.clicked.connect(lambda: self.config_saved.emit(self.key_input.text().strip()))
        
        layout.addStretch()
        layout.addWidget(title); layout.addWidget(description); layout.addWidget(link_btn)
        layout.addWidget(self.key_input); layout.addWidget(btn)
        layout.addStretch()

    def _build_chat_page(self):
        layout = QVBoxLayout(self.chat_page); layout.setContentsMargins(10, 2, 10, 10)
        self.chat_display = QTextBrowser(); self.chat_display.setOpenExternalLinks(False)
        self.chat_display.anchorClicked.connect(self.handle_copy_click)
        input_bar = QHBoxLayout(); input_bar.setSpacing(5)
        self.clip_btn = QPushButton("📎"); self.clip_btn.setFixedSize(35, 35)
        self.clip_btn.setStyleSheet("background-color: #1a1a1a; color: #00FF41; border: 1px solid #333; border-radius: 6px;")
        self.clip_btn.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        self.input_field = QLineEdit(); self.input_field.setPlaceholderText("> Query system or use /help..."); self.input_field.setFixedHeight(35)
        self.input_field.returnPressed.connect(self.handle_submission)
        input_bar.addWidget(self.clip_btn); input_bar.addWidget(self.input_field)
        layout.addWidget(self.chat_display); layout.addLayout(input_bar)

    def _build_file_page(self):
        layout = QVBoxLayout(self.file_page); layout.setContentsMargins(15, 15, 15, 15)
        header = QHBoxLayout(); header.addWidget(QLabel("FILE_EXPLORER")); header.addStretch()
        btn = QPushButton("BACK"); btn.setFixedWidth(80); btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        header.addWidget(btn)
        self.file_model = QFileSystemModel(); self.file_model.setRootPath(QDir.rootPath())
        self.file_model.setNameFilters(["*.docx", "*.pdf", "*.xlsx", "*.xls"])
        self.tree_view = QTreeView(); self.tree_view.setModel(self.file_model)
        self.tree_view.setRootIndex(self.file_model.index(QDir.homePath())); self.tree_view.setColumnWidth(0, 300)
        self.tree_view.doubleClicked.connect(self._handle_file_double_click)
        self.tree_view.setColumnHidden(1, True); self.tree_view.setColumnHidden(2, True); self.tree_view.setColumnHidden(3, True)
        layout.addLayout(header); layout.addWidget(self.tree_view)

    def _handle_file_double_click(self, index):
        if not self.file_model.isDir(index):
            self.file_selected.emit(self.file_model.filePath(index)); self.stack.setCurrentIndex(2)

    def handle_submission(self):
        text = self.input_field.text().strip()
        if not text: return
        
        # Interceptar comandos del sistema
        if text == "/help":
            self.show_help_message()
            self.input_field.clear()
            return

        self.chat_display.append(USER_MSG_HTML.format(content=text))
        self.input_field.clear(); self.chat_history.append({"role": "user", "content": text})
        self.submission_requested.emit(text)

    def show_help_message(self):
        help_content = (
            "<b>COMMANDS:</b><br>"
            "• <span style='color:white;'>/help</span> : Show this system guide.<br><br>"
            "<b>HOTKEYS (Global):</b><br>"
            "• <span style='color:white;'>Ctrl + Space</span> : Show/Hide HUD.<br>"
            "• <span style='color:white;'>Ctrl + Shift + R</span> : Capture System Audio (Red).<br>"
            "• <span style='color:white;'>Ctrl + Shift + M</span> : Capture Microphone (Yellow).<br><br>"
            "<b>UI SHORTCUTS:</b><br>"
            "• <span style='color:white;'>Esc</span> : Hide or Go Back.<br>"
            "• <span style='color:white;'>Ctrl + L</span> : Reset Chat Context."
        )
        self.chat_display.append(HELP_MSG_HTML.format(content=help_content))
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    def display_ai_response(self, text, is_new=True):
        md_ext = ['fenced_code', 'codehilite', 'nl2br']
        md_cfg = {'codehilite': {'css_class': 'code-highlight', 'guess_lang': True, 'use_pygments': True}}
        html = markdown.markdown(text, extensions=md_ext, extension_configs=md_cfg)
        def _add_btn(m):
            c = re.sub(r'<[^>]+>', '', m.group(1)).replace('&quot;', '"').replace('&apos;', "'")
            return f"<a href='copy:{c}' class='copy-btn'>[COPY]</a>{m.group(0)}"
        processed = re.sub(r'<div class="code-highlight"><pre>(.*?)</pre></div>', _add_btn, html, flags=re.DOTALL)
        if processed == html: processed = re.sub(r'<pre><code>(.*?)</code></pre>', _add_btn, html, flags=re.DOTALL)
        self.chat_display.append(f"<style>{CODE_BLOCK_STYLE}</style>" + AI_MSG_HTML.format(content=processed))
        if is_new: self.chat_history.append({"role": "model", "content": text})
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    def update_tabs(self, titles, current_index):
        self.tab_bar.blockSignals(True)
        while self.tab_bar.count() > 0:
            self.tab_bar.removeTab(0)
        for t in titles:
            self.tab_bar.addTab(t)
        self.tab_bar.setCurrentIndex(current_index)
        self.tab_bar.blockSignals(False)
        self.add_tab_btn.setEnabled(len(titles) < 3)

    def load_chat_content(self, messages):
        self.chat_display.clear(); self.chat_history = messages
        for msg in messages:
            if msg["role"] == "user": self.chat_display.append(USER_MSG_HTML.format(content=msg["content"]))
            else: self.display_ai_response(msg["content"], is_new=False)

    def handle_copy_click(self, url: QUrl):
        if url.toString().startswith("copy:"): QApplication.clipboard().setText(url.toString()[5:])
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drag_handle.underMouse():
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft(); event.accept()
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self._drag_pos); event.accept()
    def mouseReleaseEvent(self, event): self._drag_pos = QPoint()
    def apply_styles(self): self.setStyleSheet(OMNI_STYLESHEET)
    def center_window(self):
        geo = self.screen().availableGeometry()
        self.move((geo.width() - self.width()) // 2, (geo.height() - self.height()) // 2)
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if self.stack.currentIndex() >= 2: self.stack.setCurrentIndex(2)
            else: self.hide()
        elif event.key() == Qt.Key.Key_L and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.chat_display.clear(); self.chat_history = []; self.chat_cleared.emit()
        super().keyPressEvent(event)
    def focusOutEvent(self, event):
        if self._drag_pos.isNull(): self.hide()
        super().focusOutEvent(event)
    def show_and_focus(self):
        self.show(); self.raise_(); self.activateWindow()
        idx = self.stack.currentIndex()
        if idx == 0: self.email_input.setFocus()
        elif idx == 1: self.key_input.setFocus()
        else: self.input_field.setFocus()
