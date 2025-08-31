import numpy as np

class NavigationMesh:
    def __init__(self):
        self.vertices = []
        self.triangles = []
        self.connections = {}
        
    def build_navmesh(self, scene):
        # Build navigation mesh from scene geometry
        print("Building navigation mesh...")
        
    def find_path(self, start, end):
        # A* pathfinding algorithm
        open_set = [start]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self._heuristic(start, end)}
        
        while open_set:
            current = min(open_set, key=lambda x: f_score.get(x, float('inf')))
            
            if current == end:
                return self._reconstruct_path(came_from, current)
                
            open_set.remove(current)
            
            for neighbor in self.connections.get(current, []):
                tentative_g_score = g_score[current] + self._distance(current, neighbor)
                
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self._heuristic(neighbor, end)
                    if neighbor not in open_set:
                        open_set.append(neighbor)
                        
        return []  # No path found
        
    def _heuristic(self, a, b):
        return np.linalg.norm(np.array(a) - np.array(b))
        
    def _distance(self, a, b):
        return np.linalg.norm(np.array(a) - np.array(b))
        
    def _reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]

class AIAgent:
    def __init__(self):
        self.position = [0, 0, 0]
        self.target = None
        self.path = []
        self.speed = 2.0
        self.state = "IDLE"  # IDLE, PATROL, CHASE, FLEE
        
    def update(self, delta_time, navmesh):
        if self.target and self.path:
            self._follow_path(delta_time, navmesh)
            
    def _follow_path(self, delta_time, navmesh):
        if not self.path:
            return
            
        target_pos = self.path[0]
        direction = np.array(target_pos) - np.array(self.position)
        distance = np.linalg.norm(direction)
        
        if distance > 0.1:
            direction = direction / distance
            move_distance = min(distance, self.speed * delta_time)
            self.position = (np.array(self.position) + direction * move_distance).tolist()
        else:
            self.path.pop(0)