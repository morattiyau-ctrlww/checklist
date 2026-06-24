import tkinter as tk
from tkinter import ttk
import random
import math

CONFETTI_COLORS = [
    "#ff6b6b",
    "#feca57",
    "#48dbfb",
    "#ff9ff3",
    "#54a0ff",
    "#5f27cd",
    "#01a3a4",
    "#ff6348",
]

GIFTS = ["🍎", "🍊", "🍬", "🍪", "🧁", "🍫", "🍩", "🍭", "🎁", "🌟"]

DEFAULT_ITEMS = [
    "1) Find the property",
    "2) Find area and bldg age",
    "3) Market price",
    "4) Data entry",
    "5) Reply",
]


class ChecklistApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Valuation Checklist")
        self.geometry("520x400")
        self.configure(bg="#f8f9fa")

        self.check_items = []
        self.confetti_canvas = None
        self.particles = []
        self.celebrating = False
        self.progress_current = 0.0
        self.progress_target = 0.0
        self.progress_shine_pos = -30
        self.celeb_text_ids = []

        self._build_ui()
        for text in DEFAULT_ITEMS:
            self._add_check_item(text)
        self._update_progress()
        self._animate_progress_shine()

    def _build_ui(self):
        header = tk.Frame(self, bg="#f8f9fa")
        header.pack(fill="x", padx=20, pady=(15, 5))
        tk.Label(
            header,
            text="Valuation Checklist",
            font=("Segoe UI", 18, "bold"),
            fg="#2d3436",
            bg="#f8f9fa",
        ).pack(anchor="w")

        progress_frame = tk.Frame(self, bg="#f8f9fa")
        progress_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.progress_label = tk.Label(
            progress_frame,
            text="Progress: 0/5",
            font=("Segoe UI", 10),
            fg="#636e72",
            bg="#f8f9fa",
        )
        self.progress_label.pack(anchor="w")

        self.progress_canvas = tk.Canvas(
            progress_frame, height=26, bg="#f8f9fa", borderwidth=0, highlightthickness=0
        )
        self.progress_canvas.pack(fill="x", pady=(2, 0))
        self.progress_canvas.bind("<Configure>", lambda e: self._draw_progress_bar())

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=20)

        canvas_frame = tk.Frame(self, bg="#f8f9fa")
        canvas_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.canvas = tk.Canvas(
            canvas_frame, bg="#f8f9fa", borderwidth=0, highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            canvas_frame, orient="vertical", command=self.canvas.yview
        )
        inner = tk.Frame(self.canvas, bg="#f8f9fa")
        inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width),
        )
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=inner, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.scrollable_frame = inner
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        controls = tk.Frame(self, bg="#f8f9fa")
        controls.pack(fill="x", padx=20, pady=(0, 12))
        self.entry = ttk.Entry(controls, font=("Segoe UI", 10))
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.entry.bind("<Return>", lambda e: self._add_item())
        ttk.Button(controls, text="Add", command=self._add_item, width=8).pack(
            side="right"
        )
        ttk.Button(controls, text="Remove Done", command=self._remove_selected).pack(
            side="left", padx=(0, 6)
        )

    def _add_check_item(self, text):
        var = tk.BooleanVar(value=False)
        row = tk.Frame(self.scrollable_frame, bg="#f8f9fa")
        row.pack(fill="x", pady=2)
        indicator = tk.Canvas(
            row, width=24, height=24, bg="#f8f9fa", borderwidth=0, highlightthickness=0
        )
        indicator.pack(side="right", padx=(4, 2))
        cb = tk.Checkbutton(
            row,
            text=text,
            variable=var,
            font=("Segoe UI", 11),
            bg="#f8f9fa",
            activebackground="#f8f9fa",
            fg="#2d3436",
            selectcolor="#f8f9fa",
        )
        cb.config(command=lambda v=var, c=cb, ind=indicator: self._on_toggle(v, c, ind))
        cb.pack(side="left", anchor="w")
        self.check_items.append(
            {"var": var, "cb": cb, "indicator": indicator, "text": text, "row": row}
        )

    def _on_toggle(self, var, cb, indicator):
        if var.get():
            self._animate_check(cb, 0, var)
            self._animate_indicator(indicator, 0, var)
        else:
            if hasattr(cb, "_anim_after"):
                self.after_cancel(cb._anim_after)
                cb._anim_after = None
            if hasattr(indicator, "_anim_after"):
                self.after_cancel(indicator._anim_after)
                indicator._anim_after = None
            cb.config(
                fg="#2d3436",
                font=("Segoe UI", 11),
                bg="#f8f9fa",
                activebackground="#f8f9fa",
            )
            indicator.delete("all")
        self._update_progress()
        self._check_all_done()

    def _animate_check(self, cb, step, var):
        if not var.get():
            cb._anim_after = None
            return
        steps = [
            {"bg": "#d4edda"},
            {"bg": "#f8f9fa"},
            {"bg": "#d4edda"},
            {"bg": "#f8f9fa", "fg": "#28a745", "font": "overstrike"},
        ]
        if step < len(steps):
            cfg = steps[step]
            cb.config(
                bg=cfg.get("bg", "#f8f9fa"),
                activebackground=cfg.get("bg", "#f8f9fa"),
                fg=cfg.get("fg", "#2d3436"),
                font=("Segoe UI", 11, cfg.get("font", "")),
            )
            cb._anim_after = self.after(
                150, lambda: self._animate_check(cb, step + 1, var)
            )

    def _animate_indicator(self, canvas, step, var, loop=0):
        if not var.get():
            canvas._anim_after = None
            return
        canvas.delete("all")
        if step == 0:
            canvas.create_oval(3, 3, 21, 21, outline="#e74c3c", width=2)
            canvas.create_line(7, 12, 17, 12, fill="#e74c3c", width=1.5)
            canvas.create_line(12, 7, 12, 17, fill="#e74c3c", width=1.5)
            canvas._anim_after = self.after(
                180, lambda: self._animate_indicator(canvas, 1, var)
            )
        elif step == 1:
            canvas.create_oval(3, 3, 21, 21, outline="#e74c3c", width=2)
            canvas.create_line(4, 4, 20, 20, fill="#c0392b", width=3, capstyle="round")
            canvas._anim_after = self.after(
                150, lambda: self._animate_indicator(canvas, 2, var)
            )
        elif step == 2:
            canvas.create_line(
                20, 4, 4, 20, fill="#c0392b", width=2.5, capstyle="round"
            )
            canvas.create_line(
                4, 4, 20, 20, fill="#c0392b", width=2.5, capstyle="round"
            )
            canvas._anim_after = self.after(
                150, lambda: self._animate_indicator(canvas, 3, var)
            )
        elif step == 3:
            canvas.create_oval(5, 5, 19, 19, fill="#f39c12", outline="")
            canvas._anim_after = self.after(
                120, lambda: self._animate_indicator(canvas, 4, var)
            )
        elif step == 4:
            canvas.create_oval(2, 2, 22, 22, fill="#28a745", outline="#28a745")
            canvas.create_line(
                7,
                13,
                11,
                17,
                21,
                7,
                fill="white",
                width=2.5,
                capstyle="round",
                joinstyle="round",
            )
            canvas._anim_after = self.after(
                250, lambda: self._animate_indicator(canvas, 5, var, 0)
            )
        elif step == 5:
            pad = 1 if loop % 2 == 0 else 3
            canvas.create_oval(
                pad, pad, 24 - pad, 24 - pad, fill="#28a745", outline="#28a745"
            )
            canvas.create_line(
                7,
                13,
                11,
                17,
                21,
                7,
                fill="white",
                width=2.5,
                capstyle="round",
                joinstyle="round",
            )
            if loop < 6:
                canvas._anim_after = self.after(
                    200, lambda: self._animate_indicator(canvas, 5, var, loop + 1)
                )

    def _draw_progress_bar(self):
        self.progress_canvas.delete("all")
        w = self.progress_canvas.winfo_width()
        h = 26
        if w < 10:
            return
        self.progress_canvas.create_rectangle(
            2, 3, w - 2, h - 3, fill="#e9ecef", outline="", width=0
        )
        if self.progress_current > 0:
            fill_end = 2 + int((w - 4) * min(self.progress_current, 100) / 100)
            if self.progress_current < 40:
                color = "#f39c12"
            elif self.progress_current < 75:
                color = "#2ecc71"
            else:
                color = "#27ae60"
            self.progress_canvas.create_rectangle(
                2, 3, fill_end, h - 3, fill=color, outline="", width=0
            )
            if (
                self.progress_shine_pos > -15
                and self.progress_shine_pos + 2 < fill_end - 2
            ):
                sx = 2 + int(self.progress_shine_pos)
                self.progress_canvas.create_rectangle(
                    sx,
                    3,
                    sx + 20,
                    h - 3,
                    fill="white",
                    stipple="gray25",
                    outline="",
                    width=0,
                )
        self.progress_canvas.create_text(
            w // 2,
            h // 2,
            text=f"{int(self.progress_current)}%",
            font=("Segoe UI", 9, "bold"),
            fill="#495057",
        )

    def _animate_progress_fill(self):
        step = 3
        if self.progress_current < self.progress_target:
            self.progress_current = min(
                self.progress_current + step, self.progress_target
            )
        elif self.progress_current > self.progress_target:
            self.progress_current = max(
                self.progress_current - step, self.progress_target
            )
        self._draw_progress_bar()
        if abs(self.progress_current - self.progress_target) > 0.5:
            self.after(30, self._animate_progress_fill)

    def _animate_progress_shine(self):
        if not self.progress_canvas:
            return
        if self.progress_current > 5 and not self.celebrating:
            w = self.progress_canvas.winfo_width()
            fill_width = int((w - 4) * self.progress_current / 100)
            self.progress_shine_pos += 4
            if self.progress_shine_pos > fill_width:
                self.progress_shine_pos = -30
        else:
            self.progress_shine_pos = -30
        self._draw_progress_bar()
        self.after(60, self._animate_progress_shine)

    def _update_progress(self):
        total = len(self.check_items)
        checked = sum(1 for item in self.check_items if item["var"].get())
        self.progress_label.config(text=f"Progress: {checked}/{total}")
        new_target = (checked / total * 100) if total > 0 else 0
        if new_target != self.progress_target:
            self.progress_target = new_target
            self._animate_progress_fill()

    def _check_all_done(self):
        if self.celebrating:
            return
        for item in self.check_items:
            if not item["var"].get():
                return
        self._celebrate()

    def _celebrate(self):
        self.celebrating = True
        self.confetti_canvas = tk.Canvas(self, bg="#f8f9fa", highlightthickness=0)
        self.confetti_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        w = max(self.winfo_width(), 520)
        h = max(self.winfo_height(), 400)
        cx, cy = w // 2, h // 2 - 30

        self.particles = []
        for _ in range(120):
            x = random.randint(0, w)
            y = random.randint(-h, 0)
            sz = random.randint(5, 10)
            color = random.choice(CONFETTI_COLORS)
            if random.choice([True, False]):
                pid = self.confetti_canvas.create_rectangle(
                    x, y, x + sz, y + sz * 1.5, fill=color, outline=""
                )
            else:
                pid = self.confetti_canvas.create_oval(
                    x, y, x + sz, y + sz, fill=color, outline=""
                )
            self.particles.append(
                {
                    "id": pid,
                    "dx": random.uniform(-1.5, 1.5),
                    "dy": random.uniform(1, 4),
                    "gravity": random.uniform(0.05, 0.15),
                }
            )

        self.celeb_text_ids = [
            self.confetti_canvas.create_text(
                cx, cy, text="All Done!", font=("Segoe UI", 32, "bold"), fill="#2d3436"
            ),
            self.confetti_canvas.create_text(
                cx,
                cy + 50,
                text="All tasks completed",
                font=("Segoe UI", 14),
                fill="#636e72",
            ),
        ]

        reset_btn = tk.Button(
            self.confetti_canvas,
            text="Start Over",
            font=("Segoe UI", 10),
            command=self._reset_all,
            cursor="hand2",
        )
        self.confetti_canvas.create_window(cx, cy + 100, window=reset_btn)

        self.firework_bursts = []
        self.sparkle_ids = []
        self.ring_ids = []
        self.shockwave_ids = []
        self.gift_items = []
        self.gift_burst_particles = []
        self._gift_opened = False
        self._fw_count = 0

        self._animate_confetti()
        self._animate_rings(0)
        self._animate_text_color(0)
        self._animate_fireworks_particles()
        self._spawn_firework()
        self._animate_sparkles()
        self._spawn_gift()
        self.after(30000, self._reset_all)

    def _animate_rings(self, angle):
        if not self.celebrating or not self.confetti_canvas:
            return
        for rid in self.ring_ids:
            self.confetti_canvas.delete(rid)
        self.ring_ids = []
        cx = max(self.winfo_width(), 520) // 2
        cy = max(self.winfo_height(), 400) // 2 - 30

        layers = [
            (8, 65, 15, "#feca57", "#e67e22"),
            (12, 100, -10, "#ff9ff3", "#e84393"),
            (6, 135, 20, "#48dbfb", "#0abde3"),
        ]
        for count, radius, speed, color1, color2 in layers:
            for i in range(count):
                a = angle * speed / 15 + (360 / count) * i
                rad = math.radians(a)
                x = cx + radius * math.cos(rad)
                y = cy + radius * math.sin(rad)
                c = color1 if i % 2 == 0 else color2
                sz = 5 if i % 2 == 0 else 3
                self.ring_ids.append(
                    self.confetti_canvas.create_oval(
                        x - sz, y - sz, x + sz, y + sz, fill=c, outline=""
                    )
                )

        self.after(30, lambda: self._animate_rings(angle + 1))

    def _animate_text_color(self, idx):
        if not self.celebrating or not self.confetti_canvas or not self.celeb_text_ids:
            return
        colors = ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#3498db", "#9b59b6"]
        self.confetti_canvas.itemconfig(
            self.celeb_text_ids[0], fill=colors[idx % len(colors)]
        )
        self.after(200, lambda: self._animate_text_color(idx + 1))

    def _spawn_firework(self):
        if not self.celebrating or not self.confetti_canvas:
            return
        self._fw_count += 1
        w = max(self.winfo_width(), 520)
        h = max(self.winfo_height(), 400)
        bx = random.randint(60, w - 60)
        by = random.randint(60, h - 60)

        burst = []
        for _ in range(random.randint(12, 20)):
            a = random.uniform(0, 360)
            spd = random.uniform(2, 6)
            sz = random.randint(3, 6)
            color = random.choice(CONFETTI_COLORS)
            pid = self.confetti_canvas.create_oval(
                bx - 2, by - 2, bx + sz, by + sz, fill=color, outline=""
            )
            burst.append(
                {
                    "id": pid,
                    "dx": spd * math.cos(math.radians(a)),
                    "dy": spd * math.sin(math.radians(a)),
                    "life": 40,
                }
            )
        self.firework_bursts.append(burst)
        self.after(random.randint(500, 1000), self._spawn_firework)

    def _animate_fireworks_particles(self):
        if not self.celebrating or not self.confetti_canvas:
            return
        for burst in self.firework_bursts[:]:
            for p in burst[:]:
                self.confetti_canvas.move(p["id"], p["dx"], p["dy"])
                p["dx"] *= 0.96
                p["dy"] *= 0.96
                p["life"] -= 1
                if p["life"] <= 0:
                    self.confetti_canvas.delete(p["id"])
                    burst.remove(p)
            if not burst:
                self.firework_bursts.remove(burst)
        self.after(30, self._animate_fireworks_particles)

    def _animate_sparkles(self):
        if not self.celebrating or not self.confetti_canvas:
            return
        for sid in self.sparkle_ids:
            self.confetti_canvas.delete(sid)
        self.sparkle_ids = []
        w = max(self.winfo_width(), 520)
        h = max(self.winfo_height(), 400)
        for _ in range(5):
            sx = random.randint(20, w - 20)
            sy = random.randint(20, h - 20)
            color = random.choice(CONFETTI_COLORS)
            self.sparkle_ids.append(
                self.confetti_canvas.create_text(
                    sx,
                    sy,
                    text="*",
                    font=("Segoe UI", random.randint(10, 18), "bold"),
                    fill=color,
                )
            )
        self.after(150, self._animate_sparkles)

    def _spawn_gift(self):
        if not self.celebrating or not self.confetti_canvas:
            return
        self._gift_opened = False
        self.gift_burst_particles = []

        w = max(self.winfo_width(), 520)
        h = max(self.winfo_height(), 400)
        gx = w // 2 + 130
        gy = h // 2 - 60

        self.confetti_canvas.create_text(
            gx,
            gy,
            text="🎁",
            font=("Segoe UI Emoji", 64),
            fill="#f39c12",
            anchor="center",
            tags=("gift_box_emoji", "gift_click"),
        )
        self.confetti_canvas.create_rectangle(
            gx - 65,
            gy + 32,
            gx + 65,
            gy + 58,
            fill="#2d3436",
            outline="",
            tags=("gift_box_bg",),
        )
        self.confetti_canvas.create_text(
            gx,
            gy + 45,
            text="CLICK TO OPEN",
            font=("Segoe UI", 11, "bold"),
            fill="white",
            anchor="center",
            tags=("gift_btn_label",),
        )

        self.confetti_canvas.tag_bind("gift_click", "<Button-1>", self._open_gift)
        self._gift_pos = (gx, gy)

        self._pulse_gift_label()

    def _pulse_gift_label(self):
        if not self.celebrating or not self.confetti_canvas or self._gift_opened:
            return
        colors = [
            "#e74c3c",
            "#e67e22",
            "#f1c40f",
            "#2ecc71",
            "#3498db",
            "#9b59b6",
            "#e74c3c",
        ]
        current = self.confetti_canvas.find_withtag("gift_btn_label")
        if current:
            idx = random.randint(0, len(colors) - 1)
            self.confetti_canvas.itemconfig(current[0], fill=colors[idx])
        self.after(200, self._pulse_gift_label)

    def _open_gift(self, event):
        if not self.celebrating or not self.confetti_canvas or self._gift_opened:
            return
        self._gift_opened = True
        self.confetti_canvas.delete("gift_box_emoji")
        self.confetti_canvas.delete("gift_box_bg")
        self.confetti_canvas.delete("gift_btn_label")
        gx, gy = self._gift_pos
        gift = random.choice(GIFTS)

        for _ in range(25):
            a = random.uniform(0, 360)
            spd = random.uniform(3, 8)
            sz = random.randint(4, 8)
            color = random.choice(CONFETTI_COLORS)
            pid = self.confetti_canvas.create_oval(
                gx - 2,
                gy - 2,
                gx + sz,
                gy + sz,
                fill=color,
                outline="",
                tags="gift_burst",
            )
            self.gift_burst_particles.append(
                {
                    "id": pid,
                    "dx": spd * math.cos(math.radians(a)),
                    "dy": spd * math.sin(math.radians(a)),
                    "life": 35,
                }
            )

        bg_color = random.choice(
            ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#3498db", "#9b59b6"]
        )
        self.confetti_canvas.create_oval(
            gx - 45,
            gy - 45,
            gx + 45,
            gy + 45,
            fill=bg_color,
            outline="white",
            width=3,
            tags="gift_revealed",
        )
        self.confetti_canvas.create_text(
            gx,
            gy,
            text=gift,
            font=("Segoe UI Emoji", 56),
            anchor="center",
            tags="gift_revealed",
        )
        self.confetti_canvas.create_text(
            gx,
            gy + 55,
            text="You got a " + gift + "!",
            font=("Segoe UI", 12, "bold"),
            fill=bg_color,
            anchor="center",
            tags="gift_label",
        )

        self._animate_gift_burst()

    def _animate_gift_burst(self):
        if not self.celebrating or not self.confetti_canvas:
            return
        for p in self.gift_burst_particles[:]:
            self.confetti_canvas.move(p["id"], p["dx"], p["dy"])
            p["dx"] *= 0.94
            p["dy"] *= 0.94
            p["life"] -= 1
            if p["life"] <= 0:
                self.confetti_canvas.delete(p["id"])
                self.gift_burst_particles.remove(p)
        if self.gift_burst_particles:
            self.after(30, self._animate_gift_burst)

    def _animate_confetti(self):
        if not self.celebrating or not self.particles:
            return
        w = max(self.winfo_width(), 520)
        h = max(self.winfo_height(), 400)
        for p in self.particles:
            self.confetti_canvas.move(p["id"], p["dx"], p["dy"])
            p["dy"] += p["gravity"]
            p["dx"] *= 0.995
            coords = self.confetti_canvas.coords(p["id"])
            if coords and coords[1] > h + 20:
                x = random.randint(0, w)
                self.confetti_canvas.coords(p["id"], x, -20, x + 8, -20 + 12)
                p["dy"] = random.uniform(1, 4)
                p["dx"] = random.uniform(-1.5, 1.5)
                p["gravity"] = random.uniform(0.05, 0.15)
        self.after(30, self._animate_confetti)

    def _reset_all(self):
        self.celebrating = False
        if self.confetti_canvas:
            self.confetti_canvas.destroy()
            self.confetti_canvas = None
        self.particles = []
        self.celeb_text_ids = []
        self.ring_ids = []
        self.firework_bursts = []
        self.sparkle_ids = []
        self.shockwave_ids = []
        self.gift_items = []
        self.gift_burst_particles = []
        self.progress_current = 0.0
        self.progress_target = 0.0
        for item in self.check_items:
            if hasattr(item["cb"], "_anim_after"):
                self.after_cancel(item["cb"]._anim_after)
                item["cb"]._anim_after = None
            if hasattr(item["indicator"], "_anim_after"):
                self.after_cancel(item["indicator"]._anim_after)
                item["indicator"]._anim_after = None
            item["var"].set(False)
            item["cb"].config(
                fg="#2d3436",
                font=("Segoe UI", 11),
                bg="#f8f9fa",
                activebackground="#f8f9fa",
            )
            item["indicator"].delete("all")
        self._update_progress()
        self._draw_progress_bar()

    def _add_item(self):
        text = self.entry.get().strip()
        if text:
            self._add_check_item(text)
            self.entry.delete(0, tk.END)
            self._update_progress()

    def _remove_selected(self):
        to_remove = [i for i, item in enumerate(self.check_items) if item["var"].get()]
        for i in reversed(to_remove):
            item = self.check_items.pop(i)
            item["row"].destroy()
        self._update_progress()

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    ChecklistApp().run()
