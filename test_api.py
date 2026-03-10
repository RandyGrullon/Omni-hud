import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key or api_key == "tu_api_key_aqui":
    print("ERROR: API Key no configurada en .env")
else:
    try:
        genai.configure(api_key=api_key)
        print("--- Listando modelos disponibles ---")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"ID: {m.name}")
    except Exception as e:
        print(f"ERROR de conexión: {e}")
