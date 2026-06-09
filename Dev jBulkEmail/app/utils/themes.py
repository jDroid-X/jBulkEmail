import tkinter as tk
from tkinter import ttk, scrolledtext
import json
from pathlib import Path

# --- THEME DEFINITIONS ---
# (Extracted from assets/themes.json for centralized logic)
DEFAULT_THEME = {
    "bg": "#0B132B",
    "panel": "#1C2541",
    "box_bg": "#2A3A5A",
    "text_main": "#5BC0BE",
    "text_highlight": "#FFFFFF",
    "aqua": "#6FFFE9",
    "glow": "#3A506B",
    "border": "#3A506B",
    "btn_bg": "#5BC0BE",
    "btn_fg": "#0B132B",
    "btn_hover": "#6FFFE9",
    "btn_active": "#3A506B",
    "entry_bg": "#1C2541",
    "entry_fg": "#FFFFFF",
    "scrolled_text_bg": "#0B132B",
    "scrolled_text_fg": "#FFFFFF",
    "relief": "raised",
    "shadow": "#000000"
}

class ThemeManager:
    """
    Tactical Theme Management Protocol.
    Hierarchy Level: Utils / Aesthetics.
    Responsibility: UI Synchronization across all MVC components.
    """
    def __init__(self, assets_dir):
        self.themes_file = Path(assets_dir) / "themes.json"
        self.themes = {}
        self.load_themes()

    def load_themes(self):
        """Standardized Theme Discovery."""
        if self.themes_file.exists():
            try:
                with open(self.themes_file, 'r', encoding='utf-8') as f:
                    self.themes = json.load(f)
            except Exception:
                self.themes = {"Neural Void (Future)": DEFAULT_THEME}
        else:
            self.themes = {"Neural Void (Future)": DEFAULT_THEME}

    def get_theme(self, name):
        """Retrieve theme dictionary by name."""
        return self.themes.get(name, DEFAULT_THEME)

    @staticmethod
    def calibrate_box_bg(hex_color, factor=1.4):
        """Optimized color calibration protocol (40% adjustment)."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3: hex_color = ''.join([c*2 for c in hex_color])
        rgb = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        return "#%02x%02x%02x" % tuple(min(255, int(c * factor)) for c in rgb)

    def apply_to_root(self, root, theme_name):
        """Apply the selected theme to the entire UI hierarchy."""
        theme = self.get_theme(theme_name)
        style = ttk.Style()
        
        box_bg = self.calibrate_box_bg(theme['bg'], 1.4)
        header_font = ('Segoe UI', 12, 'bold')
        
        # 1. Configure Global Styles
        style.configure('TFrame', background=theme['bg'])
        style.configure('TLabel', background=theme['bg'], foreground=theme['text_main'])
        
        style.configure('TLabelFrame', background=box_bg, 
                        foreground=theme['text_highlight'], 
                        borderwidth=2, relief='solid', font=header_font)
        style.configure('TLabelFrame.Label', background=box_bg, 
                        foreground=theme['text_highlight'], font=header_font)
                        
        style.configure('TButton', background=theme['btn_bg'], foreground=theme['btn_fg'])
        style.configure('Accent.TButton', background=theme['aqua'], foreground='#000000')
        
        # 2. Hierarchy Recursion
        self._sync_recursive(root, theme)
        root.configure(bg=theme['bg'])

    def _sync_recursive(self, w, theme):
        """Deep hierarchy theme synchronization protocol."""
        from app.utils.widgets import RoundedButton
        try:
            if isinstance(w, tk.Toplevel): w.configure(bg=theme['bg'])
            if isinstance(w, tk.Frame) and not isinstance(w, ttk.Frame):
                w.configure(bg=theme['bg'])
            elif isinstance(w, tk.Label) and not isinstance(w, ttk.Label):
                w.configure(bg=theme['bg'], fg=theme['text_main'])
            elif isinstance(w, tk.Canvas) and not isinstance(w, RoundedButton):
                w.configure(bg=theme['entry_bg'])
            elif isinstance(w, (tk.Text, scrolledtext.ScrolledText)):
                w.configure(bg=theme['scrolled_text_bg'], fg=theme['scrolled_text_fg'],
                            insertbackground=theme['text_main'])
            elif isinstance(w, RoundedButton):
                w.bg, w.fg = theme['btn_bg'], theme['btn_fg']
                w.hover_bg, w.active_bg = theme['btn_hover'], theme['btn_active']
                w.draw_button()
        except: pass
        
        for child in w.winfo_children():
            self._sync_recursive(child, theme)
