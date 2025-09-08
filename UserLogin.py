from Dashboard import DashboardApp
import tkinter as tk
from tkinter import messagebox, PhotoImage

# --- Simple demo user store (replace with real auth) ---
DEMO_USERS = {
    "PRoumeliotis@tmusallc.com": "password",
    "admin": "password",
}

class LoginApp:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("ARGUS • User Login")
        self.master.attributes('-fullscreen', True)
        self.master.configure(bg="#FFFFFF")
        # ESC to exit fullscreen for convenience
        self.master.bind('<Escape>', lambda _e: self.master.attributes('-fullscreen', False))

        # --- Root container with two columns (left: branding, right: form) ---
        container = tk.Frame(master, bg="#FFFFFF")
        container.pack(expand=True, fill=tk.BOTH)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        # LEFT PANE (branding)
        left = tk.Frame(container, bg="#000000")
        left.place(relx=0.0, rely=0.0, relwidth=0.65, relheight=1.0)

        # Centered branding block
        left_inner = tk.Frame(left, bg="#000000")
        left_inner.place(relx=0.5, rely=0.5, anchor="center")

        # Load logo (fallback to text if missing)
        self.logo_image = None
        try:
            self.logo_image = PhotoImage(file="ArgusLogo.png")
        except Exception:
            self.logo_image = None

        if self.logo_image is not None:
            logo_label = tk.Label(left_inner, image=self.logo_image, bg="#000000")
            logo_label.pack(pady=(0, 20))

        # RIGHT PANE (login form)
        right = tk.Frame(container, bg="#6E747B")
        right.place(relx=0.65, rely=0.0, relwidth=0.35, relheight=1.0)

        # Constrain content width nicely
        form_wrap = tk.Frame(right, bg="#6E747B")
        form_wrap.place(relx=0.5, rely=0.5, anchor="center")

        form_inner = tk.Frame(form_wrap, bg="#6E747B", padx=48, pady=48)
        form_inner.pack()

        heading = tk.Label(form_inner, text="Welcome to Argus! Please Log in", font=("Segoe UI", 18, "bold"), fg="#FFFFFF", bg="#6E747B")
        heading.pack(anchor="w", pady=(0, 6))

        # Username field
        user_block = tk.Frame(form_inner, bg="#6E747B")
        user_block.pack(fill=tk.X, pady=(4, 10))
        tk.Label(user_block, text="Username", font=("Segoe UI", 10), bg="#6E747B").pack(anchor="w")
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(user_block, textvariable=self.username_var, font=("Segoe UI", 11), bg="#FFFFFF", fg="#000000", insertbackground="#000000", bd=0, highlightthickness=1, highlightbackground="#000000", highlightcolor="#000000")
        self.username_entry.pack(fill=tk.X, ipady=6)
        self.username_entry.focus_set()

        # Password field
        pass_block = tk.Frame(form_inner, bg="#6E747B")
        pass_block.pack(fill=tk.X, pady=(4, 10))
        tk.Label(pass_block, text="Password", font=("Segoe UI", 10), bg="#6E747B").pack(anchor="w")
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(pass_block, textvariable=self.password_var, show="•", font=("Segoe UI", 11), bg="#FFFFFF", fg="#000000", insertbackground="#000000", bd=0, highlightthickness=1, highlightbackground="#000000", highlightcolor="#000000")
        self.password_entry.pack(fill=tk.X, ipady=6)

        # Status label for inline feedback
        self.status = tk.Label(form_inner, text="", fg="#cc0000", bg="#6E747B")
        self.status.pack(anchor="w", pady=(0, 8))

        # Action buttons
        btn_row = tk.Frame(form_inner, bg="#6E747B")
        btn_row.pack(fill=tk.X, pady=(8, 0))
        login_btn = tk.Button(btn_row, text="Login Now", command=self._handle_login, height=2, bg="#FFFFFF", fg="#000000", activebackground="#FFFFFF", activeforeground="#000000", relief="solid", borderwidth=1, highlightthickness=0)
        login_btn.pack(fill=tk.X)

        cancel_row = tk.Frame(form_inner, bg="#6E747B")
        cancel_row.pack(fill=tk.X, pady=(10, 0))
        cancel_btn = tk.Button(cancel_row, text="Quit", command=self.master.quit, bg="#FFFFFF", fg="#000000", activebackground="#FFFFFF", activeforeground="#000000", relief="solid", borderwidth=1, highlightthickness=0)
        cancel_btn.pack(side=tk.RIGHT)

        # Enter key triggers login
        self.master.bind('<Return>', lambda _e: self._handle_login())

    def _toggle_password(self):
        self.password_entry.config(show="" if self.show_password_var.get() else "•")

    def _handle_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            self._set_status("Please enter a username and password.")
            return

        expected = DEMO_USERS.get(username)
        if expected and expected == password:
            self._set_status("")
            # Reuse the same root window: clear children and mount Dashboard
            for child in self.master.winfo_children():
                child.destroy()
            DashboardApp(self.master)
        else:
            self._set_status("Invalid username or password.")

    def _set_status(self, text: str):
        self.status.config(text=text)


def main():
    root = tk.Tk()
    LoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()