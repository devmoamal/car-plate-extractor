import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw, ImageOps
import main
import threading
import os
import time

# --- Ultra-Focus Color Palette ---
BG_DARK = "#0a0f1d"        # Deep midnight blue
BG_CARD = "#161e31"        # Slate blue card BG
ACCENT = "#38bdf8"         # Electric sky blue
TEXT_MAIN = "#f8fafc"      # Crisp off-white text
TEXT_DIM = "#64748b"       # Muted slate text
SUCCESS = "#10b981"        # Emerald green
CARD_BORDER = "#1e293b"    # Subtle border

class AnimatedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=180, height=48, active=True):
        super().__init__(parent, width=width, height=height, bg=BG_DARK, highlightthickness=0, cursor="hand2")
        self.command = command
        self.text = text
        self.width = width
        self.height = height
        self.is_enabled = active
        
        self.rect_id = self.create_rounded_rect(2, 2, width-2, height-2, 12, fill=BG_CARD, outline=ACCENT, width=1)
        self.text_id = self.create_text(width/2, height/2, text=text, fill=TEXT_MAIN, font=("Inter", 10, "bold"))
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def set_state(self, enabled):
        self.is_enabled = enabled
        if enabled:
            self.itemconfig(self.rect_id, fill=BG_CARD, outline=ACCENT)
            self.itemconfig(self.text_id, fill=TEXT_MAIN)
            self.config(cursor="hand2")
        else:
            self.itemconfig(self.rect_id, fill="#0f172a", outline="#334155")
            self.itemconfig(self.text_id, fill="#475569")
            self.config(cursor="arrow")

    def on_enter(self, e):
        if self.is_enabled:
            self.itemconfig(self.rect_id, fill="#0ea5e9", outline=ACCENT)

    def on_leave(self, e):
        if self.is_enabled:
            self.itemconfig(self.rect_id, fill=BG_CARD, outline=ACCENT)

    def on_click(self, e):
        if self.is_enabled:
            self.command()

class UltimatePlateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoPlate Pro - Ultimate Edition")
        self.root.geometry("1100x850")
        self.root.configure(bg=BG_DARK)
        
        self.setup_styles()
        self.setup_ui()
        self.current_image_path = None
        self.processing = False

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Premium.Horizontal.TProgressbar", troughcolor=BG_DARK, bordercolor=BG_DARK, background=ACCENT, thickness=4)

    def setup_ui(self):
        # --- Top Header (Centered) ---
        header = tk.Frame(self.root, bg=BG_DARK, pady=30)
        header.pack(fill=tk.X)
        
        tk.Label(header, text="AUTOPLATE PRO", font=("Inter", 28, "bold"), fg=ACCENT, bg=BG_DARK).pack()
        tk.Label(header, text="Unified AI Intelligence", font=("Inter", 11), fg=TEXT_DIM, bg=BG_DARK).pack()

        # --- Main Workspace (Grid based for center focus) ---
        self.workspace = tk.Frame(self.root, bg=BG_DARK)
        self.workspace.pack(expand=True, fill=tk.BOTH, padx=60)
        
        # Grid Configuration
        self.workspace.columnconfigure(0, weight=3) # Left (Image)
        self.workspace.columnconfigure(1, weight=1) # Right (Controls)

        # 1. Image Preview Wall
        self.wall_frame = tk.Frame(self.workspace, bg=BG_DARK)
        self.wall_frame.grid(row=0, column=0, sticky="nsew", padx=10)
        
        self.img_card = tk.Frame(self.wall_frame, bg=BG_CARD, highlightthickness=1, highlightbackground=CARD_BORDER)
        self.img_card.pack(expand=True, fill=tk.BOTH)
        
        self.img_label = tk.Label(self.img_card, text="CLICK 'SELECT PHOTO' TO START", bg=BG_CARD, fg=TEXT_DIM, font=("Inter", 10, "bold"))
        self.img_label.pack(expand=True, fill=tk.BOTH)

        # 2. Control Terminal
        self.terminal = tk.Frame(self.workspace, bg=BG_DARK, padx=40)
        self.terminal.grid(row=0, column=1, sticky="nsew")
        
        self.select_btn = AnimatedButton(self.terminal, "SELECT PHOTO", self.select_image)
        self.select_btn.pack(pady=(0, 20))
        
        self.process_btn = AnimatedButton(self.terminal, "IDENTIFY PLATE", self.process_image_async)
        self.process_btn.set_state(False)
        self.process_btn.pack(pady=10)
        
        # Status Monitoring
        self.pbar = ttk.Progressbar(self.terminal, style="Premium.Horizontal.TProgressbar", length=220, mode='indeterminate')
        self.pbar.pack(pady=30)
        
        self.status_main = tk.Label(self.terminal, text="SYSTEM IDLE", fg=TEXT_DIM, bg=BG_DARK, font=("Inter", 9, "bold"))
        self.status_main.pack(anchor=tk.W)
        
        self.status_detail = tk.Label(self.terminal, text="Waiting for telemetry input...", fg="#475569", bg=BG_DARK, font=("Inter", 8))
        self.status_detail.pack(anchor=tk.W)

        # --- Dynamic Results (Focused at bottom) ---
        results_header = tk.Frame(self.root, bg=BG_DARK)
        results_header.pack(fill=tk.X, padx=60, pady=(20, 0))
        tk.Label(results_header, text="DETECTION RECAP", font=("Inter", 9, "bold"), fg=TEXT_DIM, bg=BG_DARK).pack(side=tk.LEFT)

        self.results_belt = tk.Frame(self.root, bg=BG_DARK, height=180)
        self.results_belt.pack(fill=tk.BOTH, expand=False, padx=60, pady=(10, 50))
        self.results_belt.pack_propagate(False)

    def set_app_state(self, busy=True):
        self.processing = busy
        self.select_btn.set_state(not busy)
        self.process_btn.set_state(not busy)
        if busy: self.pbar.start(15)
        else: self.pbar.stop()

    def select_image(self):
        if self.processing: return
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg *.webp")])
        if not path: return
        
        self.current_image_path = path
        self.display_image(path)
        self.process_btn.set_state(True)
        self.status_main.config(text="TELEMETRY LOADED", fg=ACCENT)
        self.clear_results()

    def display_image(self, path):
        img = Image.open(path)
        img = ImageOps.exif_transpose(img)
        img.thumbnail((650, 550))
        
        # Round the edges
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0) + img.size, radius=20, fill=255)
        img.putalpha(mask)
        
        self.photo = ImageTk.PhotoImage(img)
        self.img_label.config(image=self.photo, text="", bg=BG_DARK)

    def clear_results(self):
        for w in self.results_belt.winfo_children(): w.destroy()

    def process_image_async(self):
        if not self.current_image_path or self.processing: return
        
        self.set_app_state(True)
        self.status_main.config(text="ANALYZING PLATE", fg=ACCENT)
        self.clear_results()
        threading.Thread(target=self.run_ocr, daemon=True).start()

    def run_ocr(self):
        try:
            res = main.get_plate_numbers(self.current_image_path)
            time.sleep(1) # Visual hold to see animations
            self.root.after(0, self.render_results, res)
        except Exception as e:
            self.root.after(0, lambda: self.set_app_state(False))
            self.root.after(0, lambda: self.status_main.config(text="FAILED", fg="#f43f5e"))

    def render_results(self, res):
        self.set_app_state(False)
        if not res:
            self.status_main.config(text="NO PLATE FOUND", fg=TEXT_DIM)
            return

        self.status_main.config(text="IDENTIFIED", fg=SUCCESS)
        
        for i, (text, prob, _) in enumerate(res):
            self.root.after(i * 150, lambda t=text, p=prob, top=(i==0): self.add_card(t, p, top))

    def add_card(self, text, prob, is_top):
        frame = tk.Frame(self.results_belt, bg=BG_DARK, pady=10)
        frame.pack(side=tk.LEFT, padx=10)
        
        # Top result gets a glowing border
        color = SUCCESS if is_top else ACCENT
        card = tk.Frame(frame, bg=BG_CARD, highlightthickness=2 if is_top else 1, highlightbackground=color, padx=30, pady=25)
        card.pack()
        
        tk.Label(card, text=text, font=("Inter", 24 if is_top else 18, "bold"), fg=TEXT_MAIN, bg=BG_CARD).pack()
        tk.Label(card, text=f"{prob*100:.1f}% Confidence", font=("Inter", 9), fg=color, bg=BG_CARD).pack(pady=(5, 0))

if __name__ == "__main__":
    root = tk.Tk()
    # Auto-adjust scaling for macOS Retina
    root.tk.call('tk', 'scaling', 2.0)
    app = UltimatePlateApp(root)
    root.mainloop()
