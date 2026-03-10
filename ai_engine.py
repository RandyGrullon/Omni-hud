# ai_engine.py
import os
from typing import List, Dict, Optional
from groq import Groq
from PyQt6.QtCore import QThread, pyqtSignal
from constants import GROQ_MODEL, DEVELOPER_SYSTEM_PROMPT

class AIWorker(QThread):
    """
    Motor Multi-Threading para el asistente Omni.
    Refactorizado para ser agnóstico al modelo y eficiente en memoria.
    """
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, prompt: str, history: List[Dict[str, str]], api_key: Optional[str] = None):
        super().__init__()
        self.prompt = prompt
        self.history = history
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError("API Key faltante.")

    def run(self) -> None:
        """ Ejecución del worker de forma asíncrona. """
        try:
            client = Groq(api_key=self.api_key)
            messages = self._build_messages()

            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                temperature=0.5,
                max_tokens=2048,
                stream=False
            )
            
            response = completion.choices[0].message.content
            if response:
                self.response_ready.emit(response)
            else:
                self.error_occurred.emit("Respuesta vacía del motor IA.")
                
        except Exception as e:
            self.error_occurred.emit(f"Falla del Motor IA: {str(e)}")

    def _build_messages(self) -> List[Dict[str, str]]:
        """ Construye la lista de mensajes compatible con la API de Groq. """
        messages = [{"role": "system", "content": DEVELOPER_SYSTEM_PROMPT}]
        
        # Añadir recordatorio dinámico basado en el idioma del prompt actual
        mirror_instruction = "Remember: Respond in English if the user writes in English, or Spanish if the user writes in Spanish."
        messages.append({"role": "system", "content": mirror_instruction})
        
        for msg in self.history:
            role = "assistant" if msg["role"] == "model" else "user"
            messages.append({"role": role, "content": msg["content"]})
            
        messages.append({"role": "user", "content": self.prompt})
        return messages
