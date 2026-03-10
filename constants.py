# constants.py
from PyQt6.QtCore import Qt

# Dimensiones y Flags
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
WINDOW_FLAGS = (
    Qt.WindowType.FramelessWindowHint | 
    Qt.WindowType.WindowStaysOnTopHint | 
    Qt.WindowType.Tool
)

# Modelos y Motores
DEFAULT_MOTOR = "groq"
GROQ_MODEL = "llama-3.3-70b-versatile"

# System Prompts
DEVELOPER_SYSTEM_PROMPT = (
    "LANGUAGE RULES: YOU MUST DETECT THE USER'S LANGUAGE AND REPLY IN THE SAME LANGUAGE. "
    "IF THE USER WRITES IN ENGLISH, REPLY IN ENGLISH. IF THE USER WRITES IN SPANISH, REPLY IN SPANISH. "
    "Act as a Senior Full Stack Developer. Provide Markdown code and concise explanations."
)

# Hotkeys
HOTKEY_INVOKE = "ctrl+space"
HOTKEY_VOICE = "ctrl+shift+r"
HOTKEY_MIC = "ctrl+shift+m"
HOTKEY_CLEAR = "ctrl+l"

# Audio
MAX_RECORDING_DURATION = 60


# Estilos de Opacidad
BACKGROUND_OPACITY = 235 # 0-255
