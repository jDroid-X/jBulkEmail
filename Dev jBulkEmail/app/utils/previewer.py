import tkinter as tk
from tkinter import ttk, scrolledtext
import sys

try:
    from tkinterweb import HtmlFrame
    HTML_SUPPORT = True
except ImportError:
    HTML_SUPPORT = False

class HtmlPreviewer:
    """
    Tactical HTML Preview Protocol.
    Hierarchy Level: Utils / UI Specialist.
    Responsibility: Render HTML drafts in a sandboxed window.
    """
    def __init__(self, parent_root):
        self.root = parent_root

    def show_preview(self, html_content, subject="Mission Preview"):
        """Spawn a tactical preview window."""
        preview_win = tk.Toplevel(self.root)
        preview_win.title(f"🔍 {subject}")
        preview_win.geometry("800x600")
        
        container = ttk.Frame(preview_win, padding="10")
        container.pack(fill="both", expand=True)

        ttk.Label(container, text=f"Subject: {subject}", font=('Segoe UI', 10, 'bold')).pack(fill="x", pady=(0, 10))
        
        if HTML_SUPPORT:
            try:
                frame = HtmlFrame(container)
                frame.pack(fill="both", expand=True)
                frame.load_html(html_content)
                return
            except Exception as e:
                print(f"HtmlFrame Render failure: {e}")

        # Fallback to ScrolledText if HTML render fails or is missing
        fallback = scrolledtext.ScrolledText(container, wrap=tk.WORD, font=('Consolas', 10))
        fallback.pack(fill="both", expand=True)
        fallback.insert('1.0', html_content)
        fallback.config(state='disabled')
