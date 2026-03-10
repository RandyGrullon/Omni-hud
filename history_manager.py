# history_manager.py
import json
import os
from typing import List, Dict

CHATS_FILE = "chats.json"

def load_chats() -> List[Dict]:
    """ Carga la lista de chats desde el archivo local. """
    if not os.path.exists(CHATS_FILE):
        return [{"id": 0, "title": "Chat 1", "messages": []}]
    
    try:
        with open(CHATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return [{"id": 0, "title": "Chat 1", "messages": []}]

def save_chats(chats: List[Dict]):
    """ Guarda la lista completa de chats en el archivo local. """
    with open(CHATS_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, indent=4, ensure_ascii=False)
