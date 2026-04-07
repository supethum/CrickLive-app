import tkinter as tk
import base64

ICON_DATA = {
    "ball": "R0lGODlhFAAUAOYAAAAAAIGBgTMzM/9mM/9mZpn/Zsz/ZswzMzNmZv//zP//ZmYzM2ZmZpmZmczMzP///wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAAIALAAAAAAUABQAAAdvgIKDhIWGh4iJIgAClYyNkpOUlZaFmI2cnZ6foKEADqKlqKmqq6ytrq+wRQOytLW2t7i5uru8vRYAvsDBwsPExcbHyMnKygAZzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHzIQAh+QQBAAACACwAAAAAFAAUAAAHb4CCg4SFhoeIiSIABJWMjZKTlJWWg5iNnJ2en6ChAA+ipaiplQOur7CxsrO0tba3uLm6u7y9vr/AwcLDxMXGx8jJysvMzRYA0NHS09TV1tfY2drb3N3e3+Dh4uPk5ebn6Onq6+zt7u/w8fLz9PX29yEAIfkEAQAAAgAsAAAAABQAFAAAB2+AgoOEhYaHiIkiAASVjI2Sk5SVloOYjZydnp+goQAPoqWoqZUDrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM0WANHS09TV1tfY2drb3N3e3+Dh4uPk5ebn6Onq6+zt7u/w8fLz9PX29yEAOw==",
    "bat": "R0lGODlhFAAUAOYAAAAAAP///8zMzJmZmTMzM////2ZmZswzMwAzZgAzzAAzZmYAZpkAmZkAmWYAmcwAnMwAnpkAnWYAnWYAAGYAmQAAmQAAZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAAIALAAAAAAUABQAAAdvgIKDhIWGh4iJigAClYyNkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vMiACH5BAEAAAIALAAAAAAUABQAAAdvgIKDhIWGh4iJigADlYyNkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vMiACH5BAEAAAIALAAAAAAUABQAAAdvgIKDhIWGh4iJigADlYyNkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vMiADs=",
    "out": "R0lGODlhFAAUAOYAAAAAAP///wAAAP8AAP8zM/9mM/9mZjNmZv//zP//Zv//M8wzMzMzM2ZmZpmZmczMzP///wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAAIALAAAAAAUABQAAAdtgIKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8CEAOw==",
    "undo": "R0lGODlhFAAUAOYAAAAAAP///zMzM/9mM////5mZmf8zM2ZmZv//zP//ZmYzM8wzM2ZmZszMzJmZmQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAAIALAAAAAAUABQAAAdtgIKDhIWGh4iJioSMjY6PkJGSgwAClZeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8CEAOw=="
}

COLORS = {
    "bg_body": "#0F0F0F", 
    "bg_panel": "#18181B",
    "bg_card": "#27272A",
    "bg_input": "#2D2D30",
    "primary": "#3B82F6", 
    "primary_dark": "#1D4ED8",
    "accent": "#10B981",
    "danger": "#EF4444", 
    "warning": "#F59E0B", 
    "text_white": "#FAFAFA",
    "text_gray": "#A1A1AA", 
    "text_muted": "#52525B", 
    "border": "#3F3F46", 
    
    "btn_run": "#2563EB", 
    "btn_undo": "#0D9488", 
    "btn_extra": "#D97706", 
    "btn_out": "#DC2626", 
}

FONT_HEADER = ("Segoe UI", 16, "bold")
FONT_SCORE = ("Segoe UI", 48, "bold")
FONT_BTN = ("Segoe UI", 12, "bold")
FONT_SML = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 11, "bold")

def get_acronym(name):
    if not name: return ""
    return "".join([w[0].upper() for w in name.split() if w])

class ModernButton(tk.Button):
    def __init__(self, master, **kwargs):
        self.bg_color = kwargs.pop("bg", COLORS["bg_card"])
        self.fg_color = kwargs.pop("fg", COLORS["text_white"])
        self.hover_color = kwargs.pop("hover", None) 
        self.corner_radius = kwargs.pop("corner_radius", 8)
        
        if not self.hover_color:
             self.hover_color = self._adjust_color(self.bg_color, 20)

        super().__init__(master, **kwargs)
        
        self.configure(
            bg=self.bg_color, 
            fg=self.fg_color, 
            relief="flat", 
            bd=0,
            activebackground=self.hover_color, 
            activeforeground=self.fg_color,
            cursor="hand2", 
            highlightthickness=0,
            font=kwargs.pop("font", FONT_BTN),
            padx=kwargs.pop("padx", 8),
            pady=kwargs.pop("pady", 8),
            borderwidth=0
        )
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Configure>", self._on_configure)
        
    def _on_enter(self, event):
        self.config(bg=self.hover_color)
        self._draw_rounded_corners(self.hover_color)
        
    def _on_leave(self, event):
        self.config(bg=self.bg_color)
        self._draw_rounded_corners(self.bg_color)
        
    def _on_configure(self, event):
        self._draw_rounded_corners(self.bg_color)

    def _draw_rounded_corners(self, color):
        try:
            for child in self.master.winfo_children():
                if isinstance(child, tk.Canvas) and hasattr(child, '_rounded_btn'):
                    child.destroy()
            
            self.update_idletasks()
            x = self.winfo_x()
            y = self.winfo_y()
            width = self.winfo_width()
            height = self.winfo_height()
            
            if width > 1 and height > 1:
                canvas = tk.Canvas(self.master, width=width, height=height, 
                                 bg=self.master['bg'], highlightthickness=0)
                canvas._rounded_btn = True
                canvas.place(x=x, y=y)
                
                r = self.corner_radius
                points = [
                    r, 0, width-r, 0, width, r, width, height-r, 
                    width-r, height, r, height, 0, height-r, 0, r
                ]
                canvas.create_polygon(points, fill=color, smooth=True, splinesteps=12)
                self.lift()
        except:
            pass

    def _adjust_color(self, hex_color, amount):
        if not hex_color.startswith("#"): return hex_color
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            r = min(255, r + amount)
            g = min(255, g + amount)
            b = min(255, b + amount)
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color

class ModernEntry(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=COLORS["border"], padx=1, pady=1)
        self.entry = tk.Entry(self, 
            relief="flat",
            bg=COLORS["bg_input"],
            fg="white",
            insertbackground="white",
            highlightthickness=0,
            font=("Segoe UI", 11)
        )
        self.entry.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.entry.bind("<FocusIn>", self._on_focus)
        self.entry.bind("<FocusOut>", self._on_unfocus)
        self.entry.bind("<KeyRelease>", self._on_key)
        self.callback = None

    def _on_focus(self, e): self.config(bg=COLORS["primary"])
    def _on_unfocus(self, e): self.config(bg=COLORS["border"])
    def _on_key(self, e): 
        if self.callback: self.callback(e)
    def insert(self, idx, text): self.entry.insert(idx, text)
    def get(self): return self.entry.get()
    def bind(self, event, func): 
        if event == "<KeyRelease>": self.callback = func
        else: self.entry.bind(event, func)

class ModernText(tk.Frame):
    def __init__(self, master, height=8, **kwargs):
        super().__init__(master, bg=COLORS["border"], padx=1, pady=1)
        self.text = tk.Text(self,
            height=height,
            relief="flat",
            bg=COLORS["bg_input"],
            fg="white",
            insertbackground="white",
            highlightthickness=0,
            font=("Segoe UI", 10),
            padx=5,
            pady=5
        )
        self.text.pack(fill="both", expand=True)
        self.text.bind("<FocusIn>", lambda e: self.config(bg=COLORS["primary"]))
        self.text.bind("<FocusOut>", lambda e: self.config(bg=COLORS["border"]))

    def insert(self, idx, text): self.text.insert(idx, text)
    def get(self, *args): return self.text.get(*args)
    def delete(self, *args): self.text.delete(*args)

def get_icons_dict():
    icons = {}
    for name, b64 in ICON_DATA.items():
        icons[name] = tk.PhotoImage(data=base64.b64decode(b64))
    return icons

def create_popup_window(root, width, height, title):
    top = tk.Toplevel(root)
    top.configure(bg=COLORS["bg_panel"])
    top.overrideredirect(True)
    
    x = root.winfo_x() + (root.winfo_width() // 2) - (width // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (height // 2)
    top.geometry(f"{width}x{height}+{int(x)}+{int(y)}")
    
    frame = tk.Frame(top, bg=COLORS["bg_panel"], highlightbackground=COLORS["primary"], highlightthickness=1)
    frame.pack(fill="both", expand=True)
    tk.Label(frame, text=title, font=("Segoe UI", 12, "bold"), bg=COLORS["bg_panel"], fg=COLORS["text_white"]).pack(pady=10)
    
    # Make draggable
    def start_move(event):
        top.x = event.x
        top.y = event.y

    def stop_move(event):
        top.x = None
        top.y = None

    def do_move(event):
        deltax = event.x - top.x
        deltay = event.y - top.y
        x = top.winfo_x() + deltax
        y = top.winfo_y() + deltay
        top.geometry(f"+{x}+{y}")

    frame.bind("<Button-1>", start_move)
    frame.bind("<ButtonRelease-1>", stop_move)
    frame.bind("<B1-Motion>", do_move)
    
    return top, frame

def create_btn_grid(parent, options, var_to_update, cols=4, command=None):
    frame = tk.Frame(parent, bg=COLORS["bg_panel"])
    frame.pack(fill="x", pady=5, padx=10)
    for i in range(cols): 
        frame.columnconfigure(i, weight=1)
    
    buttons = {}
    
    def on_click(val):
        var_to_update.set(val)
        for v, b in buttons.items():
            if v == val:
                b.configure(bg=COLORS["primary"], fg=COLORS["text_white"])
            else:
                b.configure(bg=COLORS["bg_input"], fg=COLORS["text_gray"])
        if command: 
            command()
                
    row, col = 0, 0
    for opt in options:
        val = opt["value"]
        text = opt["label"]
        is_selected = var_to_update.get() == val
        
        b = tk.Button(frame, text=text, font=FONT_SML, relief="flat", bd=0, cursor="hand2",
                     bg=COLORS["primary"] if is_selected else COLORS["bg_input"],
                     fg=COLORS["text_white"] if is_selected else COLORS["text_gray"],
                     command=lambda v=val: on_click(v))
        b.grid(row=row, column=col, padx=3, pady=3, sticky="nsew", ipady=5)
        buttons[val] = b
        
        col += 1
        if col >= cols:
            col = 0
            row += 1
            
    return frame
