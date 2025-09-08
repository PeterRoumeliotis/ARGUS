import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Optional
from datetime import datetime
from brokers import get_brokers, get_specialized
from utils import search_site_for_name


class WebClearApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ARGUS • Web Clear")
        self.root.configure(bg="#222222")

        # Container
        main = tk.Frame(self.root, bg="#222222")
        main.pack(fill="both", expand=True)

        # Centered card
        card = tk.Frame(main, bg="#333333")
        card.place(relx=0.5, rely=0.5, anchor="center", width=600, height=420)
        self.card = card

        heading = tk.Label(card, text="Web Clear", fg="#ffffff", bg="#333333",
                           font=("Arial", 22, "bold"))
        heading.pack(pady=(24, 8))

        sub = tk.Label(card, text="Enter details to proceed with web clearing.",
                        fg="#dddddd", bg="#333333", font=("Arial", 11))
        sub.pack(pady=(0, 16))

        # Simple example form fields (placeholder)
        form = tk.Frame(card, bg="#333333")
        form.pack(fill="x", padx=40)

        def _row(label):
            r = tk.Frame(form, bg="#333333")
            r.pack(fill="x", pady=6)
            tk.Label(r, text=label, fg="#ffffff", bg="#333333").pack(anchor="w")
            e = tk.Entry(r, bg="#ffffff", fg="#000000")
            e.pack(fill="x", ipady=6)
            return e

        self.name_entry = _row("Full Name")
        self.city_entry = _row("City (optional)")
        self.state_entry = _row("State (optional)")

        # Actions
        actions = tk.Frame(card, bg="#333333")
        actions.pack(fill="x", padx=40, pady=(16, 0))

        submit_btn = tk.Button(actions, text="Start Web Clear", height=2,
                               bg="#ffffff", fg="#000000",
                               activebackground="#eeeeee", activeforeground="#000000",
                               relief="solid", borderwidth=1,
                               command=self._start_web_clear)
        submit_btn.pack(fill="x")

        actions2 = tk.Frame(card, bg="#333333")
        actions2.pack(fill="x", padx=40, pady=(8, 0))

        back_btn = tk.Button(actions2, text="Back to Dashboard",
                             bg="#ffffff", fg="#000000",
                             activebackground="#eeeeee", activeforeground="#000000",
                             relief="solid", borderwidth=1,
                             command=self._go_back)
        back_btn.pack(side=tk.RIGHT)

        # Bottom status + progress bar
        self.status_text = tk.StringVar(value="Idle")
        self.progress_var = tk.IntVar(value=0)

        status_bar = tk.Frame(self.root, bg="#1f1f1f")
        status_bar.pack(side="bottom", fill="x")

        self.progress = ttk.Progressbar(status_bar, orient="horizontal",
                                        mode="determinate", maximum=100,
                                        variable=self.progress_var)
        self.progress.pack(side="left", fill="x", expand=True, padx=(8, 6), pady=6)

        self.progress_label = tk.Label(status_bar, textvariable=self.status_text,
                                       fg="#dddddd", bg="#1f1f1f")
        self.progress_label.pack(side="right", padx=8)

        # ESC exits fullscreen if set by parent
        self.root.bind("<Escape>", lambda e: self.root.attributes('-fullscreen', False))

    def _start_web_clear(self):
        # Placeholder handler; wire to your clearing workflow here
        name = self.name_entry.get().strip()
        city = self.city_entry.get().strip()
        state = self.state_entry.get().strip()

        # Kick off async workflow (placeholder demo) and update progress bar
        self._disable_inputs(True)
        self._set_progress(0, "Starting...")
        threading.Thread(target=self._simulate_clear_workflow,
                         args=(name, city, state), daemon=True).start()

    def _go_back(self):
        # Rebuild the dashboard in the same root window
        for child in self.root.winfo_children():
            child.destroy()
        from Dashboard import DashboardApp  # import here to avoid circular import
        DashboardApp(self.root)

    # --- Helpers for progress + threading-safe UI updates ---
    def _set_progress(self, value: int, text: Optional[str] = None):
        try:
            self.progress_var.set(max(0, min(100, int(value))))
        except Exception:
            self.progress_var.set(0)
        if text is not None:
            self.status_text.set(text)

    def _disable_inputs(self, disabled: bool):
        state = tk.DISABLED if disabled else tk.NORMAL
        for w in (self.name_entry, self.city_entry, self.state_entry):
            w.configure(state=state)

    def _simulate_clear_workflow(self, name: str, city: str, state: str):
        started_all = datetime.now().isoformat(timespec="seconds")

        # Helper to animate progress smoothly to a target percent
        def _progress_to(target: int, label: str, delay: float = 0.02):
            while self.progress_var.get() < target:
                current = self.progress_var.get() + 1
                self.root.after(0, self._set_progress, current, label)
                time.sleep(delay)

        # Initial validation and setup
        _progress_to(5, "Validating input")
        _progress_to(10, "Loading providers")

        # Load providers from sites.json via brokers package
        providers = [{"key": b["key"], "display": b["display"], "domain": b.get("domain")} for b in get_brokers()]
        if not providers:
            providers = [{"key": "default", "display": "Default Provider"}]
        provider_results = {}

        # Distribute progress roughly evenly across providers (10%..95%)
        base = 10
        span = 85
        per = max(1, span // max(1, len(providers)))

        for idx, p in enumerate(providers):
            p_start = base + per * idx
            p_end = base + per * (idx + 1) - 1
            key = p["key"]
            disp = p["display"]
            domain = p.get("domain")
            started = datetime.now().isoformat(timespec="seconds")

            # Phase 1: search via specialized broker if available; otherwise fallback
            step1 = min(p_start + max(1, per // 3), p_end)
            _progress_to(step1, f"{disp}: searching")
            urls = []
            err_msg = None
            try:
                if domain and name:
                    spec = get_specialized(domain)
                    if spec is not None:
                        urls = spec(name, city or None, state or None, timeout=12.0, limit=5)
                    else:
                        urls = search_site_for_name(domain, name, city or None, state or None, limit=3, timeout=12.0)
            except Exception as e:
                urls = []
                err_msg = str(e)

            # Phase 2: basic analysis
            step2 = min(p_start + max(2, (2 * per) // 3), p_end)
            _progress_to(step2, f"{disp}: analyzing")
            time.sleep(0.02)
            _progress_to(p_end, f"{disp}: done")

            finished = datetime.now().isoformat(timespec="seconds")
            provider_results[key] = {
                "display_name": disp,
                "status": "found" if urls else "not_found",
                "message": ("Matches found" if urls else (err_msg or "No results detected")),
                "records_found": len(urls),
                "opt_out_submitted": False,
                "urls": urls,
                "started_at": started,
                "finished_at": finished,
            }

            # Small throttle between providers to avoid rate limiting
            time.sleep(0.2)

        # Final wrap-up to 100%
        _progress_to(100, "Completed")
        finished_all = datetime.now().isoformat(timespec="seconds")

        summary = f"Done: {name or 'N/A'}" + (f", {city}" if city else "") + (f", {state}" if state else "")

        # Save a detailed report with provider results
        try:
            from reporter import save_webclear_report
        except Exception:
            save_webclear_report = None

        report_path = None
        try:
            if save_webclear_report is not None:
                report_path = save_webclear_report({
                    "name": name,
                    "city": city,
                    "state": state,
                    "status": "completed",
                    "started_at": started_all,
                    "finished_at": finished_all,
                    "providers": provider_results,
                })
        except Exception:
            report_path = None

        self._last_report_path = report_path
        self.root.after(0, self._set_progress, 100, summary if not report_path else f"Completed • Saved: {report_path}")
        self.root.after(0, self._disable_inputs, False)
        if report_path:
            self.root.after(0, self._show_report_ui, report_path)

    # Public hook to allow an external clearing routine to update progress
    def update_progress(self, percent: int, message: Optional[str] = None):
        self._set_progress(percent, message)

    # --- Report helpers ---
    def _show_report_ui(self, path: str):
        if getattr(self, "report_frame", None):
            try:
                self.report_path_var.set(path)
            except Exception:
                pass
            return
        self.report_frame = tk.Frame(self.card, bg="#333333")
        self.report_frame.pack(fill="x", padx=40, pady=(12, 0))
        tk.Label(self.report_frame, text="Report saved:", fg="#dddddd", bg="#333333").pack(side="left")
        self.report_path_var = tk.StringVar(value=path)
        tk.Label(self.report_frame, textvariable=self.report_path_var, fg="#aaaaaa", bg="#333333").pack(side="left", padx=(6, 12))
        open_btn = tk.Button(self.report_frame, text="Open Report", bg="#ffffff", fg="#000000",
                             relief="solid", borderwidth=1, command=self._open_report)
        open_btn.pack(side="right")

    def _open_report(self):
        import os, platform, subprocess
        path = getattr(self, "_last_report_path", None)
        if not path or not os.path.exists(path):
            return
        system = platform.system()
        try:
            if system == "Darwin":
                subprocess.Popen(["open", path])
            elif system == "Windows":
                os.startfile(path)  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception:
            pass


def main():
    root = tk.Tk()
    WebClearApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
