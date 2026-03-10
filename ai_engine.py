# ai_engine.py
import os
from typing import List, Dict, Optional
from groq import Groq
from PyQt6.QtCore import QThread, pyqtSignal
from constants import GROQ_MODEL, DEVELOPER_SYSTEM_PROMPT

# Modelo de visión recomendado
VISION_MODEL = "llama-3.2-11b-vision-preview"

class AIWorker(QThread):
    response_ready = pyqtSignal(str)
    chunk_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, prompt: str, history: List[Dict], image_b64: Optional[str] = None):
        super().__init__()
        self.prompt = prompt
        self.history = history
        self.image_b64 = image_b64

    def run(self):
        try:
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            
            # Construir mensaje con imagen si existe
            content = []
            if self.image_b64:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{self.image_b64}"}
                })
            
            content.append({"type": "text", "text": self.prompt})

            messages = [{"role": "system", "content": DEVELOPER_SYSTEM_PROMPT}]
            for msg in self.history:
                messages.append({"role": "user" if msg["role"] == "user" else "assistant", "content": msg["content"]})
            
            messages.append({"role": "user", "content": content})

            # Usar modelo de visión si hay imagen, sino el estándar
            model = VISION_MODEL if self.image_b64 else GROQ_MODEL

            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
                stream=True
            )
            
            full_response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    text_chunk = chunk.choices[0].delta.content
                    full_response += text_chunk
                    self.chunk_ready.emit(text_chunk)
            
            self.response_ready.emit(full_response)
        except Exception as e:
            self.error_occurred.emit(f"Error Neural: {str(e)}")
