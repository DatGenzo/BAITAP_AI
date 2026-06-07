"""
8-Puzzle Solver - Dashboard GUI
Giao diện tổng hợp duy nhất cho tất cả các thuật toán
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from algorithms import (
    create_solver, shuffle_puzzle_state, get_move_direction,
    GOAL_STATE, ALGORITHMS, HEURISTICS, VARIANTS
)

class PuzzleDashboard:
    """Giao diện Dashboard tổng hợp cho tất cả các thuật toán"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver - Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg="#111827")
        
        # Puzzle state
        self.current_state = list(GOAL_STATE)
        self.goal_state = GOAL_STATE
        self.is_solving = False
        self.animation_speed = 400  # milliseconds
        
        # Create UI
        self._create_menu_panel()
        self._create_main_content()
        self._create_footer()
        
        # Initial shuffle
        self._shuffle_puzzle()
    
    def _create_menu_panel(self):
        """Tạo panel menu với các dropdown và slider"""
        menu_frame = tk.Frame(self.root, bg="#1f2937", height=120)
        menu_frame.pack(fill=tk.X, padx=0, pady=0)
        menu_frame.pack_propagate(False)
        
        # Title
        title = tk.Label(
            menu_frame,
            text="🧩 8-PUZZLE SOLVER DASHBOARD",
            font=("Montserrat", 18, "bold"),
            bg="#1f2937",
            fg="#10b981"
        )
        title.pack(pady=(10, 15))
        
        # Control Row
        control_frame = tk.Frame(menu_frame, bg="#1f2937")
        control_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Algorithm Selection
        tk.Label(control_frame, text="Thuật toán:", bg="#1f2937", fg="#f3f4f6", font=("Montserrat", 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.algorithm_var = tk.StringVar(value="BFS")
        algorithm_combo = ttk.Combobox(
            control_frame,
            textvariable=self.algorithm_var,
            values=list(ALGORITHMS.keys()),
            state="readonly",
            width=15
        )
        algorithm_combo.pack(side=tk.LEFT, padx=(0, 15))
        algorithm_combo.bind("<<ComboboxSelected>>", self._on_algorithm_change)
        
        # Heuristic Selection
        tk.Label(control_frame, text="Heuristic:", bg="#1f2937", fg="#f3f4f6", font=("Montserrat", 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.heuristic_var = tk.StringVar(value="Manhattan")
        self.heuristic_combo = ttk.Combobox(
            control_frame,
            textvariable=self.heuristic_var,
            values=list(HEURISTICS.keys()),
            state="readonly",
            width=15
        )
        self.heuristic_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        # Variant Selection (cho Hill Climbing)
        tk.Label(control_frame, text="Kiểu Leo:", bg="#1f2937", fg="#f3f4f6", font=("Montserrat", 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.variant_var = tk.StringVar(value="Simple")
        self.variant_combo = ttk.Combobox(
            control_frame,
            textvariable=self.variant_var,
            values=list(VARIANTS.keys()),
            state="readonly",
            width=12
        )
        self.variant_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        # Speed Slider
        tk.Label(control_frame, text="Tốc độ (ms):", bg="#1f2937", fg="#f3f4f6", font=("Montserrat", 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.speed_var = tk.IntVar(value=400)
        speed_slider = tk.Scale(
            control_frame,
            from_=50,
            to=2000,
            orient=tk.HORIZONTAL,
            bg="#111827",
            fg="#10b981",
            variable=self.speed_var,
            length=100,
            command=self._on_speed_change
        )
        speed_slider.pack(side=tk.LEFT, padx=(0, 15))
        
        # Speed Display
        self.speed_label = tk.Label(control_frame, text="400ms", bg="#1f2937", fg="#10b981", font=("Montserrat", 9, "bold"), width=6)
        self.speed_label.pack(side=tk.LEFT)
    
    def _create_main_content(self):
        """Tạo nội dung chính với bàn cờ + dashboard"""
        main_frame = tk.Frame(self.root, bg="#111827")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Left side - Puzzle board
        left_frame = tk.Frame(main_frame, bg="#111827")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        tk.Label(left_frame, text="Bàn Cờ Hiện Tại", font=("Montserrat", 12, "bold"), bg="#111827", fg="#10b981").pack()
        
        # Puzzle grid
        self.board_frame = tk.Frame(left_frame, bg="#1f2937", padx=5, pady=5)
        self.board_frame.pack(pady=10)
        
        self.cells = []
        for i in range(9):
            btn = tk.Button(
                self.board_frame,
                text="",
                font=("Montserrat", 20, "bold"),
                width=5,
                height=2,
                relief=tk.FLAT,
                bg="#1e293b",
                fg="#f3f4f6",
                command=lambda idx=i: self._cell_clicked(idx)
            )
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)
            self.cells.append(btn)
        
        # Control buttons
        button_frame = tk.Frame(left_frame, bg="#111827")
        button_frame.pack(fill=tk.X, pady=10)
        
        self.shuffle_btn = tk.Button(
            button_frame,
            text="🔀 Xáo Trộn",
            font=("Montserrat", 11, "bold"),
            bg="#2563eb",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self._shuffle_puzzle
        )
        self.shuffle_btn.pack(side=tk.LEFT, padx=5)
        
        self.solve_btn = tk.Button(
            button_frame,
            text="🤖 AI Giải",
            font=("Montserrat", 11, "bold"),
            bg="#10b981",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self._solve_puzzle
        )
        self.solve_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = tk.Button(
            button_frame,
            text="↺ Đặt Lại",
            font=("Montserrat", 11, "bold"),
            bg="#f59e0b",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self._reset_puzzle
        )
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Right side - Dashboard
        right_frame = tk.Frame(main_frame, bg="#1f2937", padx=15, pady=15)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(right_frame, text="📊 DASHBOARD THỐNG KÊ", font=("Montserrat", 12, "bold"), bg="#1f2937", fg="#10b981").pack(anchor="w")
        
        # Statistics boxes
        stats_frame = tk.Frame(right_frame, bg="#1f2937")
        stats_frame.pack(fill=tk.X, pady=(10, 15))
        
        # Examined states
        tk.Label(stats_frame, text="Đã Duyệt:", bg="#1f2937", fg="#cbd5e1", font=("Montserrat", 10)).pack(anchor="w")
        self.examined_var = tk.StringVar(value="0")
        tk.Label(stats_frame, textvariable=self.examined_var, bg="#1f2937", fg="#10b981", font=("Montserrat", 18, "bold")).pack(anchor="w")
        
        # Steps
        tk.Label(stats_frame, text="Số Bước Giải:", bg="#1f2937", fg="#cbd5e1", font=("Montserrat", 10)).pack(anchor="w", pady=(10, 0))
        self.steps_var = tk.StringVar(value="0")
        tk.Label(stats_frame, textvariable=self.steps_var, bg="#1f2937", fg="#10b981", font=("Montserrat", 18, "bold")).pack(anchor="w")
        
        # Execution time
        tk.Label(stats_frame, text="Thời Gian Chạy:", bg="#1f2937", fg="#cbd5e1", font=("Montserrat", 10)).pack(anchor="w", pady=(10, 0))
        self.time_var = tk.StringVar(value="0ms")
        tk.Label(stats_frame, textvariable=self.time_var, bg="#1f2937", fg="#10b981", font=("Montserrat", 18, "bold")).pack(anchor="w")
        
        # Steps log
        tk.Label(right_frame, text="📋 BÁO CÁO CÁC BƯỚC DI CHUYỂN", font=("Montserrat", 11, "bold"), bg="#1f2937", fg="#10b981").pack(anchor="w", pady=(15, 5))
        
        # Text area with scrollbar
        text_frame = tk.Frame(right_frame, bg="#111827")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(
            text_frame,
            font=("Courier", 9),
            bg="#111827",
            fg="#cbd5e1",
            relief=tk.FLAT,
            yscrollcommand=scrollbar.set,
            height=15,
            state=tk.DISABLED
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
    
    def _create_footer(self):
        """Tạo footer"""
        footer = tk.Frame(self.root, bg="#0f172a", height=40)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        info_text = tk.Label(
            footer,
            text="8-Puzzle Solver © 2026 | Refactored Dashboard with Unified Algorithms",
            bg="#0f172a",
            fg="#6b7280",
            font=("Montserrat", 9)
        )
        info_text.pack(pady=10)
    
    def _draw_board(self):
        """Vẽ lại bàn cờ"""
        for i, cell in enumerate(self.cells):
            value = self.current_state[i]
            cell.config(text=str(value) if value != 0 else "")
            
            if value == 0:
                cell.config(bg="#0f172a", fg="#111827")
            else:
                cell.config(bg="#1e293b", fg="#f3f4f6")
    
    def _cell_clicked(self, idx):
        """Xử lý khi nhấp vào ô"""
        if self.is_solving:
            return
        
        # Find blank (0) position
        blank_idx = self.current_state.index(0)
        
        # Check if move is valid (adjacent to blank)
        row, col = idx // 3, idx % 3
        blank_row, blank_col = blank_idx // 3, blank_idx % 3
        
        if abs(row - blank_row) + abs(col - blank_col) == 1:
            # Swap
            self.current_state[idx], self.current_state[blank_idx] = \
                self.current_state[blank_idx], self.current_state[idx]
            self._draw_board()
            
            # Check win
            if tuple(self.current_state) == self.goal_state:
                messagebox.showinfo("Thắng!", "Bạn đã giải được ma trận!")
    
    def _shuffle_puzzle(self):
        """Xáo trộn bàn cờ"""
        if self.is_solving:
            return
        
        self.current_state = shuffle_puzzle_state(self.goal_state, 40)
        self._draw_board()
        self._clear_log()
        self._update_stats(0, 0, 0)
    
    def _reset_puzzle(self):
        """Đặt lại bàn cờ"""
        if self.is_solving:
            return
        
        self.current_state = list(self.goal_state)
        self._draw_board()
        self._clear_log()
        self._update_stats(0, 0, 0)
    
    def _solve_puzzle(self):
        """Giải bài toán bằng thuật toán đã chọn"""
        if self.is_solving:
            messagebox.showwarning("Cảnh báo", "Đang giải, vui lòng chờ...")
            return
        
        # Get algorithm info
        algorithm = self.algorithm_var.get()
        heuristic = HEURISTICS.get(self.heuristic_var.get(), "manhattan")
        variant = VARIANTS.get(self.variant_var.get(), "simple")
        
        # Create solver
        try:
            # Gộp các thuật toán cần Heuristic vào một list
            if algorithm in ["A*", "Greedy", "Simulated Annealing"]:
                # Chuyển đổi tên để truyền đúng vào tham số (VD: "Simulated Annealing" -> "simulated_annealing")
                algo_key = algorithm.lower().replace(" ", "_")
                solver = create_solver(algo_key, heuristic=heuristic)
            elif algorithm == "Hill Climbing":
                solver = create_solver("hill_climbing", variant=variant)
            else:
                algo_map = {
                    "BFS": "bfs",
                    "DFS": "dfs",
                    "IDS": "ids",
                    "UCS": "ucs",  # Bổ sung mapping cho UCS
                    "Random Restart": "random_restart",
                    "Beam Search": "beam_search"
                }
                solver = create_solver(algo_map[algorithm])
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo solver: {str(e)}")
            return
        
        # Solve in separate thread
        thread = threading.Thread(
            target=self._solve_in_thread,
            args=(solver, algorithm, heuristic, variant)
        )
        thread.start()
    
    def _solve_in_thread(self, solver, algorithm, heuristic, variant):
        """Giải bài toán trong thread riêng"""
        self.is_solving = True
        self.shuffle_btn.config(state=tk.DISABLED)
        self.solve_btn.config(state=tk.DISABLED)
        self.reset_btn.config(state=tk.DISABLED)
        
        start_time = time.time()
        
        # Chạy thuật toán tìm kiếm (Nặng nhất, để ở thread riêng là đúng)
        start_state = tuple(self.current_state)
        path, nodes_examined, steps = solver.solve(start_state)
        
        execution_time = time.time() - start_time
        
        if path is None:
            self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không tìm được đường đi!"))
            self.root.after(0, self._enable_buttons)
            return
        
        # CHÚ Ý SỬA TẠI ĐÂY: Chuyển toàn bộ dữ liệu về Main Thread để vẽ giao diện an toàn
        self.root.after(0, lambda: self._animate_solution(path, steps, nodes_examined, execution_time))

    def _enable_buttons(self):
        """Kích hoạt lại các nút bấm"""
        self.is_solving = False
        self.shuffle_btn.config(state=tk.NORMAL)
        self.solve_btn.config(state=tk.NORMAL)
        self.reset_btn.config(state=tk.NORMAL)
    
    def _animate_solution(self, path, steps, nodes_examined, execution_time):
        """Hiển thị animation của giải pháp (Chạy trên Main Thread)"""
        self._clear_log()
        self._log(f"🤖 Thuật toán: {self.algorithm_var.get()}")
        self._log(f"📊 Trạng thái duyệt: {nodes_examined}")
        self._log(f"⏱️ Thời gian: {execution_time:.3f}s")
        self._log(f"📈 Số bước: {len(path) - 1}")
        self._log("─" * 40)
        
        self._update_stats(nodes_examined, len(path) - 1, execution_time)
        
        def animate(step_idx):
            if step_idx >= len(path):
                self._enable_buttons()
                messagebox.showinfo("Xong!", "Giải hoàn thành!")
                return
            
            self.current_state = list(path[step_idx])
            self._draw_board()
            
            # Kiểm tra log của từng bước di chuyển
            if steps and step_idx < len(steps):
                self._log(steps[step_idx])
            
            # Gọi bước tiếp theo dựa trên tốc độ slider (ms)
            self.root.after(self.animation_speed, lambda: animate(step_idx + 1))
        
        animate(0)
    
    def _update_stats(self, examined, steps, time_taken):
        """Cập nhật thống kê"""
        self.examined_var.set(str(examined))
        self.steps_var.set(str(steps))
        self.time_var.set(f"{time_taken:.3f}s")
    
    def _clear_log(self):
        """Xóa log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _log(self, text):
        """Thêm vào log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _on_algorithm_change(self, event=None):
        """Xử lý khi thay đổi thuật toán"""
        algorithm = self.algorithm_var.get()
        
        # Enable/disable heuristic options based on algorithm
        if algorithm in ["A*", "Greedy", "Simulated Annealing", "Random Restart", "Beam Search"]:
            self.heuristic_combo.config(state="readonly")
        else:
            self.heuristic_combo.config(state="disabled")
        
        # Enable/disable variant options based on algorithm
        if algorithm == "Hill Climbing":
            self.variant_combo.config(state="readonly")
        else:
            self.variant_combo.config(state="disabled")
    
    def _on_speed_change(self, value):
        """Xử lý khi thay đổi tốc độ"""
        self.animation_speed = int(value)
        self.speed_label.config(text=f"{value}ms")


def main():
    root = tk.Tk()
    app = PuzzleDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
