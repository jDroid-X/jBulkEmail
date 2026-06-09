import tkinter as tk

class RoundedButton(tk.Canvas):
    """
    Custom button with rounded corners.
    Hierarchy Level: Shared Widget.
    """
    def __init__(self, parent, text="", command=None, bg="#00E5FF", fg="#000000", 
                 hover_bg="#00B8D4", active_bg="#00838F", width=100, height=30, 
                 corner_radius=15, font=('Segoe UI', 8, 'bold'), **kwargs):
        try:
            parent_bg = parent.cget('bg')
        except:
            parent_bg = '#808080' # Default grey
            
        super().__init__(parent, width=width, height=height, bg=parent_bg, 
                        highlightthickness=0, **kwargs)
        
        self.command = command
        self.bg = bg
        self.fg = fg
        self.hover_bg = hover_bg
        self.active_bg = active_bg
        self.corner_radius = corner_radius
        self.text = text
        self.font = font
        self.is_hovered = False
        self.is_pressed = False
        
        # Draw button
        self.draw_button()
        
        # Bind events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        
    def _draw_rounded_rect(self, canvas, w, h, r, color):
        canvas.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=color, outline=color)
        canvas.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, fill=color, outline=color)
        canvas.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, fill=color, outline=color)
        canvas.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, fill=color, outline=color)
        canvas.create_rectangle(r, 0, w-r, h, fill=color, outline=color)
        canvas.create_rectangle(0, r, w, h-r, fill=color, outline=color)

    def draw_button(self):
        self.delete("all")
        color = self.active_bg if self.is_pressed else (self.hover_bg if self.is_hovered else self.bg)
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        self._draw_rounded_rect(self, w, h, self.corner_radius, color)
        self.create_text(w/2, h/2, text=self.text, fill=self.fg, font=self.font)
        
    def on_enter(self, event):
        self.is_hovered = True
        self.draw_button()
        self.config(cursor="hand2")
        
    def on_leave(self, event):
        self.is_hovered = False
        self.is_pressed = False
        self.draw_button()
        
    def on_press(self, event):
        self.is_pressed = True
        self.draw_button()
        
    def on_release(self, event):
        self.is_pressed = False
        self.draw_button()
        if self.command and self.is_hovered:
            self.command()
