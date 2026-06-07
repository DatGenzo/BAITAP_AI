"""
8-Puzzle Solver - Complex Environment Dashboard
Giao diện tùy chỉnh trạng thái Bắt đầu và Đích
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
from algorithms import (
    create_solver, GOAL_STATE, ALGORITHMS, HEURISTICS, VARIANTS, manhattan_distance
)

class ComplexPuzzleDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle - Complex Environment")
        self.root.geometry("1300x850")
        self.root.configure(bg="#111827")
        
        self.is_solving = False
        self.animation_speed = 400
        self.current_display_state = list(GOAL_STATE)
        
        self._setup_ui()
        self._set_default_goal()
        self._randomize_valid()

    def _setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#1f2937", height=100)
        header.pack(fill=tk.X)
        tk.Label(header, text="🧩 COMPLEX ENVIRONMENT SOLVER", font=("Montserrat", 20, "bold"), bg="#1f2937", fg="#10b981").pack(pady=10)

        # Main Container
        container = tk.Frame(self.root, bg="#111827")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # --- Left Panel: Custom Grids ---
        left_panel = tk.Frame(container, bg="#111827")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Start Grid
        tk.Label(left_panel, text="TRẠNG THÁI BẮT ĐẦU", font=("Montserrat", 11, "bold"), bg="#111827", fg="#f3f4f6").pack(pady=(0,5))
        self.start_entries = self._create_grid(left_panel)

        # Goal Grid
        tk.Label(left_panel, text="TRẠNG THÁI ĐÍCH", font=("Montserrat", 11, "bold"), bg="#111827", fg="#f3f4f6").pack(pady=(20,5))
        self.goal_entries = self._create_grid(left_panel)

        # Grid Controls
        btn_frame = tk.Frame(left_panel, bg="#111827")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Goal Mặc Định", command=self._set_default_goal, bg="#4b5563", fg="white", font=("Montserrat", 9, "bold"), padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Random Hợp Lệ", command=self._randomize_valid, bg="#2563eb", fg="white", font=("Montserrat", 9, "bold"), padx=10).pack(side=tk.LEFT, padx=5)

        # --- Right Panel: Dashboard ---
        right_panel = tk.Frame(container, bg="#1f2937", padx=20, pady=20, width=450)
        right_panel.pack_propagate(False) # Ép Frame giữ nguyên chiều rộng 450px
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH)

        # Algorithm Settings
        tk.Label(right_panel, text="CẤU HÌNH THUẬT TOÁN", font=("Montserrat", 12, "bold"), bg="#1f2937", fg="#10b981").pack(anchor="w")
        
        settings_grid = tk.Frame(right_panel, bg="#1f2937")
        settings_grid.pack(fill=tk.X, pady=10)

        tk.Label(settings_grid, text="Thuật toán:", bg="#1f2937", fg="#cbd5e1").grid(row=0, column=0, sticky="w")
        self.algo_var = tk.StringVar(value="A*")
        self.algo_combo = ttk.Combobox(settings_grid, textvariable=self.algo_var, values=list(ALGORITHMS.keys()), state="readonly")
        self.algo_combo.grid(row=0, column=1, padx=10, pady=5)
        self.algo_combo.bind("<<ComboboxSelected>>", self._on_algo_change)

        tk.Label(settings_grid, text="Heuristic:", bg="#1f2937", fg="#cbd5e1").grid(row=1, column=0, sticky="w")
        self.heur_var = tk.StringVar(value="Manhattan")
        self.heur_combo = ttk.Combobox(settings_grid, textvariable=self.heur_var, values=list(HEURISTICS.keys()), state="readonly")
        self.heur_combo.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(settings_grid, text="Kiểu Leo:", bg="#1f2937", fg="#cbd5e1").grid(row=2, column=0, sticky="w")
        self.variant_var = tk.StringVar(value="Simple")
        self.variant_combo = ttk.Combobox(settings_grid, textvariable=self.variant_var, values=list(VARIANTS.keys()), state="readonly")
        self.variant_combo.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(settings_grid, text="Tốc độ (ms):", bg="#1f2937", fg="#cbd5e1").grid(row=3, column=0, sticky="w")
        self.speed_var = tk.IntVar(value=400)
        speed_slider = tk.Scale(
            settings_grid, from_=50, to=2000, orient=tk.HORIZONTAL, 
            bg="#111827", fg="#10b981", variable=self.speed_var, 
            length=150, command=self._on_speed_change, highlightthickness=0
        )
        speed_slider.grid(row=3, column=1, padx=10, pady=5)

        # Khởi tạo trạng thái UI ban đầu
        self._on_algo_change()

        # Stats Area
        self.examined_var = tk.StringVar(value="0")
        self.steps_var = tk.StringVar(value="0")
        self.time_var = tk.StringVar(value="0.000s")

        stats_box = tk.Frame(right_panel, bg="#111827", padx=15, pady=15)
        stats_box.pack(fill=tk.X, pady=15)
        
        for label, var in [("Đã Duyệt", self.examined_var), ("Số Bước", self.steps_var), ("Thời Gian", self.time_var)]:
            f = tk.Frame(stats_box, bg="#111827")
            f.pack(fill=tk.X)
            tk.Label(f, text=label, bg="#111827", fg="#94a3b8").pack(side=tk.LEFT)
            tk.Label(f, textvariable=var, bg="#111827", fg="#10b981", font=("Montserrat", 12, "bold")).pack(side=tk.RIGHT)

        # Log
        tk.Label(right_panel, text="NHẬT KÝ GIẢI", font=("Montserrat", 10, "bold"), bg="#1f2937", fg="#10b981").pack(anchor="w")
        self.log_text = tk.Text(right_panel, height=12, bg="#111827", fg="#cbd5e1", font=("Courier", 9), relief=tk.FLAT)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Solve Button
        self.solve_btn = tk.Button(right_panel, text="BẮT ĐẦU TÌM KIẾM", font=("Montserrat", 12, "bold"), bg="#10b981", fg="white", command=self._solve_puzzle, pady=10)
        self.solve_btn.pack(fill=tk.X, pady=(10, 0))

    def _on_algo_change(self, event=None):
        """Replicates UI constraints logic from main.py"""
        algo = self.algo_var.get()
        
        # 1. Uninformed searches: Disable both
        if algo in ["BFS", "DFS", "IDS", "UCS"]:
            self.heur_combo.config(state="disabled")
            self.variant_combo.config(state="disabled")
            
        # 2. Informed searches: Enable Heuristic, Disable Variant
        elif algo in ["A*", "Greedy", "Beam Search"]:
            self.heur_combo.config(state="readonly")
            self.variant_combo.config(state="disabled")
            
        # 3. Local search / Hybrid: Enable BOTH
        elif algo in ["Hill Climbing", "Random Restart", "Simulated Annealing"]:
            self.heur_combo.config(state="readonly")
            self.variant_combo.config(state="readonly")

    def _on_speed_change(self, value):
        """Cập nhật tốc độ animation từ slider"""
        self.animation_speed = int(value)

    def _create_grid(self, parent):
        grid_frame = tk.Frame(parent, bg="#374151", padx=2, pady=2)
        grid_frame.pack(pady=5)
        entries = []
        for i in range(9):
            ent = tk.Entry(grid_frame, width=3, font=("Montserrat", 18, "bold"), justify="center", bg="#1e293b", fg="#f3f4f6", borderwidth=0)
            ent.grid(row=i//3, column=i%3, padx=1, pady=1, ipady=10)
            entries.append(ent)
        return entries

    def _get_state_from_entries(self, entries):
        try:
            state = [int(e.get() if e.get().strip() != "" else 0) for e in entries]
            if sorted(state) != list(range(9)):
                raise ValueError("Ma trận phải chứa đủ các số từ 0-8")
            return tuple(state)
        except:
            return None

    def _set_entries_from_state(self, entries, state):
        for i, val in enumerate(state):
            entries[i].delete(0, tk.END)
            entries[i].insert(0, str(val))

    def _set_default_goal(self):
        self._set_entries_from_state(self.goal_entries, GOAL_STATE)

    def _randomize_valid(self):
        # Generate random goal
        g = list(range(9))
        random.shuffle(g)
        self._set_entries_from_state(self.goal_entries, g)
        
        # Generate random start
        s = list(range(9))
        random.shuffle(s)
        
        # Fix parity if needed
        if not self._check_solvability(tuple(s), tuple(g), silent=True):
            # Swap two non-zero adjacent elements to flip parity
            idx1, idx2 = [i for i, x in enumerate(s) if x != 0][:2]
            s[idx1], s[idx2] = s[idx2], s[idx1]
            
        self._set_entries_from_state(self.start_entries, s)

    def _count_inversions(self, state):
        inv_count = 0
        flat = [x for x in state if x != 0]
        for i in range(len(flat)):
            for j in range(i + 1, len(flat)):
                if flat[i] > flat[j]:
                    inv_count += 1
        return inv_count

    def _check_solvability(self, start, goal, silent=False):
        inv_start = self._count_inversions(start)
        inv_goal = self._count_inversions(goal)
        
        # Parity must match for 3x3 puzzle
        if (inv_start % 2) == (inv_goal % 2):
            return True
        
        if not silent:
            messagebox.showerror("Lỗi Cấu Hình", 
                f"Cấu hình này không thể giải được!\n\n"
                f"Inversions Start: {inv_start}\n"
                f"Inversions Goal: {inv_goal}\n"
                "Parity không trùng khớp.")
        return False

    def _solve_puzzle(self):
        if self.is_solving: return
        
        start_state = self._get_state_from_entries(self.start_entries)
        goal_state = self._get_state_from_entries(self.goal_entries)

        if not start_state or not goal_state:
            messagebox.showwarning("Dữ liệu lỗi", "Vui lòng nhập đủ các số từ 0 đến 8 cho cả hai bảng.")
            return

        if not self._check_solvability(start_state, goal_state):
            return

        algo_name = self.algo_var.get()
        heur_key = HEURISTICS.get(self.heur_var.get(), "manhattan")
        variant_key = VARIANTS.get(self.variant_var.get(), "simple")
        
        # Create dynamic solver
        try:
            algo_key = algo_name.lower().replace(" ", "_")
            # Handle names mapped in algorithms factory
            mapping = {"a*": "astar", "greedy": "greedy", "beam_search": "beam_search"}
            solver = create_solver(mapping.get(algo_key, algo_key), goal_state=goal_state, heuristic=heur_key, variant=variant_key)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Solver error: {e}")
            return

        self.is_solving = True
        self.solve_btn.config(state=tk.DISABLED, text="ĐANG GIẢI...", bg="#374151")
        self._clear_log()
        
        thread = threading.Thread(target=self._solve_worker, args=(solver, start_state, goal_state))
        thread.start()

    def _solve_worker(self, solver, start, goal):
        start_time = time.time()
        path, examined, steps = solver.solve(start)
        exec_time = time.time() - start_time

        if path:
            self.root.after(0, lambda: self._animate_solution(path, steps, examined, exec_time, goal))
        else:
            self.root.after(0, lambda: self._handle_failure())

    def _handle_failure(self):
        self.is_solving = False
        self.solve_btn.config(state=tk.NORMAL, text="BẮT ĐẦU TÌM KIẾM", bg="#10b981")
        messagebox.showinfo("Kết quả", "Không tìm thấy lời giải cho cấu hình này.")

    def _animate_solution(self, path, steps, examined, exec_time, goal_state):
        self.examined_var.set(str(examined))
        self.steps_var.set(str(len(path) - 1))
        self.time_var.set(f"{exec_time:.3f}s")
        
        self._log(f"--- THÔNG TIN ---")
        self._log(f"Thuật toán: {self.algo_var.get()}")
        self._log(f"Trạng thái: THÀNH CÔNG")
        self._log("-" * 20)

        def animate(idx):
            if idx >= len(path):
                self.is_solving = False
                self.solve_btn.config(state=tk.NORMAL, text="BẮT ĐẦU TÌM KIẾM", bg="#10b981")
                messagebox.showinfo("Hoàn tất", "Đã mô phỏng xong đường đi!")
                return
            
            state = path[idx]
            self._update_start_grid_visuals(state, goal_state)
            
            if steps and idx < len(steps):
                self._log(steps[idx])
            
            self.root.after(self.animation_speed, lambda: animate(idx + 1))

        animate(0)

    def _update_start_grid_visuals(self, state, goal_state):
        """Cập nhật Grid 1 để hiển thị quá trình chạy, highlight số đúng vị trí đích"""
        for i, val in enumerate(state):
            ent = self.start_entries[i]
            ent.delete(0, tk.END)
            ent.insert(0, str(val) if val != 0 else "")
            
            if val == 0:
                ent.config(bg="#111827", fg="#111827")
            elif val == goal_state[i]:
                ent.config(bg="#065f46", fg="#10b981") # Greenish for correct pos
            else:
                ent.config(bg="#1e293b", fg="#f3f4f6")

    def _log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, str(msg) + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ComplexPuzzleDashboard(root)
    root.mainloop()