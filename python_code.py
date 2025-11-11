
import tkinter as tk
from tkinter import ttk
import random
import time

# ----------------- Configuration -----------------
DEFAULT_N = 40         # Default number of elements (try 10..200)
CANVAS_W = 900
CANVAS_H = 400
BAR_GAP = 2
MIN_VAL = 5
MAX_VAL = 100
# -------------------------------------------------


class SortVisualizer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Algorithm State Transition Visualizer — Bubble Sort")
        self.geometry(f"{CANVAS_W + 20}x{CANVAS_H + 220}")
        self.resizable(False, False)

        # State variables
        self.N = DEFAULT_N
        self.seed = None
        self.array = []
        self.states = []
        self.frame_index = 0
        self.running = False
        self.speed_ms = 80
        self.start_time = None
        self.elapsed = 0.0

        # Build UI
        self._build_ui()
        self.randomize_array()
        self.prepare_states()
        self.draw_frame(0)

    # ------------------- UI Setup -------------------
    def _build_ui(self):
        # Canvas
        self.canvas = tk.Canvas(self, width=CANVAS_W, height=CANVAS_H, bg="white")
        self.canvas.pack(padx=10, pady=8)

        # Controls
        ctrl = ttk.Frame(self)
        ctrl.pack(fill="x", padx=10)

        self.play_btn = ttk.Button(ctrl, text="Play", command=self.toggle_play)
        self.play_btn.grid(row=0, column=0, padx=6)

        ttk.Button(ctrl, text="Step", command=self.step_once).grid(row=0, column=1, padx=6)
        ttk.Button(ctrl, text="Reset", command=self.reset).grid(row=0, column=2, padx=6)
        ttk.Button(ctrl, text="Randomize", command=self.randomize_and_prepare).grid(row=0, column=3, padx=6)

        ttk.Label(ctrl, text="Size").grid(row=0, column=4, padx=(14, 2))
        self.size_spin = ttk.Spinbox(ctrl, from_=5, to=200, width=5, command=self.on_size_change)
        self.size_spin.set(str(self.N))
        self.size_spin.grid(row=0, column=5)

        ttk.Label(ctrl, text="Speed").grid(row=0, column=6, padx=(14, 2))
        self.speed_scale = ttk.Scale(
            ctrl, from_=10, to=500, value=self.speed_ms, orient="horizontal", command=self.on_speed_change
        )
        self.speed_scale.grid(row=0, column=7, sticky="we", padx=6)
        ctrl.columnconfigure(7, weight=1)

        # Info Labels
        info = ttk.Frame(self)
        info.pack(fill="x", padx=10, pady=(6, 0))
        self.frame_label = ttk.Label(info, text="Frame: 0/0")
        self.frame_label.pack(side="left")
        self.op_label = ttk.Label(info, text="Operation: —", width=60)
        self.op_label.pack(side="left", padx=(10, 0))
        self.time_label = ttk.Label(info, text="Elapsed: 0.000s")
        self.time_label.pack(side="right")

        # Keyboard bindings
        self.bind("<space>", lambda e: self.toggle_play())
        self.bind("<Right>", lambda e: self.step_once())
        self.bind("<r>", lambda e: self.randomize_and_prepare())

    # ------------------- Array & States -------------------
    def randomize_array(self, seed=None):
        if seed is not None:
            random.seed(seed)
            self.seed = seed
        else:
            self.seed = int(time.time() * 1000) & 0xFFFFFF
            random.seed(self.seed)
        self.array = [random.randint(MIN_VAL, MAX_VAL) for _ in range(self.N)]

    def prepare_states(self):
        self.states = list(self.bubble_sort_states(self.array))
        self.frame_index = 0
        self.elapsed = 0.0
        self.start_time = None
        self.update_info()

    def randomize_and_prepare(self):
        self.running = False
        self.play_btn.config(text="Play")
        try:
            self.N = int(self.size_spin.get())
        except ValueError:
            self.N = DEFAULT_N
            self.size_spin.set(str(self.N))
        self.randomize_array()
        self.prepare_states()
        self.draw_frame(0)

    def reset(self):
        self.running = False
        self.play_btn.config(text="Play")
        self.prepare_states()
        self.draw_frame(0)

    def on_size_change(self):
        try:
            self.N = int(self.size_spin.get())
        except ValueError:
            return
        self.randomize_and_prepare()

    def on_speed_change(self, v):
        try:
            self.speed_ms = int(float(v))
        except ValueError:
            pass

    # ------------------- Sorting generator -------------------
    def bubble_sort_states(self, arr):
        a = arr.copy()
        n = len(a)
        start = time.perf_counter()
        yield (a.copy(), None, None, False, f"Start (seed={self.seed}): {a}", 0.0)
        step = 0
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                elapsed = time.perf_counter() - start
                desc = f"Compare {j} and {j+1}: {a[j]} ? {a[j+1]}"
                yield (a.copy(), j, j + 1, False, desc, elapsed)
                if a[j] > a[j + 1]:
                    a[j], a[j + 1] = a[j + 1], a[j]
                    swapped = True
                    step += 1
                    elapsed = time.perf_counter() - start
                    desc = f"Swap {j} and {j+1}: now {a[j]}, {a[j+1]} (step {step})"
                    yield (a.copy(), j, j + 1, True, desc, elapsed)
            elapsed = time.perf_counter() - start
            yield (a.copy(), None, None, False, f"After pass {i+1}: {a}", elapsed)
            if not swapped:
                break
        elapsed = time.perf_counter() - start
        yield (a.copy(), None, None, False, f"Sorted: {a}", elapsed)

    # ------------------- Drawing -------------------
    def draw_frame(self, idx):
        if not self.states:
            return
        idx = max(0, min(idx, len(self.states) - 1))
        arr_snapshot, i_idx, j_idx, swapped, desc, elapsed = self.states[idx]

        self.canvas.delete("all")
        margin = 10
        w = CANVAS_W - 2 * margin
        h = CANVAS_H - 2 * margin
        bar_w = max(1, (w - (len(arr_snapshot) - 1) * BAR_GAP) // len(arr_snapshot))
        max_val = max(arr_snapshot) if arr_snapshot else 1

        for i, v in enumerate(arr_snapshot):
            x0 = margin + i * (bar_w + BAR_GAP)
            x1 = x0 + bar_w
            bar_h = (v / max_val) * h
            y1 = CANVAS_H - margin
            y0 = y1 - bar_h

            # Colors
            color = "#d3d3d3"
            outline = "black"
            width = 1
            if i_idx is not None and j_idx is not None and (i == i_idx or i == j_idx):
                color = "#7B68EE" if i == i_idx else "#FF8C00"
                if swapped:
                    width = 2

            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=outline, width=width)
            self.canvas.create_text((x0 + x1) / 2, y0 - 9, text=str(v), font=("TkDefaultFont", 8))

        self.op_label.config(text=f"Operation: {desc[:120]}")
        self.frame_label.config(text=f"Frame: {idx + 1}/{len(self.states)}")
        self.time_label.config(text=f"Elapsed: {elapsed:.4f}s")

    # ------------------- Controls -------------------
    def toggle_play(self):
        self.running = not self.running
        self.play_btn.config(text="Pause" if self.running else "Play")
        if self.running:
            if self.start_time is None:
                self.start_time = time.perf_counter()
            self.after(0, self._run_loop)

    def _run_loop(self):
        if not self.running:
            return
        if self.frame_index < len(self.states) - 1:
            self.frame_index += 1
            self.draw_frame(self.frame_index)
            self.update_info()
            self.after(max(10, self.speed_ms), self._run_loop)
        else:
            self.running = False
            self.play_btn.config(text="Play")

    def step_once(self):
        if self.frame_index < len(self.states) - 1:
            self.frame_index += 1
            self.draw_frame(self.frame_index)
            self.update_info()

    def update_info(self):
        if not self.states:
            return
        _, _, _, _, desc, elapsed = self.states[min(self.frame_index, len(self.states) - 1)]
        self.op_label.config(text=f"Operation: {desc[:120]}")
        self.frame_label.config(text=f"Frame: {self.frame_index + 1}/{len(self.states)}")
        self.time_label.config(text=f"Elapsed: {elapsed:.4f}s")


# ------------------- Run Application -------------------
if __name__ == "__main__":
    app = SortVisualizer()
    app.mainloop()
