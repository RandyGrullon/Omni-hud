# main.py
import sys
import os
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from gui import OmniUI
from ai_engine import AIWorker
from voice_engine import VoiceWorker
from utils import GlobalHotkeyHandler, enable_ghost_mode
from history_manager import load_chats, save_chats
from document_processor import DocumentWorker
from constants import MAX_RECORDING_DURATION
from dotenv import load_dotenv
from supabase import create_client, Client

class OmniController:
    def __init__(self):
        if os.name == 'nt':
            try: ctypes.windll.ole32.CoInitialize(None)
            except: pass

        QApplication.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)
        self.app = QApplication(sys.argv)
        self.ui = OmniUI()
        
        load_dotenv()
        
        # Conexión Supabase
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key) if url and key else None
        
        enable_ghost_mode(self.ui.winId())
        
        self.chats = load_chats()
        self.current_chat_index = 0
        self.user_session = None
        
        self.ai_worker = None
        self.voice_worker = None
        self.doc_worker = None
        
        self._setup_hotkeys()
        self._connect_signals()
        self._check_initial_state()
        self._refresh_ui_tabs()

    def _setup_hotkeys(self):
        self.hotkey_handler = GlobalHotkeyHandler()
        self.hotkey_handler.hotkey_pressed.connect(self.ui.show_and_focus)
        self.hotkey_handler.voice_hotkey_pressed.connect(lambda: self.handle_voice_toggle("system"))
        self.hotkey_handler.mic_hotkey_pressed.connect(lambda: self.handle_voice_toggle("mic"))

    def _connect_signals(self):
        self.ui.submission_requested.connect(self.process_ai_query)
        self.ui.config_saved.connect(self.save_configuration)
        self.ui.tab_changed.connect(self.switch_chat)
        self.ui.tab_added.connect(self.add_new_chat)
        self.ui.tab_closed.connect(self.remove_chat)
        self.ui.file_selected.connect(self.start_document_processing)
        self.ui.login_requested.connect(self.handle_login)

    def handle_login(self, email, password):
        """ Valida credenciales con Supabase Auth y verifica plan activo. """
        if not self.supabase:
            self.ui.login_error.setText("Error: Supabase no configurado en .env")
            return

        try:
            # 1. Autenticar con Supabase Auth
            res = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
            user_id = res.user.id
            
            # 2. Verificar suscripción en la tabla 'profiles'
            profile_res = self.supabase.table("profiles").select("*").eq("id", user_id).single().execute()
            profile = profile_res.data
            
            if not profile or not profile.get("purchase_id"):
                self.ui.login_error.setText("ACCESO DENEGADO: Requiere Plan Activo.")
                return

            # 3. Acceso concedido
            self.user_session = res.session
            # Guardar sesión de forma básica (email) para persistencia simple
            with open(".auth_token", "w") as f: f.write(email)
            
            # Si tiene sesión, ir a config o chat
            self._check_initial_state()
        except Exception as e:
            self.ui.login_error.setText(f"Login fallido: {str(e)}")

    def _check_initial_state(self):
        # 1. Verificar si está logueado
        if not os.path.exists(".auth_token"):
            self.ui.stack.setCurrentIndex(0) # Pantalla Login
            return

        # 2. Verificar API Key
        if not os.getenv("GROQ_API_KEY"):
            self.ui.stack.setCurrentIndex(1) # Pantalla Config
        else:
            self.ui.stack.setCurrentIndex(2) # Pantalla Chat
            self.switch_chat(0)

    def _refresh_ui_tabs(self):
        self.ui.update_tabs([c["title"] for c in self.chats], self.current_chat_index)

    def switch_chat(self, index):
        if 0 <= index < len(self.chats):
            self.current_chat_index = index
            self.ui.load_chat_content(self.chats[index]["messages"])

    def add_new_chat(self):
        if len(self.chats) < 3:
            new_id = max([c["id"] for c in self.chats]) + 1 if self.chats else 0
            self.chats.append({"id": new_id, "title": f"Chat {new_id+1}", "messages": []})
            self.current_chat_index = len(self.chats) - 1
            save_chats(self.chats); self._refresh_ui_tabs(); self.switch_chat(self.current_chat_index)

    def remove_chat(self, index):
        if len(self.chats) > 1:
            self.chats.pop(index)
            self.current_chat_index = min(self.current_chat_index, len(self.chats)-1)
            save_chats(self.chats); self._refresh_ui_tabs(); self.switch_chat(self.current_chat_index)

    def handle_voice_toggle(self, source="system"):
        if self.voice_worker and self.voice_worker.isRunning():
            self.voice_worker.stop_recording()
            return
        self.voice_worker = VoiceWorker(max_duration=MAX_RECORDING_DURATION, source_type=source)
        color = "#FF003C" if source == "system" else "#FFFF00"
        self.voice_worker.listening_status.connect(lambda active: self._update_ui_style(active, color))
        self.voice_worker.transcription_ready.connect(lambda t: (self.ui.input_field.setText(t), self.ui.input_field.setFocus()))
        self.voice_worker.start()

    def _update_ui_style(self, active, color):
        c = color if active else "#00FF41"
        self.ui.container.setStyleSheet(f"QWidget#MainContainer {{ border: 2px solid {c}; }}")

    def process_ai_query(self, prompt: str):
        if self.ai_worker and self.ai_worker.isRunning(): return
        self.chats[self.current_chat_index]["messages"] = self.ui.chat_history
        save_chats(self.chats)
        self.ai_worker = AIWorker(prompt, self.ui.chat_history[:-1])
        self.ai_worker.response_ready.connect(self.handle_ai_response)
        self.ai_worker.error_occurred.connect(lambda e: self.ui.display_ai_response(f"<span style='color:red;'>{e}</span>"))
        self.ai_worker.start()

    def handle_ai_response(self, response):
        self.ui.display_ai_response(response)
        self.chats[self.current_chat_index]["messages"] = self.ui.chat_history
        save_chats(self.chats)

    def start_document_processing(self, file_path):
        if self.doc_worker and self.doc_worker.isRunning(): return
        self.doc_worker = DocumentWorker(file_path)
        self.doc_worker.extraction_ready.connect(lambda f, c: (self.ui.chat_display.append(f"<b>[SISTEMA] {f} listo.</b><br>"), self.ui.input_field.setText("Analiza: "), self.ui.chat_history.append({"role": "user", "content": f"[DOC: {f}]\n{c}"})))
        self.doc_worker.start()

    def save_configuration(self, api_key):
        with open(".env", "a") as f: f.write(f"\nGROQ_API_KEY={api_key}")
        os.execl(sys.executable, sys.executable, *sys.argv)

    def run(self):
        self.ui.show_and_focus()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    controller = OmniController()
    controller.run()
