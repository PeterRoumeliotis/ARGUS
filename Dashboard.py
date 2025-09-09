import threading, traceback, datetime
from models import ClientProfile
from app import run_discovery
from reporter import save_results, generate_todo

import tkinter as tk
from PIL import Image, ImageTk
import os
from typing import Optional

class DashboardApp:
    def _find_logo_path(self) -> Optional[str]:
        """Try to locate a logo image near the project.
        Searches current file dir, CWD, and common subfolders with common names."""
        base_dirs = [
            os.path.dirname(__file__),
            os.getcwd(),
            os.path.join(os.path.dirname(__file__), "assets"),
            os.path.join(os.path.dirname(__file__), "images"),
            os.path.join(os.path.dirname(__file__), "img"),
        ]
        candidates = [
            "ArgusLogo.png", "arguslogo.png", "ARGUSLogo.png",
            "logo.png", "Logo.png",
            "ArgusLogo.jpg", "logo.jpg",
        ]
        for d in base_dirs:
            for name in candidates:
                p = os.path.join(d, name)
                if os.path.exists(p):
                    return p
        return None

    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#222222")

        # Main frame
        self.main_frame = tk.Frame(self.root, bg="#222222")
        self.main_frame.pack(fill="both", expand=True)

        # Left panel (black) with logo
        self.left_panel = tk.Frame(self.main_frame, bg="#000000", width=420)
        self.left_panel.pack(side="left", fill="y")
        self.left_panel.pack_propagate(False)

        # Load and scale logo (robust path search)
        logo_path = self._find_logo_path()

        if logo_path:
            try:
                pil_logo = Image.open(logo_path)
                # Scale logo to fit nicely in the left panel
                logo_height = 180
                aspect = pil_logo.width / max(1, pil_logo.height)
                logo_width = int(logo_height * aspect)
                pil_logo = pil_logo.resize((logo_width, logo_height), Image.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(pil_logo)
                logo_label = tk.Label(self.left_panel, image=self.logo_img, bg="#000000")
                logo_label.place(relx=0.5, rely=0.3, anchor="center")
            except Exception:
                # Fallback: try Tk PhotoImage (handles PNG/GIF) without Pillow
                try:
                    self.logo_img = tk.PhotoImage(file=logo_path)
                    logo_label = tk.Label(self.left_panel, image=self.logo_img, bg="#000000")
                    logo_label.place(relx=0.5, rely=0.3, anchor="center")
                except Exception:
                    logo_label = tk.Label(self.left_panel, text="LOGO", fg="white", bg="#000000", font=("Arial", 32, "bold"))
                    logo_label.place(relx=0.5, rely=0.3, anchor="center")
        else:
            logo_label = tk.Label(self.left_panel, text="LOGO", fg="white", bg="#000000", font=("Arial", 32, "bold"))
            logo_label.place(relx=0.5, rely=0.3, anchor="center")

        # Right panel (gray) with card
        self.right_panel = tk.Frame(self.main_frame, bg="#222222")
        self.right_panel.pack(side="left", fill="both", expand=True)

        # Card frame (centered)
        self.card = tk.Frame(self.right_panel, bg="#333333", bd=0, relief="flat")
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=420, height=340)

        # Heading label
        heading = tk.Label(self.card, text="Dashboard", fg="#ffffff", bg="#333333",
                           font=("Arial", 24, "bold"))
        heading.pack(pady=(36, 32))

        # Button style
        button_style = {
            "bg": "#ffffff",
            "fg": "#000000",
            "activebackground": "#eeeeee",
            "activeforeground": "#000000",
            "relief": "solid",
            "borderwidth": 2,
            "font": ("Arial", 14, "bold"),
            "highlightthickness": 0,
            "bd": 0,
        }

        # Web Clear button
        btn_web_clear = tk.Button(
            self.card,
            text="Web Clear",
            height=2,
            command=self.show_web_clear_form,
            **button_style,
        )
        btn_web_clear.pack(fill="x", padx=40, pady=(0, 16))

        # Web Monitoring button
        btn_web_monitor = tk.Button(
            self.card, text="Web Monitoring", height=2, **button_style
        )
        btn_web_monitor.pack(fill="x", padx=40)

        # Bind Escape to quit fullscreen
        self.root.bind("<Escape>", lambda e: self.root.attributes('-fullscreen', False))

    def show_web_clear_form(self):
        # Clear right card and render a small form
        for w in self.card.winfo_children():
            w.destroy()

        # Make the card taller to fit the full form + buttons
        try:
            self.card.place_configure(height=520)
        except Exception:
            pass

        heading = tk.Label(self.card, text="Web Clear", fg="#ffffff", bg="#333333",
                           font=("Arial", 22, "bold"))
        heading.pack(pady=(24, 10))

        form = tk.Frame(self.card, bg="#333333")
        form.pack(fill="x", padx=32)

        # Full Name field
        lbl_name = tk.Label(form, text="Full Name", font=("Arial", 11), fg="#EDEDED", bg="#333333")
        lbl_name.pack(anchor="w", pady=(6, 4))

        self.webclear_name = tk.StringVar()
        ent_name = tk.Entry(
            form,
            textvariable=self.webclear_name,
            font=("Arial", 12),
            bg="#FFFFFF",
            fg="#000000",
            insertbackground="#000000",
            bd=0,
            highlightthickness=1,
            highlightbackground="#000000",
            highlightcolor="#000000"
        )
        ent_name.pack(fill="x", ipady=6)
        ent_name.focus_set()

        # City (optional)
        lbl_city = tk.Label(form, text="City (optional)", font=("Arial", 11), fg="#EDEDED", bg="#333333")
        lbl_city.pack(anchor="w", pady=(10, 4))
        self.webclear_city = tk.StringVar()
        ent_city = tk.Entry(
            form,
            textvariable=self.webclear_city,
            font=("Arial", 12),
            bg="#FFFFFF",
            fg="#000000",
            insertbackground="#000000",
            bd=0,
            highlightthickness=1,
            highlightbackground="#000000",
            highlightcolor="#000000"
        )
        ent_city.pack(fill="x", ipady=6)

        # State (optional)
        lbl_state = tk.Label(form, text="State (optional)", font=("Arial", 11), fg="#EDEDED", bg="#333333")
        lbl_state.pack(anchor="w", pady=(10, 4))
        self.webclear_state = tk.StringVar()
        ent_state = tk.Entry(
            form,
            textvariable=self.webclear_state,
            font=("Arial", 12),
            bg="#FFFFFF",
            fg="#000000",
            insertbackground="#000000",
            bd=0,
            highlightthickness=1,
            highlightbackground="#000000",
            highlightcolor="#000000"
        )
        ent_state.pack(fill="x", ipady=6)

        # Status + output
        self.webclear_status = tk.Label(self.card, text="", fg="#FFD166", bg="#333333", font=("Arial", 10))
        self.webclear_status.pack(anchor="w", padx=32, pady=(8, 0))

        # Progress bar row
        import tkinter.ttk as ttk
        self._progress_var = tk.IntVar(value=0)
        prog_row = tk.Frame(self.card, bg="#333333")
        prog_row.pack(fill="x", padx=32, pady=(6, 0))
        self._progress = ttk.Progressbar(prog_row, orient="horizontal", mode="determinate", maximum=100, variable=self._progress_var)
        self._progress.pack(fill="x")
        self._progress_label = tk.Label(self.card, text="", fg="#CCCCCC", bg="#333333", font=("Arial", 10))
        self._progress_label.pack(anchor="w", padx=32, pady=(2, 0))

        self.webclear_output = tk.Text(self.card, height=8, bg="#2A2A2A", fg="#EDEDED",
                                       insertbackground="#EDEDED", relief="flat", wrap="word")
        self.webclear_output.pack(fill="both", expand=True, padx=32, pady=(8, 0))
        self.webclear_output.config(state="disabled")

        # Buttons row
        row = tk.Frame(self.card, bg="#333333")
        row.pack(fill="x", padx=32, pady=16)

        def on_clear_click():
            name = (self.webclear_name.get() or "").strip()
            city = (self.webclear_city.get() or "").strip()
            state = (self.webclear_state.get() or "").strip()
            if not name:
                # inline status only
                self.webclear_status.config(text="Please enter the client’s full name.")
                return
            # disable while running
            btn_clear.config(state="disabled")
            self.webclear_status.config(text="Running discovery… please wait.")
            # reset progress
            self._progress_var.set(0)
            self._progress_label.config(text="Starting…")
            self.webclear_output.config(state="normal")
            self.webclear_output.delete("1.0", "end")
            self.webclear_output.config(state="disabled")

            t = threading.Thread(target=self._run_web_clear, args=(name, city, state, btn_clear), daemon=True)
            t.start()

        button_style = {
            "bg": "#ffffff",
            "fg": "#000000",
            "activebackground": "#eeeeee",
            "activeforeground": "#000000",
            "relief": "solid",
            "borderwidth": 2,
            "font": ("Arial", 14, "bold"),
            "highlightthickness": 0,
            "bd": 0,
        }

        btn_clear = tk.Button(row, text="Start Web Clear", height=2, command=on_clear_click, **button_style)
        btn_clear.pack(fill="x")

    def _run_web_clear(self, full_name: str, city: str, state: str, btn_clear: tk.Button):
        """
        Background worker: runs discovery, saves reports, and prints checklist.
        """
        try:
            profile = ClientProfile(name=full_name, city=(city or None), state=(state or None))

            def progress_cb(percent: int, message: str = ""):
                try:
                    self.root.after(0, self._update_progress, int(percent), message)
                except Exception:
                    pass

            # Include all sites listed in sites.json, even if marked disabled
            results = run_discovery(profile, progress_cb=progress_cb, include_disabled=True)

            # Save reports into reports/<slug>_<YYYYmmdd-HHMMSS>*
            ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            outdir = os.path.join("reports", full_name.lower().replace(" ", "_"))
            csv_path, json_path, txt_path = save_results(full_name, results, outdir)
            checklist = generate_todo(full_name, profile, results)

            # Update UI on main thread
            def done():
                self.webclear_status.config(
                    text=f"Done. Saved CSV/JSON in: {outdir}"
                )
                self.webclear_output.config(state="normal")
                self.webclear_output.insert("end", checklist + "\n")
                self.webclear_output.insert("end", f"\nSaved:\n- {csv_path}\n- {json_path}\n- {txt_path}\n")
                self.webclear_output.config(state="disabled")
                btn_clear.config(state="normal")

            self.root.after(0, done)

        except Exception as e:
            tb = traceback.format_exc()

            def fail():
                self.webclear_status.config(text=f"Error: {e}")
                self.webclear_output.config(state="normal")
                self.webclear_output.insert("end", tb)
                self.webclear_output.config(state="disabled")
                btn_clear.config(state="normal")

            self.root.after(0, fail)

    def _update_progress(self, percent: int, message: str):
        try:
            self._progress_var.set(max(0, min(100, int(percent))))
        except Exception:
            self._progress_var.set(0)
        self._progress_label.config(text=message or "")

def main():
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
