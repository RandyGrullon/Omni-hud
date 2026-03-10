# main.py
import sys
import os
import ctypes
import requests
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QRect, QLockFile, QTimer
from gui import OmniUI
from ai_engine import AIWorker
from voice_engine import VoiceWorker
from utils import GlobalHotkeyHandler, enable_ghost_mode
from history_manager import load_chats, save_chats
from document_processor import DocumentWorker
from web_search import WebSearchWorker
from screen_processor import ScreenSelector, extract_text_from_area
from constants import MAX_RECORDING_DURATION
from dotenv import load_dotenv
from supabase import create_client, Client

VERSION = "1.0.2"
UPDATE_URL = "https://raw.githubusercontent.com/RandyGrullon/Omni-hud/main/version.json"

class OmniController:
    def __init__(self):
        if os.name == 'nt':
            try: ctypes.windll.ole32.CoInitialize(None)
            except: pass

        self.lock_file = QLockFile(os.path.join(os.path.expanduser("~"), "omni_hud.lock"))
        if not self.lock_file.tryLock(100): sys.exit(0)

        QApplication.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)
        self.app = QApplication(sys.argv)
        self.ui = OmniUI()
        
        load_dotenv()
        url = os.getenv("SUPABASE_URL"); key = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key) if url and key else None
        
        enable_ghost_mode(self.ui.winId())
        self.chats = load_chats(); self.current_chat_index = 0
        self.user_session = None; self.ai_worker = None; self.voice_worker = None
        self.doc_worker = None; self.search_worker = None; self.screen_selector = None
        
        self._setup_hotkeys(); self._connect_signals()
        self._check_initial_state(); self._refresh_ui_chats()

    def _setup_hotkeys(self):
        self.hotkey_handler = GlobalHotkeyHandler()
        self.hotkey_handler.hotkey_pressed.connect(self.handle_visibility_toggle)
        self.hotkey_handler.voice_hotkey_pressed.connect(lambda: self.handle_voice_toggle("system"))
        self.hotkey_handler.mic_hotkey_pressed.connect(lambda: self.handle_voice_toggle("mic"))

    def handle_visibility_toggle(self):
        if self.ui.isVisible(): self.ui.hide()
        else: self.ui.show_and_focus()

    def _connect_signals(self):
        self.ui.submission_requested.connect(self.process_ai_query)
        self.ui.config_saved.connect(self.save_configuration)
        self.ui.chat_selected.connect(self.switch_chat)
        self.ui.chat_delete_requested.connect(self.remove_chat)
        self.ui.new_chat_requested.connect(self.add_new_chat)
        self.ui.file_selected.connect(self.start_document_processing)
        self.ui.login_requested.connect(self.handle_login)
        self.ui.tool_selected.connect(self.handle_tool_execution)
        self.ui.update_requested.connect(self.check_for_updates)
        self.ui.logout_requested.connect(self.handle_logout)

    def handle_login(self, email, password):
        if not self.supabase: return
        self.ui.set_login_loading(True)
        def _login():
            try:
                res = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
                profile = self.supabase.table("profiles").select("*").eq("id", res.user.id).single().execute().data
                if profile:
                    self.user_session = res.session; with open(".auth_token", "w") as f: f.write(email)
                    self.ui.update_profile_info(profile); QTimer.singleShot(0, self._check_initial_state)
            except Exception as e: self.ui.login_error.setText(f"Error: {str(e)}")
            finally: self.ui.set_login_loading(False)
        QTimer.singleShot(500, _login)

    def handle_logout(self):
        if os.path.exists(".auth_token"): os.remove(".auth_token")
        self.user_session = None; self.ui.stack.setCurrentIndex(0)
        if self.ui.sidebar_expanded: self.ui.toggle_sidebar()

    def check_for_updates(self):
        self.ui.chat_display.append("<b>[SISTEMA] Verificando actualizaciones...</b><br>")
        def _check():
            try:
                r = requests.get(UPDATE_URL, timeout=5)
                if r.status_code == 200:
                    remote = r.json().get("version", VERSION)
                    if remote > VERSION: self.ui.chat_display.append(f"<span style='color:yellow;'>[UPDATE] v{remote} disponible. <a href='{r.json().get('url', '#')}'>[BAJAR]</a></span><br>")
                    else: self.ui.chat_display.append("<span style='color:#00FF41;'>[SISTEMA] Versión actual al día.</span><br>")
            except: self.ui.chat_display.append("<span style='color:red;'>[SISTEMA] Error de conexión.</span><br>")
        QTimer.singleShot(1000, _check)

    def handle_tool_execution(self, tool_id):
        if tool_id == "clipboard":
            text = QApplication.clipboard().text()
            if text:
                self.ui.chat_display.append("<b>[SISTEMA] Portapapeles Sincronizado.</b><br>")
                self.ui.chat_history.append({"role": "user", "content": f"[CLIPBOARD]\n{text}"})
                self.ui.input_field.setText("Resume esto: ")
            else: self.ui.chat_display.append("<span style='color:orange;'>[SISTEMA] Vacío.</span><br>")
        elif tool_id == "web_search":
            self.ui.input_field.setText("Búsqueda Web: "); self.ui.input_field.setFocus()
        elif tool_id == "screen_read":
            self.ui.hide(); self.screen_selector = ScreenSelector()
            self.screen_selector.area_selected.connect(self.process_screen_ocr); self.screen_selector.show()

    def process_screen_ocr(self, rect: QRect):
        self.ui.show(); text = extract_text_from_area(rect)
        if text:
            self.ui.chat_display.append("<b>[SISTEMA] OCR OK.</b><br>")
            self.ui.chat_history.append({"role": "user", "content": f"[OCR]\n{text}"})
            self.ui.input_field.setText("Explica esto: ")
        else: self.ui.chat_display.append("<span style='color:orange;'>[SISTEMA] Sin texto detectado.</span><br>")

    def process_ai_query(self, prompt: str):
        if self.ai_worker and self.ai_worker.isRunning(): return
        if prompt.startswith("Búsqueda Web:"):
            query = prompt.replace("Búsqueda Web:", "").strip(); self.start_web_search(query); return
        self.chats[self.current_chat_index]["messages"] = self.ui.chat_history; save_chats(self.chats)
        self.ai_worker = AIWorker(prompt, self.ui.chat_history[:-1])
        self.ai_worker.response_ready.connect(self.handle_ai_response)
        self.ai_worker.error_occurred.connect(lambda e: self.ui.display_ai_response(f"<span style='color:red;'>{e}</span>"))
        self.ai_worker.start()

    def start_web_search(self, query):
        self.ui.chat_display.append(f"<b>[SISTEMA] Buscando en la red: {query}...</b><br>")
        self.search_worker = WebSearchWorker(query)
        self.search_worker.results_ready.connect(self.handle_web_search_results); self.search_worker.start()

    def handle_web_search_results(self, results):
        self.ui.chat_history.append({"role": "user", "content": results})
        self.ui.chat_display.append("<b>[SISTEMA] Analizando fuentes web y sintetizando...</b><br>")
        prompt = "Actúa como experto analista. Basado en el 'CONTEXTO DE FUENTES WEB EXTERNAS' anterior, responde a mi consulta de forma técnica y profesional citando fuentes."
        self.process_ai_query(prompt)

    def handle_ai_response(self, response):
        self.ui.display_ai_response(response); self.chats[self.current_chat_index]["messages"] = self.ui.chat_history; save_chats(self.chats)

    def _check_initial_state(self):
        if not os.path.exists(".auth_token"): self.ui.stack.setCurrentIndex(0); return
        if not os.getenv("GROQ_API_KEY"): self.ui.stack.setCurrentIndex(1)
        else: self.ui.stack.setCurrentIndex(2); self.switch_chat(0)

    def _refresh_ui_chats(self): self.ui.update_chat_list([c["title"] for c in self.chats], self.current_chat_index)
    def switch_chat(self, index):
        if 0 <= index < len(self.chats): self.current_chat_index = index; self.ui.load_chat_content(self.chats[index]["messages"])
    def add_new_chat(self):
        if len(self.chats) < 5:
            new_id = max([c["id"] for c in self.chats]) + 1 if self.chats else 0
            self.chats.append({"id": new_id, "title": f"Chat {new_id+1}", "messages": []})
            self.current_chat_index = len(self.chats) - 1; save_chats(self.chats); self._refresh_ui_chats(); self.switch_chat(self.current_chat_index)
    def remove_chat(self, index):
        if len(self.chats) > 1:
            self.chats.pop(index); self.current_chat_index = min(self.current_chat_index, len(self.chats)-1)
            save_chats(self.chats); self._refresh_ui_chats(); self.switch_chat(self.current_chat_index)
    def start_document_processing(self, file_path):
        self.doc_worker = DocumentWorker(file_path)
        self.doc_worker.extraction_ready.connect(lambda f, c: (self.ui.chat_display.append(f"<b>[SISTEMA] {f} OK.</b><br>"), self.ui.chat_history.append({"role": "user", "content": f"[DOC]\n{c}"})))
        self.doc_worker.start()
    def save_configuration(self, api_key):
        with open(".env", "a") as f: f.write(f"\nGROQ_API_KEY={api_key}")
        os.execl(sys.executable, sys.executable, *sys.argv)
    def handle_voice_toggle(self, source="system"):
        if self.voice_worker and self.voice_worker.isRunning(): self.voice_worker.stop_recording(); return
        self.voice_worker = VoiceWorker(max_duration=MAX_RECORDING_DURATION, source_type=source)
        color = "#FF003C" if source == "system" else "#FFFF00"
        self.voice_worker.listening_status.connect(lambda active: self._update_ui_style(active, color))
        self.voice_worker.transcription_ready.connect(lambda t: (self.ui.input_field.setText(t), self.ui.input_field.setFocus()))
        self.voice_worker.start()
    def _update_ui_style(self, active, color):
        c = color if active else "#00FF41"; self.ui.content_area.setStyleSheet(f"QWidget#MainContainer {{ border: 2px solid {c}; border-radius: 10px; }}")
    def run(self): self.ui.show_and_focus(); sys.exit(self.app.exec())

if __name__ == "__main__":
    controller = OmniController(); controller.run()
