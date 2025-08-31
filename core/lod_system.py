class LODLevel:
    def __init__(self, distance, mesh_complexity):
        self.distance = distance
        self.mesh_complexity = mesh_complexity  # e.g., triangle count
        self.mesh_data = None

class LODSystem:
    def __init__(self):
        self.lod_levels = {}
        self.current_lod = {}
        
    def add_lod_level(self, object_name, distance, mesh_complexity):
        if object_name not in self.lod_levels:
            self.lod_levels[object_name] = []
        
        self.lod_levels[object_name].append(LODLevel(distance, mesh_complexity))
        self.lod_levels[object_name].sort(key=lambda x: x.distance)
        
    def update_lod(self, camera_position, objects):
        for obj in objects:
            if obj.name in self.lod_levels:
                distance = self._calculate_distance(camera_position, obj.position)
                appropriate_lod = self._get_appropriate_lod(obj.name, distance)
                self.current_lod[obj.name] = appropriate_lod
                
    def _calculate_distance(self, pos1, pos2):
        return ((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2 + (pos1[2]-pos2[2])**2)**0.5
        
    def _get_appropriate_lod(self, object_name, distance):
        levels = self.lod_levels.get(object_name, [])
        for level in levels:
            if distance <= level.distance:
                return level
        return levels[-1] if levels else None