# styles.py

OMNI_STYLESHEET = """
QWidget#MainContainer {
    background-color: rgba(10, 10, 10, 240); 
    border: 1px solid rgba(0, 255, 65, 0.5); 
    border-radius: 12px;
}

#DragHandle {
    background-color: rgba(0, 255, 65, 15);
    border-top-left-radius: 11px;
    border-top-right-radius: 11px;
    border-bottom: 1px solid rgba(0, 255, 65, 0.2);
    min-height: 12px;
}

/* --- TAB BAR STYLING --- */
QTabBar::tab {
    background-color: #1a1a1a;
    color: #888;
    border: 1px solid #333;
    padding: 5px 15px;
    margin-right: 2px;
    font-size: 11px;
}
QTabBar::tab:selected {
    color: #00FF41;
    border: 1px solid #00FF41;
}

/* --- FILE EXPLORER STYLING --- */
QTreeView {
    background-color: transparent;
    border: 1px solid #333;
    color: #E0E0E0;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
}
QTreeView::item:hover {
    background-color: rgba(0, 255, 65, 20);
}
QTreeView::item:selected {
    background-color: rgba(0, 255, 65, 50);
    color: #00FF41;
}
QHeaderView::section {
    background-color: #1a1a1a;
    color: #00FF41;
    padding: 4px;
    border: 1px solid #333;
}

QLabel { color: #00FF41; font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 13px; }
QTextBrowser { background-color: transparent; border: none; color: #E0E0E0; font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 13px; }
QLineEdit {
    background-color: rgba(20, 20, 20, 200);
    border: 1px solid rgba(0, 255, 65, 0.3);
    border-radius: 6px;
    color: #00FF41;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 13px;
    padding: 10px;
}
QLineEdit:focus {
    border: 1px solid #00FF41;
}
QPushButton { background-color: #00FF41; color: #0D0D0D; border: none; border-radius: 4px; padding: 10px; font-weight: bold; }
"""
USER_MSG_HTML = "<div style='color: #00FF41; margin-bottom: 8px; padding: 8px; background: rgba(0,255,65,0.05); border-left: 2px solid #00FF41; border-radius: 4px;'><b style='font-size: 11px; opacity: 0.8;'>&gt;&gt; USER</b><br>{content}</div>"
AI_MSG_HTML = "<div style='color: #888; font-weight: bold; font-size: 11px; margin-top: 12px;'>&gt;&gt; OMNI</div><div style='color: #E0E0E0; margin-bottom: 15px; line-height: 1.5;'>{content}</div><hr style='border: none; border-top: 1px solid rgba(255,255,255,0.05);'>"
HELP_MSG_HTML = """
<div style='color: #00E5FF; border: 1px solid #00E5FF; padding: 10px; border-radius: 5px; background-color: rgba(0, 229, 255, 0.05); margin: 10px 0;'>
    <b style='letter-spacing: 2px;'>[SYSTEM_GUIDE]</b><br><br>
    {content}
</div>
"""

CODE_BLOCK_STYLE = """
pre { background-color: rgba(10, 10, 10, 0.8); border: 1px solid rgba(0, 255, 65, 0.2); border-radius: 5px; padding: 15px; color: #E0E0E0; margin-top: 10px; font-family: 'JetBrains Mono', monospace; font-size: 12px; }
...

.copy-btn { color: #00FF41; background-color: #111; border: 1px solid #00FF41; padding: 2px 8px; border-radius: 3px; font-size: 10px; float: right; margin-bottom: -20px; text-decoration: none; }
.k { color: #66d9ef } .s { color: #e6db74 } .nf { color: #a6e22e } .c { color: #75715e }
"""
