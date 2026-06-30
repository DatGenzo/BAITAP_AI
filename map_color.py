import customtkinter as ctk
import tkinter as tk
import random
import math
from collections import deque

# Cấu hình giao diện mặc định
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Cấu hình hằng số bài toán
COLORS = ["#FF595E", "#8AC926", "#1982C4", "#FFCA3A"]
COLOR_NAMES = ["Đỏ", "Xanh lá", "Xanh dương", "Vàng"]

class MapColoringApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Map Coloring CSP - Python AI")
        self.geometry("1100x700")
        
        self.nodes = []
        self.edges = []
        self.assignment = {}
        self.steps = 0
        self.is_running = False
        self.algo_generator = None

        self.setup_ui()
        self.generate_random_graph()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self, width=350, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.sidebar_frame.grid_propagate(False)

        ctk.CTkLabel(self.sidebar_frame, text="Cài đặt Thuật toán", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(10, 10))

        ctk.CTkLabel(self.sidebar_frame, text="Thuật toán:", anchor="w").pack(fill="x", padx=10)
        # ĐÃ CẬP NHẬT: Thêm Min-Conflicts và AC-3 vào danh sách
        self.algo_combobox = ctk.CTkComboBox(self.sidebar_frame, values=[
            "Backtracking Search", 
            "Forward Checking",
            "Min-Conflicts (Local Search)",
            "AC-3 Preprocessing"
        ])
        self.algo_combobox.pack(fill="x", padx=10, pady=(0, 15))

        ctk.CTkLabel(self.sidebar_frame, text="Độ trễ / Bước chạy (ms):", anchor="w").pack(fill="x", padx=10)
        self.speed_slider = ctk.CTkSlider(self.sidebar_frame, from_=10, to=1000, number_of_steps=100)
        self.speed_slider.set(300)
        self.speed_slider.pack(fill="x", padx=10, pady=(0, 15))

        self.btn_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=10, pady=10)
        
        self.btn_random = ctk.CTkButton(self.btn_frame, text="Random Bản Đồ", fg_color="#4a4e69", hover_color="#22223b", command=self.generate_random_graph)
        self.btn_random.pack(side="left", expand=True, padx=(0, 5))

        self.btn_start = ctk.CTkButton(self.btn_frame, text="Bắt đầu Giải", command=self.start_algorithm)
        self.btn_start.pack(side="right", expand=True, padx=(5, 0))

        ctk.CTkLabel(self.sidebar_frame, text="Dashboard", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 5))
        
        self.lbl_steps = ctk.CTkLabel(self.sidebar_frame, text="Số bước (Steps): 0", anchor="w", font=ctk.CTkFont(family="Consolas"))
        self.lbl_steps.pack(fill="x", padx=10)
        
        self.lbl_status = ctk.CTkLabel(self.sidebar_frame, text="Trạng thái: Đang chờ...", anchor="w", text_color="#1982C4", font=ctk.CTkFont(weight="bold"))
        self.lbl_status.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(self.sidebar_frame, text="Assignment hiện tại:", anchor="w").pack(fill="x", padx=10)
        self.lbl_assignment = ctk.CTkLabel(self.sidebar_frame, text="{}", anchor="nw", justify="left", font=ctk.CTkFont(family="Consolas"))
        self.lbl_assignment.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(self.sidebar_frame, text="Lịch sử hoạt động:", anchor="w").pack(fill="x", padx=10)
        self.textbox_log = ctk.CTkTextbox(self.sidebar_frame, height=200, font=ctk.CTkFont(family="Consolas", size=12))
        self.textbox_log.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.textbox_log.configure(state="disabled")

        # --- MAIN CANVAS ---
        self.canvas_frame = ctk.CTkFrame(self)
        self.canvas_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#2b2b2b", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=2, pady=2)

    # --- HÀM UI & VISUALIZATION ---
    def log_message(self, msg):
        self.textbox_log.configure(state="normal")
        self.textbox_log.insert("end", f"[Bước {self.steps}] {msg}\n")
        self.textbox_log.see("end")
        self.textbox_log.configure(state="disabled")

    def update_dashboard(self, current_node_id=None):
        self.lbl_steps.configure(text=f"Số bước (Steps): {self.steps}")
        assign_texts = [f"{k}: {COLOR_NAMES[v]}" for k, v in self.assignment.items()]
        assign_str = ", ".join(assign_texts) if assign_texts else "{}"
        
        import textwrap
        wrapped_assign = "\n".join(textwrap.wrap(assign_str, width=40))
        self.lbl_assignment.configure(text=wrapped_assign)

        self.draw_graph(current_node_id)

    def draw_graph(self, current_node_id=None):
        self.canvas.delete("all")
        
        # Vẽ cạnh (Edges)
        for u, v in self.edges:
            n1 = next(n for n in self.nodes if n['id'] == u)
            n2 = next(n for n in self.nodes if n['id'] == v)
            self.canvas.create_line(n1['x'], n1['y'], n2['x'], n2['y'], fill="#666666", width=2)

        # Vẽ Node (Vùng đất)
        for node in self.nodes:
            x, y = node['x'], node['y']
            r = 25
            
            # Vòng sáng bao quanh Node đang xét
            if node['id'] == current_node_id:
                self.canvas.create_oval(x-r-7, y-r-7, x+r+7, y+r+7, outline="#FFCA3A", width=4)

            # Chọn màu tô
            color_idx = self.assignment.get(node['id'])
            fill_color = COLORS[color_idx] if color_idx is not None else "#ffffff"
            outline_color = "#ffffff" if node['id'] == current_node_id else "#888888"
            outline_width = 3 if node['id'] == current_node_id else 2

            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill_color, outline=outline_color, width=outline_width)
            
            text_color = "#ffffff" if color_idx is not None else "#000000"
            self.canvas.create_text(x, y, text=node['id'], fill=text_color, font=("Arial", 15, "bold"))

    def generate_random_graph(self):
        self.is_running = False
        self.btn_start.configure(state="normal")
        self.algo_combobox.configure(state="normal")
        
        self.nodes = []
        self.edges = []
        self.assignment = {}
        self.steps = 0
        
        self.lbl_status.configure(text="Trạng thái: Đang chờ...", text_color="#1982C4")
        self.textbox_log.configure(state="normal")
        self.textbox_log.delete("1.0", "end")
        self.textbox_log.configure(state="disabled")

        self.update() 
        w = self.canvas.winfo_width() or 700
        h = self.canvas.winfo_height() or 600
        num_nodes = random.randint(7, 12)
        
        # 1. Sinh tọa độ các Vùng
        for i in range(num_nodes):
            node_id = chr(65 + i)
            attempts = 0
            while attempts < 100:
                nx = random.randint(50, w - 50)
                ny = random.randint(50, h - 50)
                if all(math.hypot(nx - n['x'], ny - n['y']) > 100 for n in self.nodes):
                    self.nodes.append({'id': node_id, 'x': nx, 'y': ny})
                    break
                attempts += 1

        def ccw(A, B, C):
            return (C['y']-A['y']) * (B['x']-A['x']) > (B['y']-A['y']) * (C['x']-A['x'])

        def segments_intersect(A, B, C, D):
            return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

        def point_segment_distance(p, a, b):
            l2 = (a['x'] - b['x'])**2 + (a['y'] - b['y'])**2
            if l2 == 0: return math.hypot(p['x'] - a['x'], p['y'] - a['y'])
            t = max(0, min(1, ((p['x'] - a['x']) * (b['x'] - a['x']) + (p['y'] - a['y']) * (b['y'] - a['y'])) / l2))
            proj_x = a['x'] + t * (b['x'] - a['x'])
            proj_y = a['y'] + t * (b['y'] - a['y'])
            return math.hypot(p['x'] - proj_x, p['y'] - proj_y)

        # 2. Tạo đường nối
        possible_edges = []
        for i in range(len(self.nodes)):
            for j in range(i + 1, len(self.nodes)):
                n1, n2 = self.nodes[i], self.nodes[j]
                dist = math.hypot(n1['x'] - n2['x'], n1['y'] - n2['y'])
                possible_edges.append((dist, n1, n2))
                
        possible_edges.sort(key=lambda x: x[0])
        
        for dist, n1, n2 in possible_edges:
            is_valid = True
            for u, v in self.edges:
                if u in (n1['id'], n2['id']) or v in (n1['id'], n2['id']):
                    continue
                nu = next(n for n in self.nodes if n['id'] == u)
                nv = next(n for n in self.nodes if n['id'] == v)
                if segments_intersect(n1, n2, nu, nv):
                    is_valid = False
                    break
                    
            if is_valid:
                for n in self.nodes:
                    if n['id'] not in (n1['id'], n2['id']):
                        if point_segment_distance(n, n1, n2) < 40:
                            is_valid = False
                            break
                            
            if is_valid and random.random() < 0.85:
                self.edges.append((n1['id'], n2['id']))

        self.update_dashboard()

    # --- CORE THUẬT TOÁN CSP ---

    def is_consistent(self, var, color_idx, assignment):
        """Dùng cho Backtracking thuần"""
        for u, v in self.edges:
            neighbor = None
            if u == var: neighbor = v
            elif v == var: neighbor = u
            
            if neighbor and neighbor in assignment:
                if assignment[neighbor] == color_idx:
                    return False
        return True

    def backtrack_generator(self, assignment):
        """1. Backtracking Search Thuần"""
        if len(assignment) == len(self.nodes):
            return True

        unassigned = [n['id'] for n in self.nodes if n['id'] not in assignment]
        var = unassigned[0]
        
        yield ("log", f"Đang xét Vùng [{var}]", var)

        for c in range(len(COLORS)):
            self.steps += 1
            if self.is_consistent(var, c, assignment):
                assignment[var] = c
                yield ("update", f"Tô Vùng [{var}] = {COLOR_NAMES[c]}", var)
                
                result = yield from self.backtrack_generator(assignment)
                if result:
                    return True
                
                self.steps += 1
                del assignment[var]
                yield ("backtrack", f"QUAY LUI: Xóa màu Vùng [{var}] vì ngõ cụt!", var)
            else:
                self.steps += 1
                yield ("log", f"Thử màu {COLOR_NAMES[c]} cho [{var}] -> Bị trùng", var)

        yield ("fail", f"Vùng [{var}] thử hết màu vẫn sai -> Trả về Thất bại", var)
        return False

    def forward_checking_generator(self, assignment, domains):
        """2. Backtracking kết hợp Forward Checking"""
        if len(assignment) == len(self.nodes):
            return True

        unassigned = [n['id'] for n in self.nodes if n['id'] not in assignment]
        var = unassigned[0]
        
        available_colors_str = [COLOR_NAMES[c] for c in domains[var]]
        yield ("log", f"Xét [{var}] - Màu khả dụng: {available_colors_str}", var)

        for c in list(domains[var]):
            self.steps += 1
            assignment[var] = c
            yield ("update", f"Tô Vùng [{var}] = {COLOR_NAMES[c]}", var)

            domain_removals = []
            fc_failed = False
            
            for u, v in self.edges:
                neighbor = None
                if u == var: neighbor = v
                elif v == var: neighbor = u
                
                if neighbor and neighbor not in assignment:
                    if c in domains[neighbor]:
                        domains[neighbor].remove(c)
                        domain_removals.append((neighbor, c))
                        yield ("log", f"  -> FC: Xóa {COLOR_NAMES[c]} khỏi miền của [{neighbor}]", var)
                        
                        if len(domains[neighbor]) == 0:
                            fc_failed = True
                            yield ("log", f"  -> FC CẢNH BÁO: Vùng [{neighbor}] hết sạch màu! Phải quay lui sớm.", var)
                            break
            
            if not fc_failed:
                result = yield from self.forward_checking_generator(assignment, domains)
                if result:
                    return True
            
            self.steps += 1
            del assignment[var]
            
            for neighbor, removed_color in domain_removals:
                domains[neighbor].append(removed_color)
                domains[neighbor].sort()
                
            yield ("backtrack", f"QUAY LUI: Xóa màu Vùng [{var}]", var)

        yield ("fail", f"Vùng [{var}] thất bại -> Lùi về trước", var)
        return False

    # --- THÊM MỚI: CÁC HÀM HỖ TRỢ MIN-CONFLICTS ---
    
    def count_conflicts(self, var, color_idx, assignment):
        """Đếm số lượng xung đột nếu gán màu color_idx cho biến var"""
        conflicts = 0
        for u, v in self.edges:
            neighbor = None
            if u == var: neighbor = v
            elif v == var: neighbor = u

            if neighbor and neighbor in assignment:
                if assignment[neighbor] == color_idx:
                    conflicts += 1
        return conflicts

    def get_conflicted_vars(self, assignment):
        """Lấy danh sách các biến đang bị vi phạm ràng buộc"""
        conflicted = []
        for n in self.nodes:
            var = n['id']
            if self.count_conflicts(var, assignment.get(var, -1), assignment) > 0:
                conflicted.append(var)
        return conflicted

    def min_conflicts_generator(self, max_steps=1000):
        """3. Thuật toán Min-Conflicts (Local Search)"""
        # Bước 1: Khởi tạo ngẫu nhiên một trạng thái đầy đủ (Chấp nhận lỗi)
        for n in self.nodes:
            self.assignment[n['id']] = random.choice(range(len(COLORS)))
        
        yield ("log", "Khởi tạo ngẫu nhiên toàn bộ màu cho bản đồ...", None)

        # Bước 2: Vòng lặp tối ưu hóa cục bộ
        for step in range(max_steps):
            self.steps += 1
            conflicted_vars = self.get_conflicted_vars(self.assignment)

            # Nếu không còn biến nào xung đột -> Đã giải xong!
            if not conflicted_vars:
                yield ("success", "Tuyệt vời! Không còn xung đột nào.", None)
                return True

            # Chọn ngẫu nhiên 1 vùng đang bị lỗi
            var = random.choice(conflicted_vars)
            current_conflicts = self.count_conflicts(var, self.assignment[var], self.assignment)
            yield ("log", f"Chọn vùng lỗi: [{var}] (Đang có {current_conflicts} xung đột)", var)

            # Tìm màu thay thế giúp giảm thiểu xung đột nhất
            min_conflicts = float('inf')
            best_colors = []

            for c in range(len(COLORS)):
                conflicts = self.count_conflicts(var, c, self.assignment)
                if conflicts < min_conflicts:
                    min_conflicts = conflicts
                    best_colors = [c] # Reset danh sách nếu tìm thấy mốc thấp hơn
                elif conflicts == min_conflicts:
                    best_colors.append(c) # Lưu trữ thêm lựa chọn nếu hòa

            # Tránh bị kẹt (Local Minimum): Chọn ngẫu nhiên trong các màu tốt nhất
            best_color = random.choice(best_colors)
            old_color = self.assignment[var]
            self.assignment[var] = best_color

            if old_color != best_color:
                yield ("update", f"Đổi [{var}] sang {COLOR_NAMES[best_color]} -> Còn {min_conflicts} xung đột", var)
            else:
                yield ("log", f"Giữ nguyên màu {COLOR_NAMES[best_color]} cho [{var}] (Tối ưu nhất lúc này)", var)

        # Hết max_steps mà vẫn lỗi
        yield ("fail", f"Thất bại! Đã đạt giới hạn {max_steps} bước chạy.", None)
        return False

    # --- CẬP NHẬT: START ALGORITHM ---
    
    def start_algorithm(self):
        if self.is_running: return
        self.is_running = True
        self.btn_start.configure(state="disabled")
        self.algo_combobox.configure(state="disabled")
        
        self.assignment = {}
        self.steps = 0
        self.textbox_log.configure(state="normal")
        self.textbox_log.delete("1.0", "end")
        self.textbox_log.configure(state="disabled")
        
        self.lbl_status.configure(text="Đang giải (Running)...", text_color="#FFCA3A")
        
        # Chọn thuật toán dựa trên Combobox
        algo_choice = self.algo_combobox.get()
        if algo_choice == "Backtracking Search":
            self.algo_generator = self.backtrack_generator(self.assignment)
        elif algo_choice == "Forward Checking":
            initial_domains = {n['id']: list(range(len(COLORS))) for n in self.nodes}
            self.algo_generator = self.forward_checking_generator(self.assignment, initial_domains)
        elif algo_choice == "Min-Conflicts (Local Search)":
            self.algo_generator = self.min_conflicts_generator(max_steps=1000)
        elif algo_choice == "AC-3 Preprocessing":
            self.algo_generator = self.ac3_preprocessing_generator()
            
        self.run_next_step()

    def ac3_preprocessing_generator(self):
        """AC-3 Algorithm theo pseudocode chuẩn - Thu gọn domain và tô màu"""
        # Khởi tạo domain ban đầu cho tất cả các node
        domains = {n['id']: list(range(len(COLORS))) for n in self.nodes}
        
        # Khởi tạo hàng đợi với tất cả các cung (Xi, Xj) và (Xj, Xi)
        queue = deque()
        for u, v in self.edges:
            queue.append((u, v))
            queue.append((v, u))
        
        yield ("log", "Bắt đầu AC-3: Loại bỏ giá trị không nhất quán...", None)
        
        # Vòng lặp AC-3 chính (while queue is not empty)
        while queue:
            xi, xj = queue.popleft()
            self.steps += 1
            
            # RM-INCONSISTENT-VALUES(Xi, Xj)
            removed = False
            for x in list(domains[xi]):
                # if NO value y in DOMAIN[Xj] allows (x,y) to satisfy constraint
                found_support = False
                for y in domains[xj]:
                    if x != y:  # Constraint: x != y
                        found_support = True
                        break
                
                # Nếu không tìm thấy y hỗ trợ, xóa x
                if not found_support:
                    domains[xi].remove(x)
                    removed = True
                    yield ("log", f"AC-3: Xóa {COLOR_NAMES[x]} khỏi [{xi}]", xi)
            
            # if removed then: for each Xk in NEIGHBORS[Xi], add (Xk, Xi) to queue
            if removed:
                for u, v in self.edges:
                    if v == xi and u != xj:
                        queue.append((u, xi))
                    elif u == xi and v != xj:
                        queue.append((v, xi))
                yield ("log", f"AC-3: Domain [{xi}] = {[COLOR_NAMES[c] for c in domains[xi]]}", xi)
        
        yield ("log", "AC-3 hoàn tất! Bắt đầu gán màu từ domain tối ưu...", None)
        
        # Gán màu từ domain tối ưu (tuần tự, cập nhật domain neighbor)
        for n in self.nodes:
            node_id = n['id']
            if domains[node_id]:
                color = domains[node_id][0]  # Chọn màu nhỏ nhất
                self.assignment[node_id] = color
                self.steps += 1
                yield ("update", f"Gán [{node_id}] = {COLOR_NAMES[color]} (từ {[COLOR_NAMES[c] for c in domains[node_id]]})", node_id)
                
                # Xóa màu này khỏi domain của các node kế cạnh
                for u, v in self.edges:
                    if u == node_id and color in domains[v]:
                        domains[v].remove(color)
                    elif v == node_id and color in domains[u]:
                        domains[u].remove(color)
            else:
                yield ("log", f"CẢNH BÁO: [{node_id}] domain rỗng!", node_id)
        
        yield ("success", "AC-3 hoàn tất! Tô màu thành công từ domain tối ưu", None)
        return True

    def run_next_step(self):
        if not self.is_running:
            return

        try:
            action, msg, current_var = next(self.algo_generator)
            
            self.log_message(msg)
            self.update_dashboard(current_node_id=current_var)
            
            delay_ms = int(self.speed_slider.get())
            self.after(delay_ms, self.run_next_step)

        except StopIteration as e:
            self.is_running = False
            self.btn_start.configure(state="normal")
            self.algo_combobox.configure(state="normal")
            self.update_dashboard()
            
            success = e.value
            if success:
                self.log_message(">>> THÀNH CÔNG! <<<")
                self.lbl_status.configure(text="Hoàn thành (Success)!", text_color="#8AC926")
            else:
                self.log_message(">>> KHÔNG TÌM THẤY LỜI GIẢI! <<<")
                self.lbl_status.configure(text="Bó tay (Failure)!", text_color="#FF595E")

if __name__ == "__main__":
    app = MapColoringApp()
    app.mainloop()