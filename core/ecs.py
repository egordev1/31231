class Entity:
    def __init__(self, entity_id, name="Entity"):
        self.id = entity_id
        self.name = name
        self.components = {}
        self.enabled = True
        self.transform = None
        
    def add_component(self, component):
        component_type = type(component).__name__
        self.components[component_type] = component
        component.entity = self
        
    def get_component(self, component_type):
        return self.components.get(component_type)
        
    def has_component(self, component_type):
        return component_type in self.components

class Component:
    def __init__(self):
        self.entity = None
        self.enabled = True
        
    def start(self):
        pass
        
    def update(self, delta_time):
        pass

class TransformComponent(Component):
    def __init__(self, position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
        super().__init__()
        self.position = list(position)
        self.rotation = list(rotation)
        self.scale = list(scale)
        self.world_matrix = None

class MeshRendererComponent(Component):
    def __init__(self, mesh_path=None, material=None):
        super().__init__()
        self.mesh_path = mesh_path
        self.material = material
        self.cast_shadows = True
        self.receive_shadows = True

class CameraComponent(Component):
    def __init__(self, fov=60.0, near=0.1, far=1000.0):
        super().__init__()
        self.fov = fov
        self.near = near
        self.far = far
        self.clear_color = [0.2, 0.2, 0.2, 1.0]
        self.is_main = False

class ECSManager:
    def __init__(self):
        self.entities = {}
        self.systems = []
        self.next_entity_id = 0
        
    def create_entity(self, name="Entity"):
        entity_id = self.next_entity_id
        self.next_entity_id += 1
        entity = Entity(entity_id, name)
        self.entities[entity_id] = entity
        
        # Add transform component by default
        entity.add_component(TransformComponent())
        return entity
        
    def destroy_entity(self, entity_id):
        if entity_id in self.entities:
            del self.entities[entity_id]
            
    def add_system(self, system):
        self.systems.append(system)
        
    def update(self, delta_time):
        for system in self.systems:
            system.update(delta_time, self.entities)