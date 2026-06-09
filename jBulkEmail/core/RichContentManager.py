import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font, colorchooser, simpledialog
import json
import webbrowser
import os
import io
import base64
import ctypes
import re
import requests
import threading
from PIL import Image, ImageTk, ImageGrab
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

# --- ToolTip Helper ---
class ToolTip:
    """Lightweight hover tooltip for any tkinter widget."""
    theme_bg = "#1E1E2E" # Fallback
    theme_fg = "#00E5FF" # Fallback
    
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self._tip_win = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, event=None):
        if self._tip_win or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self._tip_win = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(tw, text=self.text, justify="left",
                       background=ToolTip.theme_bg, foreground=ToolTip.theme_fg,
                       relief="solid", borderwidth=1,
                       font=("Segoe UI", 8))
        lbl.pack(ipadx=4, ipady=2)

    def _hide(self, event=None):
        if self._tip_win:
            self._tip_win.destroy()
            self._tip_win = None

class RichToolTip:
    """Hover tooltip for any tkinter widget supporting multicolor text and better formatting."""
    theme_bg = "#1E1E2E" # Fallback
    theme_fg = "#FFFFFF" # Fallback

    def __init__(self, widget, lines):
        """
        lines: List of tuples (text, color, font_style)
        e.g. [("Hello", "#FF0000", ("Segoe UI", 9, "bold")), (" World", "#FFFFFF", ("Segoe UI", 9))]
        """
        self.widget = widget
        self.lines = lines
        self._tip_win = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, event=None):
        if self._tip_win or not self.lines:
            return
        
        # Position below widget
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self._tip_win = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.configure(bg=RichToolTip.theme_bg, padx=1, pady=1) # Border effect
        
        # Use a Text widget for multicolor support
        text_area = tk.Text(tw, background=RichToolTip.theme_bg, foreground=RichToolTip.theme_fg,
                           relief="flat", borderwidth=0, font=("Segoe UI", 9),
                           padx=10, pady=8, wrap="word", height=len(self.lines) if len(self.lines) < 15 else 15,
                           width=60)
        
        for i, (txt, color, fstyle) in enumerate(self.lines):
            tag_name = f"tag_{i}"
            text_area.insert(tk.END, txt + "\n" if i < len(self.lines)-1 else txt, tag_name)
            text_area.tag_configure(tag_name, foreground=color, font=fstyle)
        
        text_area.config(state="disabled")
        text_area.pack()
        
        # Adjust width based on content if possible, or keep fixed
        tw.update_idletasks()
        # Ensure it doesn't go off screen
        sw = tw.winfo_screenwidth()
        if x + tw.winfo_width() > sw:
            tw.wm_geometry(f"+{sw - tw.winfo_width() - 10}+{y}")

    def _hide(self, event=None):
        if self._tip_win:
            self._tip_win.destroy()
            self._tip_win = None

# --- Link Preview (Start) ---
class LinkPreviewFetcher:
    """Fetches metadata from a URL and generates a WhatsApp-style preview card"""
    @staticmethod
    def get_preview_html(url):
        try:
            if not url.startswith('http'):
                url = 'https://' + url
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.title.string if soup.title else url
            desc = ""
            domain = url.split('/')[2] if '/' in url else url
            
            meta_desc = soup.find("meta", property="og:description")
            if meta_desc: desc = meta_desc["content"]
            
            card_html = f'''
            <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 8px;">
                <a href="{url}" style="font-weight: bold; color: #0066cc;">{title}</a>
                <p style="font-size: 12px; color: #666; margin: 5px 0;">{desc[:100]}...</p>
                <div style="font-size: 10px; color: #999;">{domain}</div>
            </div>
            '''
            return card_html
        except:
            return f'<a href="{url}">{url}</a>'
# --- Link Preview (End) ---

# --- Clipboard Manager (Start) ---
class RichContentManager:
    """Helper for cleaning and processing HTML for Email compatibility"""
    @staticmethod
    def get_html_from_clipboard():
        try:
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            
            if not user32.OpenClipboard(None): return ""
            
            try:
                CF_HTML = user32.RegisterClipboardFormatW("HTML Format")
                h_data = user32.GetClipboardData(CF_HTML)
                if h_data:
                    try:
                        lp_data = kernel32.GlobalLock(h_data)
                        if lp_data:
                            raw_data = ctypes.string_at(lp_data)
                            html_str = raw_data.decode('utf-8', errors='ignore')
                            frag_start = html_str.find('<!--StartFragment-->')
                            frag_end = html_str.find('<!--EndFragment-->')
                            if frag_start != -1: 
                                return html_str[frag_start+20:frag_end].strip()
                            return html_str
                    finally:
                        kernel32.GlobalUnlock(h_data)
                
                # Fallback to Text
                CF_UNICODETEXT = 13
                h_text = user32.GetClipboardData(CF_UNICODETEXT)
                if h_text:
                    lp_text = kernel32.GlobalLock(h_text)
                    if lp_text:
                        text = ctypes.wstring_at(lp_text)
                        kernel32.GlobalUnlock(h_text)
                        return f"<p>{text.replace(chr(10), '<br>')}</p>"
                        
                return ""
            finally:
                user32.CloseClipboard()
        except:
            return ""

# --- MAIN WYSIWYG EDITOR LOGIC (Moved from bulk_email_sender.py) ---
class RichTextEditor:
    def __init__(self, parent_window, text_widget, update_html_mode_callback, 
                 log_callback=None, attach_callback=None, attach_mgr_callback=None, 
                 attach_status_var=None, theme_callback=None, help_mission_callback=None):
        self.root = parent_window
        self.body_text = text_widget
        self.set_html_mode = update_html_mode_callback
        self.log_message = log_callback if log_callback else (lambda x: print(x))
        self.attach_files = attach_callback
        self.attach_mgr = attach_mgr_callback
        self.attach_status_var = attach_status_var # Variable for "X files (Y MB)" display
        self.theme_callback = theme_callback
        self.help_mission_callback = help_mission_callback
        
        self.images = []
        self.images_data = []
        
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_steps = 50
        self._undo_timer = None   # debounce timer id
        
        self.font_size_var = tk.StringVar(value="11")
        
        self._setup_tags()
        self._bind_events()

    def _setup_tags(self):
        self.body_text.tag_config("bold", font=('Segoe UI', 11, 'bold'))
        self.body_text.tag_config("italic", font=('Segoe UI', 11, 'italic'))
        self.body_text.tag_config("link", foreground="#0066CC", underline=True)
        
        # Click binding for links
        self.body_text.tag_bind("link", "<Button-1>", self._handle_link_click)
        self.body_text.tag_bind("link", "<Enter>", lambda e: self.body_text.config(cursor="hand2"))
        self.body_text.tag_bind("link", "<Leave>", lambda e: self.body_text.config(cursor=""))

    def _bind_events(self):
        # Keyboard shortcuts
        self.body_text.bind('<Control-b>', lambda e: self.format_bold())
        self.body_text.bind('<Control-i>', lambda e: self.format_italic())
        self.body_text.bind('<Control-z>', lambda e: self.undo_action())
        self.body_text.bind('<Control-y>', lambda e: self.redo_action())
        self.body_text.bind('<Tab>', lambda e: self.insert_tab() or "break")
        self.body_text.bind('<Shift-Tab>', lambda e: self.dedent_text() or "break")
        self.body_text.bind('<KeyRelease-Return>', self.check_auto_link)
        
        # Track changes
        self.body_text.bind('<<Modified>>', self.on_text_modified)
        
        # Right-click context menu
        self.body_text.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event):
        """Show standard Windows right-click menu"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Cut", command=lambda: self.body_text.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: self.body_text.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: self.body_text.event_generate("<<Paste>>"))
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: self.body_text.tag_add("sel", "1.0", "end"))
        menu.post(event.x_root, event.y_root)

    def create_toolbar(self, parent_frame):
        """Creates the toolbar frame (caller must layout it, e.g. pack or grid)"""
        toolbar_frame = ttk.Frame(parent_frame)
        # toolbar_frame.pack(fill="x", pady=2) <--- REMOVED

        
        # SINGLE HIGH-DENSITY TOOLBAR ROW
        row1 = ttk.Frame(toolbar_frame)
        row1.pack(fill="x", pady=2)
        
        # --- helper to create a button and attach a tooltip in one call ---
        def _btn(parent, text, cmd, style, width, tip):
            b = ttk.Button(parent, text=text, command=cmd, style=style, width=width)
            b.pack(side="left", padx=1)
            ToolTip(b, tip)
            return b

        # Section: Formatting
        _btn(row1, "B",  self.format_bold,    'Accent.TButton', 2, "Bold (Ctrl+B)")
        _btn(row1, "I",  self.format_italic,  'Accent.TButton', 2, "Italic (Ctrl+I)")
        _btn(row1, "🎨", self.format_color,   'Accent.TButton', 3, "Font Color")

        size_combo = ttk.Combobox(row1, textvariable=self.font_size_var,
                                  values=["8","9","10","11","12","14","16","18","20","24","36"],
                                  width=2, state="readonly")
        size_combo.pack(side="left", padx=1)
        size_combo.bind("<<ComboboxSelected>>", self.format_font_size)
        ToolTip(size_combo, "Font Size")

        ttk.Separator(row1, orient='vertical').pack(side="left", fill="y", padx=3)

        # Section: Structure
        _btn(row1, "•",  self.insert_bullet, 'Accent.TButton', 2, "Insert Bullet")
        _btn(row1, "⇇", self.dedent_text,   'Accent.TButton', 2, "Decrease Indent (Shift+Tab)")
        _btn(row1, "⇉", self.insert_tab,    'Accent.TButton', 2, "Increase Indent (Tab)")

        ttk.Separator(row1, orient='vertical').pack(side="left", fill="y", padx=3)

        # Section: Media/Links
        _btn(row1, "📋", self.smart_paste,      'Accent.TButton', 3, "Smart Paste (image / HTML)")
        _btn(row1, "🔗", self.insert_hyperlink, 'Accent.TButton', 3, "Insert Hyperlink")
        _btn(row1, "🖼️", self.insert_image,     'Accent.TButton', 3, "Insert Image")

        ttk.Separator(row1, orient='vertical').pack(side="left", fill="y", padx=3)

        # Section: History
        _btn(row1, "↶", self.undo_action, 'Gold.TButton', 2, "Undo (Ctrl+Z)")
        _btn(row1, "↷", self.redo_action, 'Gold.TButton', 2, "Redo (Ctrl+Y)")

        ttk.Separator(row1, orient='vertical').pack(side="left", fill="y", padx=3)

        # Section: Attachments (Ultra-Compact)
        if self.attach_files:
            _btn(row1, "📁 +", self.attach_files, 'Gold.TButton', 4, "Attach File")

        if self.attach_mgr and self.attach_status_var:
            ttk.Label(row1, textvariable=self.attach_status_var,
                      font=('Segoe UI', 8), foreground='#00E5FF').pack(side="left", padx=2)
            _btn(row1, "🗑️", self.attach_mgr, 'Gold.TButton', 3, "Manage Attachments")

        # Section: Help/Hint
        ttk.Separator(row1, orient='vertical').pack(side="left", fill="y", padx=3)
        _btn(row1, "💡 HINT", self.show_help_hint, 'Accent.TButton', 10, "Show Usage Guide")
        
        if self.theme_callback:
            _btn(row1, "🎨 Theme", self.show_theme_manager, 'Gold.TButton', 14, "Mission Aesthetics")
        
        if self.help_mission_callback:
             _btn(row1, "❓ HELP", self.help_mission_callback, 'Gold.TButton', 10, "Mission Handbook")
        
        return toolbar_frame

    def show_theme_manager(self):
        """Opens a theme selection window centered below the button"""
        # Look one level up from core/ then into assets/
        themes_file = Path(__file__).parent.parent / "assets" / "themes.json"
        
        # Fallback for non-restructured launches
        if not themes_file.exists():
            themes_file = Path(__file__).parent / "themes.json"
            
        if not themes_file.exists():
            messagebox.showerror("Error", "themes.json not found!")
            return
            
        with open(themes_file, 'r') as f:
            themes = json.load(f)
            
        theme_win = tk.Toplevel(self.root)
        theme_win.title("Mission Aesthetics - Eras of History")
        theme_win.geometry("450x550")
        theme_win.configure(bg=RichToolTip.theme_bg)
        theme_win.transient(self.root)
        theme_win.grab_set()
        
        header = tk.Label(theme_win, text="🎨 SELECT MISSION THEME", font=('Segoe UI', 14, 'bold'),
                         bg=RichToolTip.theme_bg, fg=ToolTip.theme_fg, pady=15)
        header.pack(fill="x")
        
        # Group themes by era
        eras = {
            "🏺 Antiquity": ["Pharaonic Gold (Antiquity)", "Imperial Marble (Antiquity)"],
            "🏰 Middle Ages": ["Vanguard Steel (Middle Ages)", "Cathedral Night (Middle Ages)"],
            "🎨 Renaissance": ["Da Vinci Canvas (Renaissance)", "Medici Velvet (Renaissance)"],
            "⚙️ Industrial": ["Clockwork Brass (Industrial)", "Victorian Elegance (Industrial)"],
            "🚀 Future": ["Neon Grid (Future)", "Neural Void (Future)"]
        }
        
        def pick_theme(name):
            self.theme_callback(name)
            theme_win.destroy()
            self.log_message(f"✅ Theme changed to: {name}")

        container = tk.Frame(theme_win, bg=RichToolTip.theme_bg)
        container.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Use a grid layout with wrap-around capability
        current_row = 0
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

        for era, theme_list in eras.items():
            era_lbl = tk.Label(container, text=era, font=('Segoe UI', 10, 'bold'), 
                              bg=RichToolTip.theme_bg, fg=ToolTip.theme_fg, pady=8)
            era_lbl.grid(row=current_row, column=0, columnspan=2, sticky="w", pady=(10, 2))
            current_row += 1
            
            col_idx = 0
            for t_name in theme_list:
                if t_name in themes:
                    t_data = themes[t_name]
                    # Create a preview-colored frame for each theme button
                    btn_frame = tk.Frame(container, bg=t_data['bg'], padx=2, pady=2, bd=1, relief="solid")
                    btn_frame.grid(row=current_row, column=col_idx, sticky="ew", padx=3, pady=3)
                    
                    btn = tk.Button(btn_frame, text=t_name.split(" (")[0], 
                                   command=lambda n=t_name: pick_theme(n),
                                   bg=t_data['btn_bg'], fg=t_data['btn_fg'],
                                   font=('Segoe UI', 9, 'bold'), relief='flat', 
                                   activebackground=t_data['btn_hover'],
                                   cursor="hand2")
                    btn.pack(fill="x")
                    
                    # Colors preview strip (Aqua/Accent indicator)
                    strip = tk.Frame(btn_frame, height=3, bg=t_data['aqua'])
                    strip.pack(fill="x")

                    col_idx += 1
                    if col_idx > 1: # Wrap to next row
                        col_idx = 0
                        current_row += 1
            
            # If we ended on col 1, move to next row for next era
            if col_idx == 1:
                current_row += 1

        footer = ttk.Button(theme_win, text="CANCEL", command=theme_win.destroy)
        footer.pack(pady=15)

    def show_help_hint(self):
        """Displays a copyable popup with usage instructions"""
        help_win = tk.Toplevel(self.root)
        help_win.title("Mission Intelligence - Hints")
        help_win.geometry("500x550")
        
        # Use current theme colors
        bg_color = RichToolTip.theme_bg
        fg_color = RichToolTip.theme_fg
        highlight = ToolTip.theme_fg
        
        help_win.configure(bg=bg_color)
        
        header = tk.Label(help_win, text="🚀 QUICK OPERATIONAL GUIDE", font=('Segoe UI', 12, 'bold'), 
                         bg=bg_color, fg=highlight, pady=10)
        header.pack(fill="x")
        
        help_text = """1. 📎 LOAD: Select a CSV or TXT file. 
- Column A: Email addresses (use ';' for multiple)
- Column B: Names (Target for {name})
- Column E: CC addresses

2. 👥 CC Checkbox: Enable this to process Column E and send copies.

3. 📑 LIST: Click this to view and verify all loaded participants.

4. ✍️ Personalization:
- Use {name} to insert the person's name (from Column B).
- Use {email} to insert their email address.
- Works in both SUBJECT and BODY! (Case-insensitive)

5. 📁 + & 🗑️: Attach additional files (25MB limit) or manage them.

6. 🧪 TEST: Always test your SMTP credentials before a large launch!

Copy any text from this box if needed:"""
        
        # Use a Text widget so it's copyable
        text_area = tk.Text(help_win, wrap=tk.WORD, font=('Segoe UI', 10), bg=bg_color, 
                           fg=fg_color, padx=15, pady=15, bd=1, relief="solid")
        text_area.insert('1.0', help_text)
        text_area.config(state='disabled') # Read only but selectable
        text_area.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Footer
        footer_btn = ttk.Button(help_win, text="DISMISS", command=help_win.destroy)
        footer_btn.pack(pady=10)

    # --- Formatting Methods ---
    def format_bold(self):
        try:
            if self.body_text.tag_ranges(tk.SEL):
                self.body_text.tag_add("bold", tk.SEL_FIRST, tk.SEL_LAST)
                self.set_html_mode()
                self.log_message("✅ Applied Bold")
            else: messagebox.showinfo("Bold", "Select text first.")
        except: pass

    def format_italic(self):
        try:
            if self.body_text.tag_ranges(tk.SEL):
                self.body_text.tag_add("italic", tk.SEL_FIRST, tk.SEL_LAST)
                self.set_html_mode()
                self.log_message("✅ Applied Italic")
            else: messagebox.showinfo("Italic", "Select text first.")
        except: pass
        
    def format_color(self):
        try:
            if not self.body_text.tag_ranges(tk.SEL):
                messagebox.showinfo("Color", "Select text first.")
                return
            color = colorchooser.askcolor(title="Choose Font Color")[1]
            if color:
                tag_name = f"color_{color}"
                self.body_text.tag_config(tag_name, foreground=color)
                self.body_text.tag_add(tag_name, tk.SEL_FIRST, tk.SEL_LAST)
                self.set_html_mode()
                self.log_message(f"✅ Applied Color: {color}")
        except: pass

    def format_font_size(self, event=None):
        try:
            size = int(self.font_size_var.get())
            if self.body_text.tag_ranges(tk.SEL):
                tag_name = f"size_{size}"
                self.body_text.tag_config(tag_name, font=('Segoe UI', size))
                self.body_text.tag_add(tag_name, tk.SEL_FIRST, tk.SEL_LAST)
                self.set_html_mode()
                self.body_text.focus_set()
        except: pass

    def insert_bullet(self):
        try:
            self.body_text.insert(tk.INSERT, "• ")
            self.set_html_mode()
        except: pass

    def insert_tab(self):
        try:
            self.body_text.insert(tk.INSERT, "    ")
            return True
        except: return False

    def dedent_text(self):
        try:
            # Simple dedent implementation
            current_idx = self.body_text.index(tk.INSERT)
            line_start = f"{current_idx.split('.')[0]}.0"
            line_text = self.body_text.get(line_start, f"{line_start} lineend")
            if line_text.startswith("    "):
                self.body_text.delete(line_start, f"{line_start}+4c")
            elif line_text.startswith("\t"):
                self.body_text.delete(line_start, f"{line_start}+1c")
            elif line_text.startswith("• "):
                self.body_text.delete(line_start, f"{line_start}+2c")
            return True
        except: return False

    def insert_hyperlink(self):
        try:
            url = simpledialog.askstring("URL", "Enter URL:")
            if url:
                if self.body_text.tag_ranges(tk.SEL):
                    self.body_text.delete(tk.SEL_FIRST, tk.SEL_LAST)
                
                # Insert Text
                start = self.body_text.index(tk.INSERT)
                self.body_text.insert(tk.INSERT, url)
                end = self.body_text.index(tk.INSERT)
                
                self._apply_link_tag(url, start, end)
                self.log_message("✅ Link inserted")
        except: pass

    def insert_image(self):
        try:
            choice = messagebox.askquestion("Insert Image", "Insert from file?\n(Yes=File, No=Clipboard)")
            if choice == 'yes':
                file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp")])
                if file_path: self._insert_image_from_path(file_path)
            else:
                content = ImageGrab.grabclipboard()
                if isinstance(content, list): 
                    for f in content: self._insert_image_from_path(f)
                elif content: 
                    self._insert_image_from_data(content)
                else:
                    messagebox.showinfo("Info", "No image found in clipboard")
        except Exception as e:
             messagebox.showerror("Error", str(e))

    def smart_paste(self):
        try:
            content = ImageGrab.grabclipboard()
            if isinstance(content, list):
                for f in content:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                        self._insert_image_from_path(f)
                        return
            elif content and hasattr(content, 'save'):
                self._insert_image_from_data(content)
                return

            html_content = RichContentManager.get_html_from_clipboard()
            # Just paste text for now to be safe, HTML parsing is complex
            self.body_text.event_generate("<<Paste>>")
            self.root.after(100, self.check_auto_link)
        except:
             self.body_text.event_generate("<<Paste>>")

    # --- Helpers ---
    def _insert_image_from_path(self, path):
        with open(path, 'rb') as f: self._process_image(f.read())
    
    def _insert_image_from_data(self, img_obj):
        buffer = io.BytesIO()
        img_obj.save(buffer, format='PNG')
        self._process_image(buffer.getvalue())

    def _process_image(self, raw_data):
        pil_img = Image.open(io.BytesIO(raw_data))
        if pil_img.width > 500:
            ratio = 500 / pil_img.width
            pil_img = pil_img.resize((500, int(pil_img.height * ratio)))
            
        tk_img = ImageTk.PhotoImage(pil_img)
        self.images.append(tk_img) # Keep reference
        
        b64_str = base64.b64encode(raw_data).decode('utf-8')
        self.images_data.append(b64_str)
        
        self.body_text.image_create(tk.INSERT, image=tk_img, align='baseline')
        self.body_text.insert(tk.INSERT, "\n")
        self.set_html_mode()

    def check_auto_link(self, event=None):
        try:
            current_index = self.body_text.index(tk.INSERT)
            line_num = int(current_index.split('.')[0])
            
            # Check previous line
            if line_num > 1:
                self._scan_line_for_links(line_num - 1)
            self._scan_line_for_links(line_num)
        except: pass

    def _scan_line_for_links(self, line_num):
        text = self.body_text.get(f"{line_num}.0", f"{line_num}.end")
        url_pattern = re.compile(r'(https?://\S+|www\.\S+)')
        for match in url_pattern.finditer(text):
            url = match.group()
            self._apply_link_tag(url, f"{line_num}.0 + {match.start()} chars", f"{line_num}.0 + {match.end()} chars")

    def _apply_link_tag(self, url, start, end):
        real_url = url if url.startswith(('http://', 'https://')) else 'https://' + url
        tag_name = f"link_{real_url}"
        self.body_text.tag_config(tag_name, foreground="blue", underline=True)
        self.body_text.tag_add(tag_name, start, end)
        self.body_text.tag_bind(tag_name, "<Button-1>", lambda e, u=real_url: self._handle_link_click(e, u))
        self.set_html_mode()

    def _handle_link_click(self, event, url=None):
        if not url:
            # find tag at index
            index = self.body_text.index(f"@{event.x},{event.y}")
            tags = self.body_text.tag_names(index)
            for t in tags:
                if t.startswith("link_"):
                    url = t.replace("link_", "")
                    break
        if url: webbrowser.open(url)

    # --- HTML Generation ---
    def _tag_open_html(self, tag_name):
        """Return the opening HTML for a given internal tag name."""
        if tag_name == "bold":
            return "<b>"
        if tag_name == "italic":
            return "<i>"
        if tag_name.startswith("color_"):
            color = tag_name[len("color_"):]
            return f'<span style="color:{color}">'
        if tag_name.startswith("size_"):
            size = tag_name[len("size_"):]
            return f'<span style="font-size:{size}pt">'
        if tag_name.startswith("link_"):
            url = tag_name[len("link_"):]
            return f'<a href="{url}">'
        return ""

    def _tag_close_html(self, tag_name):
        """Return the closing HTML for a given internal tag name."""
        if tag_name == "bold":   return "</b>"
        if tag_name == "italic": return "</i>"
        if tag_name.startswith(("color_", "size_")): return "</span>"
        if tag_name.startswith("link_"):             return "</a>"
        return ""

    def generate_html(self):
        if not self.body_text: return ""
        html = ["<html><body><p>"]
        content = self.body_text.dump('1.0', tk.END, tag=True, text=True, image=True)
        img_idx = 0

        # Track currently-open inline tags in order so we can close/reopen them
        # across paragraph breaks introduced by newlines.
        active_tags = []  # ordered list of tag names currently open

        _RELEVANT = {"bold", "italic"}
        def _is_relevant(tag):
            return (tag in _RELEVANT or
                    tag.startswith("color_") or
                    tag.startswith("size_") or
                    tag.startswith("link_"))

        for key, value, _ in content:
            if key == "tagon":
                open_html = self._tag_open_html(value)
                if open_html:
                    if _is_relevant(value):
                        active_tags.append(value)
                    html.append(open_html)

            elif key == "tagoff":
                close_html = self._tag_close_html(value)
                if close_html:
                    if value in active_tags:
                        active_tags.remove(value)
                    html.append(close_html)

            elif key == "text":
                # Escape HTML entities first
                safe = (value
                        .replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;"))
                # Split on newlines and use <br/> for line breaks instead of new paragraphs
                # to avoid extra vertical spacing in email clients.
                parts = safe.split("\n")
                for i, part in enumerate(parts):
                    html.append(part)
                    if i < len(parts) - 1:
                        html.append("<br/>")

            elif key == "image":
                if img_idx < len(self.images_data):
                    html.append(
                        f'<img src="data:image/png;base64,{self.images_data[img_idx]}"'
                        f' style="max-width:100%;">'
                    )
                    img_idx += 1

        html.append("</p></body></html>")
        return "".join(html).replace("<p></p>", "")

    # --- Undo/Redo (debounced snapshot, 50-step history) ---
    def _commit_snapshot(self):
        """Push a snapshot onto undo_stack; called after 500 ms of inactivity."""
        self._undo_timer = None
        content = self.body_text.get('1.0', tk.END)
        if not self.undo_stack or self.undo_stack[-1] != content:
            self.undo_stack.append(content)
            if len(self.undo_stack) > self.max_undo_steps:
                self.undo_stack.pop(0)
            self.redo_stack.clear()

    def on_text_modified(self, event=None):
        """Schedule a snapshot 500 ms after the last keystroke (debounce)."""
        if self.body_text.edit_modified():
            self.body_text.edit_modified(False)
            # Cancel any pending snapshot
            if self._undo_timer is not None:
                self.body_text.after_cancel(self._undo_timer)
            self._undo_timer = self.body_text.after(500, self._commit_snapshot)

    def undo_action(self):
        """Step back one snapshot. Saves current state to redo_stack first."""
        # Flush any pending debounced snapshot immediately
        if self._undo_timer is not None:
            self.body_text.after_cancel(self._undo_timer)
            self._undo_timer = None
            self._commit_snapshot()

        if len(self.undo_stack) > 1:
            # Save current text to redo before going back
            current = self.body_text.get('1.0', tk.END)
            # If we haven't already saved this state at the top of redo_stack
            if not self.redo_stack or self.redo_stack[-1] != current:
                self.redo_stack.append(self.undo_stack.pop())  # pop the 'current' snapshot
            else:
                self.undo_stack.pop()
            # Restore the previous snapshot
            self.body_text.delete('1.0', tk.END)
            self.body_text.insert('1.0', self.undo_stack[-1])
            self.log_message(f"↶ Undo  ({len(self.undo_stack)} steps left)")

    def redo_action(self):
        """Step forward one snapshot."""
        if self.redo_stack:
            content = self.redo_stack.pop()
            # Push onto undo so we can undo again
            if not self.undo_stack or self.undo_stack[-1] != content:
                self.undo_stack.append(content)
            self.body_text.delete('1.0', tk.END)
            self.body_text.insert('1.0', content)
            self.log_message(f"↷ Redo  ({len(self.redo_stack)} redos left)")
