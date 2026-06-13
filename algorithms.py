"""
8-Puzzle Solver - Core Algorithms
Tất cả các thuật toán AI được tích hợp trong một file duy nhất
"""

import time
import random
from collections import deque
import heapq
import math
from typing import Tuple, List, Optional, Dict

# Constants
GOAL_STATE = (1, 2, 3, 8, 0, 4, 7, 6, 5)
GRID_SIZE = 3
TOTAL_CELLS = 9
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # UP, DOWN, LEFT, RIGHT
MOVE_DIRECTIONS = {
    (-1, 0): "LÊN",
    (1, 0): "XUỐNG",
    (0, -1): "TRÁI",
    (0, 1): "PHẢI"
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_neighbors(state: tuple) -> list:
    """Generate all valid neighbor states from current state."""
    neighbors = []
    state_list = list(state)
    zi = state_list.index(0)
    r, c = zi // 3, zi % 3

    for dr, dc in MOVES:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            new_zi = nr * 3 + nc
            new_state = state_list[:]
            new_state[zi], new_state[new_zi] = new_state[new_zi], new_state[zi]
            neighbors.append(tuple(new_state))
    return neighbors


def shuffle_puzzle_state(goal_state: tuple, iterations: int = 40) -> list:
    """Shuffle puzzle by making random valid moves."""
    state = list(goal_state)
    for _ in range(iterations):
        zi = state.index(0)
        r, c = zi // 3, zi % 3
        
        valid_indices = []
        for dr, dc in MOVES:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                valid_indices.append(nr * 3 + nc)
        
        chosen_idx = random.choice(valid_indices)
        state[zi], state[chosen_idx] = state[chosen_idx], state[zi]
    
    return state


def get_move_direction(state_prev: tuple, state_curr: tuple) -> str:
    """Determine direction of blank move between states."""
    z_prev = state_prev.index(0)
    z_curr = state_curr.index(0)
    r_p, c_p = z_prev // 3, z_prev % 3
    r_c, c_c = z_curr // 3, z_curr % 3
    if r_c < r_p: return "LÊN"
    if r_c > r_p: return "XUỐNG"
    if c_c < c_p: return "TRÁI"
    if c_c > c_p: return "PHẢI"
    return ""


def manhattan_distance(state: tuple, goal_state: tuple = GOAL_STATE) -> int:
    """Calculate Manhattan distance heuristic."""
    distance = 0
    for i, value in enumerate(state):
        if value == 0:
            continue
        current_row, current_col = divmod(i, 3)
        goal_index = goal_state.index(value)
        goal_row, goal_col = divmod(goal_index, 3)
        distance += abs(current_row - goal_row) + abs(current_col - goal_col)
    return distance


def misplaced_tiles(state: tuple, goal_state: tuple = GOAL_STATE) -> int:
    """Calculate number of misplaced tiles heuristic."""
    count = 0
    for i in range(len(state)):
        if state[i] != goal_state[i] and state[i] != 0:
            count += 1
    return count


def reconstruct_path(parent_map: dict, goal_state: tuple, start_state: tuple) -> list:
    """Reconstruct solution path from parent map."""
    path = []
    current = goal_state
    while current is not None:
        path.append(current)
        current = parent_map.get(current)
    return path[::-1]


# ============================================================================
# ALGORITHM CLASSES
# ============================================================================

class PuzzleSolver:
    """Base class cho tất cả các thuật toán"""
    
    def __init__(self, goal_state: tuple = GOAL_STATE):
        self.goal_state = goal_state
        self.history = []  # Lưu lịch sử tìm kiếm để vẽ trực quan
    
    def solve(self, start_state: tuple) -> Tuple[Optional[List[tuple]], int, List[str]]:
        raise NotImplementedError

    def _generate_steps(self, path: List[tuple]) -> List[str]:
        """
        Tạo báo cáo chi tiết từng bước di chuyển kèm cấu trúc ma trận trực quan.
        Ký tự '_' đại diện cho ô trống số 0.
        """
        steps = []
        for i in range(1, len(path)):
            direction = get_move_direction(path[i-1], path[i])
            state = path[i]
            
            # Khởi tạo chuỗi vẽ ma trận 3x3 cho bước hiện tại
            matrix_rows = []
            for r in range(3):
                row_items = []
                for c in range(3):
                    val = state[r * 3 + c]
                    row_items.append("_" if val == 0 else str(val))
                matrix_rows.append("  ".join(row_items))
            matrix_str = "\n".join(matrix_rows)
            
            # Tạo format chuẩn hóa như hình ảnh yêu cầu
            step_desc = f"[Bước {i}]: AI di chuyển ô trống {direction}\n{matrix_str}\n"
            steps.append(step_desc)
        return steps


class BFSSolver(PuzzleSolver):
    """Breadth-First Search - Tìm kiếm theo chiều rộng"""
    
    def solve(self, start_state: tuple) -> Tuple[Optional[List[tuple]], int, List[str]]:
        self.history = []
        if start_state == self.goal_state:
            return [start_state], 0, ["Đã ở trạng thái đích"]
        
        frontier = deque([start_state])
        reached = {start_state}
        parent_map = {start_state: None}
        
        while frontier:
            current = frontier.popleft()
            for neighbor in get_neighbors(current):
                if neighbor not in reached:
                    parent_map[neighbor] = current
                    if neighbor == self.goal_state:
                        path = reconstruct_path(parent_map, neighbor, start_state)
                        return path, len(reached), self._generate_steps(path)
                    
                    reached.add(neighbor)
                    frontier.append(neighbor)
                    self.history.append(neighbor)
        
        return None, len(reached), ["Không tìm được đường đi"]


class DFSSolver(PuzzleSolver):
    """Depth-First Search - Tìm kiếm theo chiều sâu"""
    
    def solve(self, start_state: tuple) -> Tuple[Optional[List[tuple]], int, List[str]]:
        self.history = []
        if start_state == self.goal_state:
            return [start_state], 0, ["Đã ở trạng thái đích"]
        
        frontier = deque([start_state])
        reached = {start_state}
        parent_map = {start_state: None}
        
        while frontier:
            current = frontier.pop()
            for neighbor in get_neighbors(current):
                if neighbor not in reached:
                    parent_map[neighbor] = current
                    if neighbor == self.goal_state:
                        path = reconstruct_path(parent_map, neighbor, start_state)
                        return path, len(reached), self._generate_steps(path)
                    
                    reached.add(neighbor)
                    frontier.append(neighbor)
                    self.history.append(neighbor)
        
        return None, len(reached), ["Không tìm được đường đi"]


class IDSSolver(PuzzleSolver):
    """Iterative Deepening Search - Tìm kiếm sâu từng bước"""
    
    def solve(self, start_state: tuple, max_depth: int = 50) -> Tuple[Optional[List[tuple]], int, List[str]]:
        self.history = []
        if start_state == self.goal_state:
            return [start_state], 0, ["Đã ở trạng thái đích"]
        
        def depth_limited_search(start, limit):
            frontier = deque([(start, 0, [start])])
            result = "failure"
            
            while frontier:
                current_state, depth, path = frontier.pop()
                if current_state == self.goal_state:
                    return path, True, len(self.history)
                if depth >= limit:
                    result = "cutoff"
                else:
                    if current_state not in path[:-1]:
                        for neighbor in get_neighbors(current_state):
                            frontier.append((neighbor, depth + 1, path + [neighbor]))
                            self.history.append(neighbor)
            return None, False, len(self.history)
        
        depth = 0
        while depth <= max_depth:
            result, found, reached_count = depth_limited_search(start_state, depth)
            if found:
                return result, len(self.history), self._generate_steps(result)
            depth += 1
        
        return None, len(self.history), ["Không tìm được đường đi"]


class AStarSolver(PuzzleSolver):
    """A* Search - Tìm kiếm có heuristic"""
    
    def __init__(self, goal_state: tuple = GOAL_STATE, heuristic: str = "manhattan"):
        super().__init__(goal_state)
        self.heuristic = manhattan_distance if heuristic == "manhattan" else misplaced_tiles
    
    def solve(self, start_state: tuple) -> Tuple[Optional[List[tuple]], int, List[str]]:
        self.history = []
        if start_state == self.goal_state:
            return [start_state], 0, ["Đã ở trạng thái đích"]
        
        frontier = []
        heapq.heappush(frontier, (0, id(start_state), start_state))
        reached = {start_state: 0}
        parent_map = {start_state: None}
        g_score = {start_state: 0}
        
        counter = 0
        while frontier:
            f, _, current = heapq.heappop(frontier)
            counter += 1
            
            if current == self.goal_state:
                path = reconstruct_path(parent_map, current, start_state)
                return path, counter, self._generate_steps(path)
            
            current_g = g_score[current]
            for neighbor in get_neighbors(current):
                new_g = current_g + 1
                if neighbor not in reached or new_g < reached[neighbor]:
                    reached[neighbor] = new_g
                    g_score[neighbor] = new_g
                    f = new_g + self.heuristic(neighbor, self.goal_state)
                    parent_map[neighbor] = current
                    heapq.heappush(frontier, (f, id(neighbor), neighbor))
                    self.history.append(neighbor)
        
        return None, counter, ["Không tìm được đường đi"]


class HillClimbingSolver(PuzzleSolver):
    """Hill Climbing - Leo đồi đơn giản"""
    
    def __init__(self, goal_state: tuple = GOAL_STATE, variant: str = "simple"):
        super().__init__(goal_state)
        self.variant = variant
    
    def solve(self, start_state: tuple) -> Tuple[Optional[List[tuple]], int, List[str]]:
        self.history = []
        if start_state == self.goal_state:
            return [start_state], 0, ["Đã ở trạng thái đích"]
        
        current = start_state
        path = [current]
        counter = 1
        
        while current != self.goal_state:
            neighbors = get_neighbors(current)
            h_current = manhattan_distance(current, self.goal_state)
            best_neighbor = None
            best_h = h_current
            
            for neighbor in neighbors:
                h_neighbor = manhattan_distance(neighbor, self.goal_state)
                if h_neighbor < best_h:
                    best_neighbor = neighbor
                    best_h = h_neighbor
                    if self.variant == "simple":
                        break
            
            if best_neighbor is None:
                return None, counter, ["Kẹt tại cực tiểu cục bộ (Local Minimum)"]
            
            current = best_neighbor
            path.append(current)
            counter += 1
            self.history.append(current)
            
            if counter > 1000:
                break
        
        if current == self.goal_state:
            return path, counter, self._generate_steps(path)
        return None, counter, ["Không tìm được đường đi"]


class RandomRestartSolver(PuzzleSolver):
    """Random Restart - Khởi động lại ngẫu nhiên"""
    
    def solve(self, start_state: tuple, iterations: int = 15) -> Tuple[Optional[List[tuple]], int, List[str]]:
        self.history = []
        best_path = None
        best_nodes = float('inf')
        
        for attempt in range(iterations):
            current = start_state
            path = [current]
            
            if attempt > 0:
                for _ in range(random.randint(4, 10)):
                    ns = get_neighbors(current)
                    current = random.choice(ns)
                    path.append(current)
            
            counter = len(path)
            while current != self.goal_state and counter < 100:
                neighbors = get_neighbors(current)
                h_current = manhattan_distance(current, self.goal_state)
                best_neighbor = None
                best_h = h_current
                
                for neighbor in neighbors:
                    h_neighbor = manhattan_distance(neighbor, self.goal_state)
                    if h_neighbor < best_h:
                        best_neighbor = neighbor
                        best_h = h_neighbor
                        break
                
                if best_neighbor is None:
                    break
                
                current = best_neighbor
                path.append(current)
                counter += 1
                self.history.append(current)
            
            if current == self.goal_state:
                if counter < best_nodes:
                    best_path = path
                    best_nodes = counter
        
        if best_path:
            return best_path, len(self.history), self._generate_steps(best_path)
        return None, len(self.history), ["Không tìm được đường đi"]


class BeamSearchSolver(PuzzleSolver):
    """Beam Search - Tìm kiếm tia"""
    
    def solve(self, start_state: tuple, beam_width: int = 3) -> Tuple[Optional[List[tuple]], int, List[str]]:
        self.history = []
        if start_state == self.goal_state:
            return [start_state], 0, ["Đã ở trạng thái đích"]
        
        frontier = [start_state]
        parent_map = {start_state: None}
        counter = 0
        
        while frontier and counter < 10000:
            counter += 1
            next_frontier = []
            
            for node in frontier:
                for neighbor in get_neighbors(node):
                    if neighbor == self.goal_state:
                        parent_map[neighbor] = node
                        path = reconstruct_path(parent_map, neighbor, start_state)
                        return path, counter, self._generate_steps(path)
                    
                    if neighbor not in parent_map:
                        parent_map[neighbor] = node
                        h = manhattan_distance(neighbor, self.goal_state)
                        next_frontier.append((h, neighbor))
                    
                    self.history.append(neighbor)
            
            next_frontier.sort()
            frontier = [node for _, node in next_frontier[:beam_width]]
        
        return None, counter, ["Không tìm được đường đi"]

class UCSSolver(PuzzleSolver):
    """Uniform Cost Search - Tìm kiếm chi phí cực tiểu"""
    def solve(self, start_state: tuple) -> Tuple[Optional[List[tuple]], int, List[str]]:
        self.history = []
        if start_state == self.goal_state:
            return [start_state], 0, ["Đã ở trạng thái đích"]

        frontier = []
        heapq.heappush(frontier, (0, id(start_state), start_state))
        reached = {start_state: 0}
        parent_map = {start_state: None}

        counter = 0
        while frontier:
            g, _, current = heapq.heappop(frontier)
            counter += 1

            if current == self.goal_state:
                path = reconstruct_path(parent_map, current, start_state)
                return path, counter, self._generate_steps(path)

            for neighbor in get_neighbors(current):
                new_g = g + 1
                if neighbor not in reached or new_g < reached[neighbor]:
                    reached[neighbor] = new_g
                    parent_map[neighbor] = current
                    heapq.heappush(frontier, (new_g, id(neighbor), neighbor))
                    self.history.append(neighbor)

        return None, counter, ["Không tìm được đường đi"]


class GreedySolver(PuzzleSolver):
    """Greedy Best-First Search - Tìm kiếm tham lam"""
    def __init__(self, goal_state: tuple = GOAL_STATE, heuristic: str = "manhattan"):
        super().__init__(goal_state)
        self.heuristic = manhattan_distance if heuristic == "manhattan" else misplaced_tiles

    def solve(self, start_state: tuple) -> Tuple[Optional[List[tuple]], int, List[str]]:
        self.history = []
        if start_state == self.goal_state:
            return [start_state], 0, ["Đã ở trạng thái đích"]

        frontier = []
        h_start = self.heuristic(start_state, self.goal_state)
        heapq.heappush(frontier, (h_start, id(start_state), start_state))
        reached = {start_state}
        parent_map = {start_state: None}

        counter = 0
        while frontier:
            _, _, current = heapq.heappop(frontier)
            counter += 1

            if current == self.goal_state:
                path = reconstruct_path(parent_map, current, start_state)
                return path, counter, self._generate_steps(path)

            for neighbor in get_neighbors(current):
                if neighbor not in reached:
                    reached.add(neighbor)
                    parent_map[neighbor] = current
                    h = self.heuristic(neighbor, self.goal_state)
                    heapq.heappush(frontier, (h, id(neighbor), neighbor))
                    self.history.append(neighbor)

        return None, counter, ["Không tìm được đường đi"]


class SimulatedAnnealingSolver(PuzzleSolver):
    """Simulated Annealing - Luyện kim nhân tạo"""
    def __init__(self, goal_state: tuple = GOAL_STATE, heuristic: str = "manhattan"):
        super().__init__(goal_state)
        self.heuristic = manhattan_distance if heuristic == "manhattan" else misplaced_tiles

    def solve(self, start_state: tuple) -> Tuple[Optional[List[tuple]], int, List[str]]:
        self.history = []
        if start_state == self.goal_state:
            return [start_state], 0, ["Đã ở trạng thái đích"]

        current = start_state
        path = [current]
        counter = 1
        
        # Tham số luyện kim
        temperature = 100.0
        cooling_rate = 0.99
        min_temperature = 0.01

        while temperature > min_temperature:
            if current == self.goal_state:
                return path, counter, self._generate_steps(path)

            neighbors = get_neighbors(current)
            next_node = random.choice(neighbors)
            
            # Delta E = E_current - E_next (vì ta đang tìm Min của Heuristic)
            current_energy = self.heuristic(current, self.goal_state)
            next_energy = self.heuristic(next_node, self.goal_state)
            delta_e = current_energy - next_energy 

            if delta_e > 0:
                # Tốt hơn -> Chọn luôn
                current = next_node
                path.append(current)
            else:
                # Tệ hơn -> Chọn theo xác suất
                probability = math.exp(delta_e / temperature)
                if random.random() < probability:
                    current = next_node
                    path.append(current)

            counter += 1
            self.history.append(current)
            temperature *= cooling_rate

        if current == self.goal_state:
            return path, counter, self._generate_steps(path)
        return None, counter, ["Không tìm được đường đi (hết nhiệt độ)"]

class AndOrGraphSolver(PuzzleSolver):
    """
    Thuật toán Tìm kiếm Đồ thị AND-OR (AND-OR Graph Search) 
    Dành cho môi trường phức tạp/không tất định.
    """
    
    def __init__(self, goal_state: tuple = GOAL_STATE):
        super().__init__(goal_state)
        self.counter = 0

    def solve(self, start_state: tuple) -> Tuple[Optional[List[tuple]], int, List[str]]:
        self.history = []
        self.counter = 0
        
        # Chạy thuật toán chính theo mã giả
        plan = self._or_search(start_state, [])
        
        if plan is None or plan == "failure":
            return None, self.counter, ["Không tìm được kế hoạch (Failure)"]
            
        # Vì AND-OR sinh ra một cây kế hoạch (Plan Tree) thay vì một đường thẳng,
        # Ta sẽ trích xuất một đường đi mẫu thành công từ cây kế hoạch để hiển thị lên UI.
        path = self._extract_sample_path(start_state, plan)
        return path, self.counter, self._generate_steps(path)

    def _get_complex_results(self, state: tuple, neighbor: tuple) -> List[tuple]:
        """
        Giả lập môi trường phức tạp: Một hành động di chuyển (đến neighbor chính)
        có khả năng bị tác động môi trường tạo ra thêm 1 trạng thái phụ ngẫu nhiên.
        """
        results = [neighbor]
        # Tạo thêm 1 trạng thái nhiễu ngẫu nhiên từ các nút lân cận khác để làm môi trường "phức tạp"
        all_neighbors = get_neighbors(state)
        i = all_neighbors.index(neighbor)
        if len(all_neighbors) > i :
            extra_state = all_neighbors[(i + 1) % len(all_neighbors)]
            if extra_state != state:
                results.append(extra_state)
        return list(set(results))  # Loại bỏ trùng lặp

    def _or_search(self, state: tuple, path: list):
        """Hàm OR_SEARCH theo mã giả"""
        self.counter += 1
        self.history.append(state)
        
        # if state ∈ problem.goal_test: return []
        if state == self.goal_state:
            return []
            
        # if state ∈ path: return failure
        if state in path:
            return "failure"
            
        # for each action in problem.actions(state):
        for neighbor in get_neighbors(state):
            # result_states = problem.results(state, action)
            result_states = self._get_complex_results(state, neighbor)
            
            # plan = AND_SEARCH(result_states, problem, path + [state])
            plan = self._and_search(result_states, path + [state])
            
            # if plan ≠ failure: return [action, plan]
            if plan != "failure":
                return {"action_to": neighbor, "plan_tree": plan}
                
        return "failure"

    def _and_search(self, states: list, path: list):
        """Hàm AND_SEARCH theo mã giả"""
        # plans = empty mapping
        plans = {}
        
        # for each s in states:
        for s in states:
            # plan_s = OR_SEARCH(s, problem, path)
            plan_s = self._or_search(s, path)
            
            # if plan_s == failure: return failure
            if plan_s == "failure":
                return "failure"
                
            plans[s] = plan_s
            
        return plans

    def _extract_sample_path(self, start_state: tuple, plan) -> List[tuple]:
        """Trích xuất một đường đi từ cây kế hoạch AND-OR để vẽ lên giao diện"""
        path = [start_state]
        curr = plan
        curr_state = start_state
        
        while curr and isinstance(curr, dict) and "action_to" in curr:
            next_state = curr["action_to"]
            path.append(next_state)
            
            # Đi tiếp vào nhánh của trạng thái này trong cây AND
            plan_tree = curr["plan_tree"]
            if isinstance(plan_tree, dict) and next_state in plan_tree:
                curr = plan_tree[next_state]
            else:
                break
        return path
# ============================================================================
# FACTORY
# ============================================================================

def create_solver(algorithm: str, goal_state: tuple = GOAL_STATE, heuristic: str = "manhattan", variant: str = "simple") -> PuzzleSolver:
    algorithm = algorithm.lower().strip()
    if algorithm == "bfs": return BFSSolver(goal_state=goal_state)
    elif algorithm == "dfs": return DFSSolver(goal_state=goal_state)
    elif algorithm == "ids": return IDSSolver(goal_state=goal_state)
    elif algorithm == "ucs": return UCSSolver(goal_state=goal_state)
    elif algorithm == "astar": return AStarSolver(goal_state=goal_state, heuristic=heuristic)
    elif algorithm == "greedy": return GreedySolver(goal_state=goal_state, heuristic=heuristic)
    elif algorithm == "hill_climbing": return HillClimbingSolver(goal_state=goal_state, variant=variant)
    elif algorithm == "simulated_annealing": return SimulatedAnnealingSolver(goal_state=goal_state, heuristic=heuristic)
    elif algorithm == "random_restart": return RandomRestartSolver(goal_state=goal_state)
    elif algorithm == "beam_search": return BeamSearchSolver(goal_state=goal_state)
    elif algorithm == "and-or_graph": return AndOrGraphSolver(goal_state=goal_state)
    else: raise ValueError(f"Unknown algorithm: {algorithm}")

ALGORITHMS = {
    "BFS": "Breadth-First Search",
    "DFS": "Depth-First Search",
    "IDS": "Iterative Deepening Search",
    "UCS": "Uniform Cost Search",
    "A*": "A* Search",
    "Greedy": "Greedy Best-First Search",
    "Hill Climbing": "Hill Climbing",
    "Simulated Annealing": "Simulated Annealing",
    "Random Restart": "Random Restart",
    "Beam Search": "Beam Search",
    "AND-OR Graph": "AND-OR Graph Search"
}
HEURISTICS = {"Manhattan": "manhattan", "Misplaced Tiles": "misplaced"}
VARIANTS = {"Simple": "simple", "Steepest": "steepest"}