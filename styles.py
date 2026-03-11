# styles.py

# Paleta de Colores Moderna - Emerald/Dark
ACCENT = "#10b981"  # Emerald 500
ACCENT_LOW = "rgba(16, 185, 129, 0.1)"
BG_DARK = "rgba(15, 15, 15, 245)"
BG_CARD = "rgba(25, 25, 25, 200)"
BORDER_COLOR = "rgba(255, 255, 255, 0.08)"
TEXT_PRIMARY = "#f8fafc"
TEXT_SECONDARY = "#94a3b8"

OMNI_STYLESHEET = f"""
QWidget#MainContainer {{
    background-color: {BG_DARK}; 
    border: 1px solid {BORDER_COLOR}; 
    border-radius: 20px;
}}

#Sidebar {{ 
    background-color: rgba(10, 10, 10, 220); 
    border-right: 1px solid {BORDER_COLOR}; 
    border-top-left-radius: 20px;
    border-bottom-left-radius: 20px;
}}

#DragHandle {{
    background-color: transparent;
    min-height: 25px;
}}

/* --- MODERN INPUTS --- */
QLineEdit {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_COLOR};
    border-radius: 12px;
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 14px;
    padding: 12px 16px;
}}
QLineEdit:focus {{
    border: 1px solid {ACCENT};
    background-color: rgba(16, 185, 129, 0.05);
}}

/* --- BUTTONS --- */
QPushButton {{
    background-color: {ACCENT};
    color: #050505;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 700;
    font-size: 12px;
    font-family: 'Segoe UI', sans-serif;
}}
QPushButton:hover {{
    background-color: #34d399;
}}

#SideBtnMain {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {ACCENT}, stop:1 #059669);
    color: #050505;
    border-radius: 12px;
    font-weight: 800;
    margin: 5px 10px;
    padding: 12px;
}}

#IconButton {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 10px;
    color: {TEXT_SECONDARY};
    font-size: 16px;
    font-family: 'Segoe UI Emoji', 'Segoe UI Symbol';
}}
#IconButton:hover {{
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid {BORDER_COLOR};
    color: {ACCENT};
}}

/* --- CHAT LIST --- */
#ChatList {{
    background: transparent;
    border: none;
    padding: 5px;
}}
#ChatList::item {{
    margin-bottom: 6px;
    border-radius: 10px;
    padding: 5px;
}}
#ChatList::item:selected {{
    background-color: {ACCENT_LOW};
}}

QTextBrowser {{
    background-color: transparent;
    border: none;
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}}

QTreeView {{
    background-color: transparent;
    border: 1px solid {BORDER_COLOR};
    color: {TEXT_PRIMARY};
    font-family: 'JetBrains Mono', monospace;
    border-radius: 10px;
}}
QTreeView::item:hover {{ background-color: {ACCENT_LOW}; }}
QTreeView::item:selected {{ background-color: {ACCENT}; color: #000; }}
"""

USER_MSG_HTML = f"""
<div style='margin-bottom: 20px; text-align: right;'>
    <div style='display: inline-block; background: {ACCENT}; color: #000; padding: 12px 16px; border-radius: 18px 18px 4px 18px; max-width: 80%; font-weight: 500; font-size: 13px; line-height: 1.4;'>
        {{content}}
    </div>
</div>
"""

AI_MSG_HTML = f"""
<div style='margin-bottom: 30px; padding: 15px; background: rgba(255,255,255,0.02); border-radius: 15px; border: 1px solid rgba(255,255,255,0.03);'>
    <div style='display: flex; align-items: center; margin-bottom: 10px;'>
        <span style='color: {ACCENT}; font-weight: 800; font-size: 10px; letter-spacing: 2px; background: {ACCENT_LOW}; padding: 2px 8px; border-radius: 4px;'>OMNI CORE</span>
    </div>
    <div style='color: {TEXT_PRIMARY}; line-height: 1.6; font-size: 14px;'>
        {{content}}
    </div>
</div>
"""

HELP_MSG_HTML = f"""
<div style='color: #00E5FF; border: 1px solid rgba(0, 229, 255, 0.2); padding: 15px; border-radius: 12px; background-color: rgba(0, 229, 255, 0.03); margin: 20px 0;'>
    <b style='letter-spacing: 1px; font-size: 11px;'>[SYSTEM_GUIDE]</b><br><br>
    <div style='font-size: 13px; opacity: 0.9; line-height: 1.5;'>{{content}}</div>
</div>
"""

CODE_BLOCK_STYLE = """
pre { 
    background-color: #0f172a; 
    border: 1px solid rgba(255,255,255,0.05); 
    border-radius: 12px; 
    padding: 18px; 
    color: #e2e8f0; 
    font-family: 'JetBrains Mono', monospace; 
    font-size: 12px;
    margin-top: 15px;
}
.copy-btn { 
    color: #10b981; 
    background: rgba(16, 185, 129, 0.1); 
    border: 1px solid #10b981; 
    padding: 4px 10px; 
    border-radius: 8px; 
    font-size: 10px; 
    font-weight: 700;
}
"""
