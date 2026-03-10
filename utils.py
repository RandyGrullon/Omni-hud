# utils.py
import ctypes
import platform
import keyboard
from PyQt6.QtCore import QObject, pyqtSignal

class GlobalHotkeyHandler(QObject):
    """
    Registra los hotkeys globales y emite señales para que 
    la interfaz se despierte sin bloquear el Main Thread.
    """
    hotkey_pressed = pyqtSignal()
    voice_hotkey_pressed = pyqtSignal()
    mic_hotkey_pressed = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Hotkey para mostrar/ocultar Omni
        keyboard.add_hotkey('ctrl+space', self._on_invoke)
        # Hotkey para capturar audio del sistema (Rojo)
        keyboard.add_hotkey('ctrl+shift+r', self._on_voice)
        # Hotkey para capturar micrófono propio (Amarillo)
        keyboard.add_hotkey('ctrl+shift+m', self._on_mic)

    def _on_invoke(self):
        self.hotkey_pressed.emit()

    def _on_voice(self):
        self.voice_hotkey_pressed.emit()

    def _on_mic(self):
        self.mic_hotkey_pressed.emit()

def enable_ghost_mode(win_id):
    """
    Implementa WDA_EXCLUDEFROMCAPTURE mediante C++ Interop (ctypes)
    para que la ventana sea invisible en OBS/Discord/Capturas de pantalla.
    Compatible con Windows 10/11. En macOS/Linux omite silenciosamente 
    para no generar excepciones (cross-platform fallback).
    """
    if platform.system() == "Windows":
        try:
            # WDA_EXCLUDEFROMCAPTURE = 0x00000011
            hwnd = int(win_id)
            user32 = ctypes.windll.user32
            user32.SetWindowDisplayAffinity(hwnd, 0x00000011)
            print("Ghost Mode activado: HUD invisible en capturas.")
        except Exception as e:
            print(f"[Warning] Error al activar Ghost Mode en Windows: {e}")
    elif platform.system() == "Darwin":
        # Apple Silicon / macOS. Requiere APIs privadas nativas (CoreGraphics) para ignorar capturas.
        # Fallback elegante: el HUD funcionará normalmente pero sin la invisibilidad absoluta en OBS.
        print("Omni HUD iniciado en macOS (Apple Silicon).")
