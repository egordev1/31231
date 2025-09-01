import json
from .objects import GameObject

class Prefab:
    def __init__(self, name="Prefab"):
        self.name = name
        self.objects = []
        self.prefab_path = ""
    
    def create_from_object(self, obj, name=None):
        """Create prefab from existing object"""
        import copy
        prefab = Prefab(name or f"{obj.name}_Prefab")
        prefab.objects.append(copy.deepcopy(obj))
        return prefab
    
    def instantiate(self, position=(0, 0, 0)):
        """Create instance of prefab in scene"""
        instances = []
        for obj_data in self.objects:
            new_obj = GameObject(
                obj_data.name,
                [obj_data.position[i] + position[i] for i in range(3)],
                obj_data.color,
                obj_data.primitive_type,
                obj_data.material_name
            )
            new_obj.rotation = obj_data.rotation[:]
            new_obj.scale = obj_data.scale[:]
            instances.append(new_obj)
        return instances
    
    def save_to_file(self, path):
        """Save prefab to JSON file"""
        data = {
            'name': self.name,
            'objects': []
        }
        
        for obj in self.objects:
            obj_data = {
                'name': obj.name,
                'position': obj.position,
                'rotation': obj.rotation,
                'scale': obj.scale,
                'color': obj.color,
                'primitive_type': obj.primitive_type,
                'material_name': obj.material_name
            }
            data['objects'].append(obj_data)
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.prefab_path = path
    
    def load_from_file(self, path):
        """Load prefab from JSON file"""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            self.name = data['name']
            self.objects = []
            self.prefab_path = path
            
            for obj_data in data['objects']:
                obj = GameObject(
                    obj_data['name'],
                    obj_data['position'],
                    obj_data['color'],
                    obj_data['primitive_type'],
                    obj_data['material_name']
                )
                obj.rotation = obj_data['rotation']
                obj.scale = obj_data['scale']
                self.objects.append(obj)
            
            return True
        except Exception as e:
            print(f"Error loading prefab {path}: {e}")
            return False

class PrefabManager:
    def __init__(self):
        self.prefabs = {}
        self.prefab_paths = {}
    
    def register_prefab(self, name, prefab):
        self.prefabs[name] = prefab
    
    def load_prefab(self, path):
        prefab = Prefab()
        if prefab.load_from_file(path):
            self.prefabs[prefab.name] = prefab
            self.prefab_paths[prefab.name] = path
            return prefab
        return None
    
    def instantiate_prefab(self, name, position=(0, 0, 0)):
        if name in self.prefabs:
            return self.prefabs[name].instantiate(position)
        return []