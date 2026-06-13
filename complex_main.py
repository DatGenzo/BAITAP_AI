"""
8-Puzzle Solver - Complex Environment Dashboard (DUAL RACING MODE)
Giao diện chạy đua 2 trạng thái Bắt đầu về cùng 1 trạng thái Đích
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
from algorithms import (
    create_solver, GOAL_STATE, ALGORITHMS, HEURISTICS, VARIANTS
)

class ComplexPuzzleDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle - Dual Racing Environment")
        self.root.geometry("1400x900")  # Mở rộng chút xíu cho thoải mái
        self.root.configure(bg="#111827")
        
        self.is_solving_1 = False
        self.is_solving_2 = False
        self.animation_speed = 400
        
        self._setup_ui()
        self._set_default_goal()
        self._randomize_valid()

    def _setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#1f2937", height=80)
        header.pack(fill=tk.X)
        tk.Label(header, text="🏁 DUAL RACING SOLVER", font=("Montserrat", 20, "bold"), bg="#1f2937", fg="#10b981").pack(pady=10)

        # Main Container
        container = tk.Frame(self.root, bg="#111827")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # ==========================================
        # LEFT PANEL: GRIDS
        # ==========================================
        left_panel = tk.Frame(container, bg="#111827")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # GOAL GRID (Top Center)
        goal_frame = tk.Frame(left_panel, bg="#111827")
        goal_frame.pack(pady=(0, 20))
        tk.Label(goal_frame, text="👑 TRẠNG THÁI ĐÍCH CHUNG", font=("Montserrat", 13, "bold"), bg="#111827", fg="#fbbf24").pack(pady=(0,5))
        self.goal_entries = self._create_grid(goal_frame, border_color="#fbbf24")

        # STARTS CONTAINER (Side by Side)
        starts_container = tk.Frame(left_panel, bg="#111827")
        starts_container.pack(fill=tk.X, pady=10)

        # Start 1
        start1_frame = tk.Frame(starts_container, bg="#111827")
        start1_frame.pack(side=tk.LEFT, expand=True)
        tk.Label(start1_frame, text="🚗 TRẠNG THÁI BẮT ĐẦU 1", font=("Montserrat", 11, "bold"), bg="#111827", fg="#60a5fa").pack(pady=(0,5))
        self.start_entries_1 = self._create_grid(start1_frame, border_color="#3b82f6")

        # Start 2
        start2_frame = tk.Frame(starts_container, bg="#111827")
        start2_frame.pack(side=tk.RIGHT, expand=True)
        tk.Label(start2_frame, text="🚕 TRẠNG THÁI BẮT ĐẦU 2", font=("Montserrat", 11, "bold"), bg="#111827", fg="#f87171").pack(pady=(0,5))
        self.start_entries_2 = self._create_grid(start2_frame, border_color="#ef4444")

        # Grid Controls
        btn_frame = tk.Frame(left_panel, bg="#111827")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Goal Mặc Định", command=self._set_default_goal, bg="#4b5563", fg="white", font=("Montserrat", 9, "bold"), padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Random Hợp Lệ Cả Hai", command=self._randomize_valid, bg="#2563eb", fg="white", font=("Montserrat", 9, "bold"), padx=10).pack(side=tk.LEFT, padx=5)

        # ==========================================
        # RIGHT PANEL: DASHBOARD
        # ==========================================
        # Đặt width to hơn để chứa 2 cột log
        right_panel = tk.Frame(container, bg="#1f2937", padx=20, pady=20, width=550)
        right_panel.pack_propagate(False)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH)

        # --- Algorithm Settings ---
        tk.Label(right_panel, text="CẤU HÌNH THUẬT TOÁN CHUNG", font=("Montserrat", 12, "bold"), bg="#1f2937", fg="#10b981").pack(anchor="w")
        
        settings_grid = tk.Frame(right_panel, bg="#1f2937")
        settings_grid.pack(fill=tk.X, pady=10)

        tk.Label(settings_grid, text="Thuật toán:", bg="#1f2937", fg="#cbd5e1").grid(row=0, column=0, sticky="w")
        self.algo_var = tk.StringVar(value="A*")
        self.algo_combo = ttk.Combobox(settings_grid, textvariable=self.algo_var, values=list(ALGORITHMS.keys()), state="readonly", width=25)
        self.algo_combo.grid(row=0, column=1, padx=10, pady=5)
        self.algo_combo.bind("<<ComboboxSelected>>", self._on_algo_change)

        tk.Label(settings_grid, text="Heuristic:", bg="#1f2937", fg="#cbd5e1").grid(row=1, column=0, sticky="w")
        self.heur_var = tk.StringVar(value="Manhattan")
        self.heur_combo = ttk.Combobox(settings_grid, textvariable=self.heur_var, values=list(HEURISTICS.keys()), state="readonly", width=25)
        self.heur_combo.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(settings_grid, text="Tốc độ (ms):", bg="#1f2937", fg="#cbd5e1").grid(row=2, column=0, sticky="w")
        self.speed_var = tk.IntVar(value=400)
        speed_slider = tk.Scale(
            settings_grid, from_=50, to=2000, orient=tk.HORIZONTAL, 
            bg="#1f2937", fg="#10b981", variable=self.speed_var, 
            length=180, command=self._on_speed_change, highlightthickness=0, borderwidth=0
        )
        speed_slider.grid(row=2, column=1, padx=10, pady=0)

        self._on_algo_change()

        # --- Stats Area (Dual Columns) ---
        self.examined_var_1 = tk.StringVar(value="0")
        self.steps_var_1 = tk.StringVar(value="0")
        self.time_var_1 = tk.StringVar(value="0.000s")

        self.examined_var_2 = tk.StringVar(value="0")
        self.steps_var_2 = tk.StringVar(value="0")
        self.time_var_2 = tk.StringVar(value="0.000s")

        stats_box = tk.Frame(right_panel, bg="#111827", padx=10, pady=10)
        stats_box.pack(fill=tk.X, pady=10)
        
        # Headers cho bảng thống kê
        tk.Label(stats_box, text="Chỉ số", bg="#111827", fg="#94a3b8", width=12, anchor="w").grid(row=0, column=0, pady=5)
        tk.Label(stats_box, text="TRẠNG THÁI 1", bg="#111827", fg="#60a5fa", font=("Montserrat", 9, "bold")).grid(row=0, column=1, padx=10)
        tk.Label(stats_box, text="TRẠNG THÁI 2", bg="#111827", fg="#f87171", font=("Montserrat", 9, "bold")).grid(row=0, column=2, padx=10)

        stats_data = [
            ("Đã Duyệt", self.examined_var_1, self.examined_var_2),
            ("Số Bước", self.steps_var_1, self.steps_var_2),
            ("Thời Gian", self.time_var_1, self.time_var_2)
        ]

        for i, (label, var1, var2) in enumerate(stats_data, start=1):
            tk.Label(stats_box, text=label, bg="#111827", fg="#94a3b8", width=12, anchor="w").grid(row=i, column=0, pady=2)
            tk.Label(stats_box, textvariable=var1, bg="#111827", fg="#10b981", font=("Montserrat", 11, "bold")).grid(row=i, column=1)
            tk.Label(stats_box, textvariable=var2, bg="#111827", fg="#10b981", font=("Montserrat", 11, "bold")).grid(row=i, column=2)

        # --- Logs Area (Dual Columns) ---
        tk.Label(right_panel, text="NHẬT KÝ CHẠY ĐUA", font=("Montserrat", 10, "bold"), bg="#1f2937", fg="#10b981").pack(anchor="w", pady=(10, 0))
        
        logs_container = tk.Frame(right_panel, bg="#1f2937")
        logs_container.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text_1 = tk.Text(logs_container, width=25, bg="#111827", fg="#cbd5e1", font=("Courier", 9), relief=tk.FLAT)
        self.log_text_1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.log_text_2 = tk.Text(logs_container, width=25, bg="#111827", fg="#cbd5e1", font=("Courier", 9), relief=tk.FLAT)
        self.log_text_2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # --- Solve Button ---
        self.solve_btn = tk.Button(right_panel, text="BẮT ĐẦU ĐUA TỐC ĐỘ", font=("Montserrat", 12, "bold"), bg="#10b981", fg="white", command=self._solve_puzzle, pady=10)
        self.solve_btn.pack(fill=tk.X, pady=(10, 0))

    def _on_algo_change(self, event=None):
        algo = self.algo_var.get()
        if algo in ["BFS", "DFS", "IDS", "UCS"]:
            self.heur_combo.config(state="disabled")
        elif algo in ["A*", "Greedy", "Beam Search"]:
            self.heur_combo.config(state="readonly")
        elif algo in ["Hill Climbing", "Random Restart", "Simulated Annealing"]:
            self.heur_combo.config(state="readonly")

    def _on_speed_change(self, value):
        self.animation_speed = int(value)

    def _create_grid(self, parent, border_color="#374151"):
        grid_frame = tk.Frame(parent, bg=border_color, padx=3, pady=3)
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
                raise ValueError()
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
        # 1. Generate random goal
        g = list(range(9))
        random.shuffle(g)
        self._set_entries_from_state(self.goal_entries, g)
        
        # 2. Generate random valid starts for BOTH grids
        for entries in [self.start_entries_1, self.start_entries_2]:
            s = list(range(9))
            random.shuffle(s)
            # Fix parity
            if not self._check_solvability(tuple(s), tuple(g), silent=True):
                idx1, idx2 = [i for i, x in enumerate(s) if x != 0][:2]
                s[idx1], s[idx2] = s[idx2], s[idx1]
            self._set_entries_from_state(entries, s)

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
        if (inv_start % 2) == (inv_goal % 2):
            return True
        if not silent:
            messagebox.showerror("Lỗi", "Parity không khớp, không thể giải được!")
        return False

    def _solve_puzzle(self):
        if self.is_solving_1 or self.is_solving_2: 
            return
        
        start_state_1 = self._get_state_from_entries(self.start_entries_1)
        start_state_2 = self._get_state_from_entries(self.start_entries_2)
        goal_state = self._get_state_from_entries(self.goal_entries)

        if not start_state_1 or not start_state_2 or not goal_state:
            messagebox.showwarning("Dữ liệu lỗi", "Vui lòng nhập đủ các số từ 0 đến 8 cho tất cả các bảng.")
            return

        if not self._check_solvability(start_state_1, goal_state) or not self._check_solvability(start_state_2, goal_state):
            return

        algo_name = self.algo_var.get()
        heur_key = HEURISTICS.get(self.heur_var.get(), "manhattan")
        variant_key = "simple"
        
        try:
            algo_key = algo_name.lower().replace(" ", "_")
            mapping = {"a*": "astar", "greedy": "greedy", "beam_search": "beam_search"}
            
            # Khởi tạo 2 Solver độc lập để không ghi đè dữ liệu lịch sử
            solver_1 = create_solver(mapping.get(algo_key, algo_key), goal_state=goal_state, heuristic=heur_key, variant=variant_key)
            solver_2 = create_solver(mapping.get(algo_key, algo_key), goal_state=goal_state, heuristic=heur_key, variant=variant_key)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Solver error: {e}")
            return

        self.is_solving_1 = True
        self.is_solving_2 = True
        self.solve_btn.config(state=tk.DISABLED, text="ĐANG ĐUA...", bg="#374151")
        self._clear_logs()
        
        # Chạy 2 Threads song song
        threading.Thread(target=self._solve_worker, args=(solver_1, start_state_1, goal_state, 1)).start()
        threading.Thread(target=self._solve_worker, args=(solver_2, start_state_2, goal_state, 2)).start()

    def _solve_worker(self, solver, start, goal, player_id):
        start_time = time.time()
        path, examined, steps = solver.solve(start)
        exec_time = time.time() - start_time

        if path:
            self.root.after(0, lambda: self._animate_solution(path, steps, examined, exec_time, goal, player_id))
        else:
            self.root.after(0, lambda: self._handle_failure(player_id))

    def _handle_failure(self, player_id):
        self._log("Không tìm thấy đường đi!", player_id)
        if player_id == 1: self.is_solving_1 = False
        else: self.is_solving_2 = False
        self._check_all_done()

    def _animate_solution(self, path, steps, examined, exec_time, goal_state, player_id):
        # Cập nhật thông số tùy theo người chơi
        if player_id == 1:
            self.examined_var_1.set(str(examined))
            self.steps_var_1.set(str(len(path) - 1))
            self.time_var_1.set(f"{exec_time:.3f}s")
        else:
            self.examined_var_2.set(str(examined))
            self.steps_var_2.set(str(len(path) - 1))
            self.time_var_2.set(f"{exec_time:.3f}s")
            
        self._log(f"=== XE {player_id} ===", player_id)
        self._log(f"Thuật toán: {self.algo_var.get()}", player_id)

        def animate(idx):
            if idx >= len(path):
                self._log(">> ĐÃ VỀ ĐÍCH!", player_id)
                if player_id == 1: self.is_solving_1 = False
                else: self.is_solving_2 = False
                self._check_all_done()
                return
            
            state = path[idx]
            self._update_grid_visuals(state, goal_state, player_id)
            
            if steps and idx < len(steps):
                self._log(steps[idx], player_id)
            
            self.root.after(self.animation_speed, lambda: animate(idx + 1))

        animate(0)

    def _check_all_done(self):
        # Chỉ khi cả 2 đã chạy xong thì mới mở lại nút bấm
        if not self.is_solving_1 and not self.is_solving_2:
            self.solve_btn.config(state=tk.NORMAL, text="BẮT ĐẦU ĐUA TỐC ĐỘ", bg="#10b981")
            messagebox.showinfo("Hoàn tất", "Cuộc đua đã kết thúc!")

    def _update_grid_visuals(self, state, goal_state, player_id):
        entries = self.start_entries_1 if player_id == 1 else self.start_entries_2
        
        for i, val in enumerate(state):
            ent = entries[i]
            ent.delete(0, tk.END)
            ent.insert(0, str(val) if val != 0 else "")
            
            if val == 0:
                ent.config(bg="#111827", fg="#111827")
            elif val == goal_state[i]:
                ent.config(bg="#065f46", fg="#10b981")
            else:
                ent.config(bg="#1e293b", fg="#f3f4f6")

    def _log(self, msg, player_id):
        log_widget = self.log_text_1 if player_id == 1 else self.log_text_2
        log_widget.config(state=tk.NORMAL)
        log_widget.insert(tk.END, str(msg) + "\n")
        log_widget.see(tk.END)
        log_widget.config(state=tk.DISABLED)

    def _clear_logs(self):
        self.log_text_1.config(state=tk.NORMAL)
        self.log_text_1.delete("1.0", tk.END)
        self.log_text_1.config(state=tk.DISABLED)
        
        self.log_text_2.config(state=tk.NORMAL)
        self.log_text_2.delete("1.0", tk.END)
        self.log_text_2.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ComplexPuzzleDashboard(root)
    root.mainloop()