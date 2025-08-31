import json
from datetime import datetime
from .skybox import Skybox
from .physics import PhysicsEngine
from .animation import AnimationController
from .particle_system import ParticleSystem
from .lighting import LightingSystem
from .prefab import PrefabManager
from .scripting import ScriptManager
from .post_processing import PostProcessingStack
from .lod_system import LODSystem
from .asset_manager import AssetManager
from .optimization import SpatialPartitioning
from .pbr_material import PBRMaterial

class Scene:
    def __init__(self):
        self.objects = []
        self.selected_object = None
        self.skybox = Skybox()
        self.physics = PhysicsEngine()
        self.animations = AnimationController()
        self.particle_systems = []
        self.lighting = LightingSystem()
        self.prefab_manager = PrefabManager()
        
        # Новые системы
        self.script_manager = ScriptManager()
        self.post_processing = PostProcessingStack()
        self.lod_system = LODSystem()
        self.asset_manager = AssetManager()
        self.spatial_partitioning = SpatialPartitioning()
        
        # PBR материалы
        self.pbr_materials = {}
        
        # Scene settings
        self.name = "Untitled"
        self.ambient_light = [0.2, 0.2, 0.2, 1.0]
        self.gravity = [0, -9.81, 0]
        self.fog_enabled = False
        self.fog_color = [0.5, 0.5, 0.5, 1.0]
        self.fog_density = 0.01
        
        # Scene state
        self.is_playing = False
        self.play_time = 0.0
        self.use_optimization = True
        
        self.create_default_scene()
        self.setup_default_lighting()

    def create_default_scene(self):
        from .objects import GameObject
        
        self.objects = [
            GameObject("Cube1", (0, 0, 0), (1, 0.5, 0.3), primitive_type=0, material_name="Default"),
            GameObject("Sphere1", (3, 0, 0), (0.3, 0.8, 0.2), primitive_type=1, material_name="Metal"),
            GameObject("Cylinder1", (-3, 0, 0), (0.2, 0.4, 1.0), primitive_type=2, material_name="Plastic"),
        ]
        
        # Add physics to default objects
        for obj in self.objects:
            obj.add_collider("BOX", [1, 1, 1])
            obj.add_rigidbody()
        
        # Create a particle system for demonstration
        fire_ps = self.create_particle_system((0, 2, 0))
        fire_ps.start_color = [1.0, 0.3, 0.1, 1.0]
        fire_ps.end_color = [1.0, 1.0, 0.0, 0.0]
        fire_ps.start_size = 0.3
        fire_ps.end_size = 0.05
        fire_ps.start_lifetime = 1.5
        fire_ps.emission_rate = 20.0
        fire_ps.velocity_range = [-0.2, 0.2]
        
        # Initialize optimization
        self.optimize_scene()

    def setup_default_lighting(self):
        from .lighting import Light
        
        # Main directional light (sun)
        sun_light = Light("DIRECTIONAL", (0.5, 1.0, 0.5), (1.0, 1.0, 0.9), 1.0)
        self.lighting.add_light(sun_light)
        
        # Fill light
        fill_light = Light("DIRECTIONAL", (-0.5, 0.5, -0.5), (0.4, 0.4, 0.6), 0.3)
        self.lighting.add_light(fill_light)
        
        # Point light example
        point_light = Light("POINT", (0, 3, 0), (1.0, 0.8, 0.6), 0.8)
        self.lighting.add_light(point_light)

    def update(self, dt):
        if self.is_playing:
            self.play_time += dt
            
            # Update physics
            self.physics.gravity = self.gravity
            self.physics.update(dt, self.objects)
            
            # Update animations
            self.animations.update(dt)
            
            # Update scripts
            self.update_scripts(dt)
        
        # Always update particle systems
        for ps in self.particle_systems:
            ps.update(dt)
            
        # Update LOD system if camera is available
        if hasattr(self, 'camera_position'):
            self.lod_system.update_lod(self.camera_position, self.objects)

    def draw(self):
        # Apply post-processing if enabled
        if self.post_processing.effects:
            self.post_processing.apply_effects()
        
        # Draw skybox first
        self.skybox.draw()
        
        # Apply lighting
        self.lighting.apply_lights()
        
        # Apply fog if enabled
        if self.fog_enabled:
            from OpenGL.GL import glFogfv, glFogf, GL_FOG, GL_FOG_COLOR, GL_FOG_DENSITY
            glFogfv(GL_FOG_COLOR, self.fog_color)
            glFogf(GL_FOG_DENSITY, self.fog_density)
        
        # Get visible objects using spatial partitioning
        visible_objects = self.objects
        if self.use_optimization and hasattr(self, 'camera_position'):
            visible_objects = self.get_visible_objects()
        
        # Draw objects
        for obj in visible_objects:
            obj.draw()
        
        # Draw particle systems
        for ps in self.particle_systems:
            ps.draw()

    def play(self):
        """Start scene playback (game mode)"""
        self.is_playing = True
        self.play_time = 0.0
        self.animations.play_all()
        
        # Call start methods on scripts
        self.start_scripts()
        
        # Reset physics for all objects
        for obj in self.objects:
            if hasattr(obj, 'rigidbody') and obj.rigidbody:
                obj.rigidbody.velocity = [0, 0, 0]
                obj.rigidbody.angular_velocity = [0, 0, 0]

    def pause(self):
        """Pause scene playback"""
        self.is_playing = False
        self.animations.stop_all()

    def stop(self):
        """Stop scene playback and reset to edit mode"""
        self.is_playing = False
        self.play_time = 0.0
        self.animations.stop_all()
        
        # Reload scene to reset positions
        self.create_default_scene()

    # Object management
    def find_object(self, name):
        for obj in self.objects:
            if obj.name == name:
                return obj
        return None

    def add_object(self, obj):
        self.objects.append(obj)
        
        # Add to spatial partitioning
        if self.use_optimization:
            bounds = self._calculate_object_bounds(obj)
            self.spatial_partitioning.add_object(obj, bounds)
            
        return obj

    def remove_object(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)
            if self.selected_object == obj:
                self.selected_object = None
                
            # Remove from spatial partitioning
            if hasattr(self.spatial_partitioning, 'object_bounds'):
                self.spatial_partitioning.object_bounds.pop(obj, None)
                
            return True
        return False

    def clear(self):
        self.objects.clear()
        self.particle_systems.clear()
        self.animations = AnimationController()
        self.selected_object = None
        
        # Clear spatial partitioning
        self.spatial_partitioning = SpatialPartitioning()

    def get_object_names(self):
        return [obj.name for obj in self.objects]

    # Particle systems
    def create_particle_system(self, position=(0, 0, 0)):
        ps = ParticleSystem()
        ps.position = list(position)
        self.particle_systems.append(ps)
        return ps

    # Animation system
    def add_animation(self, animation):
        self.animations.add_animation(animation)

    def play_animations(self):
        self.animations.play_all()

    def stop_animations(self):
        self.animations.stop_all()

    # Lighting system
    def add_light(self, light_type="DIRECTIONAL", position=(0, 5, 0), color=(1, 1, 1), intensity=1.0):
        from .lighting import Light
        light = Light(light_type, position, color, intensity)
        return self.lighting.add_light(light)

    def get_lights(self):
        return self.lighting.lights

    def remove_light(self, index):
        if 0 <= index < len(self.lighting.lights):
            self.lighting.lights.pop(index)
            return True
        return False

    # Prefab system
    def instantiate_prefab(self, prefab_name, position=(0, 0, 0)):
        instances = self.prefab_manager.instantiate_prefab(prefab_name, position)
        for instance in instances:
            self.add_object(instance)
        return instances

    def create_prefab_from_object(self, obj, name=None):
        from .prefab import Prefab
        prefab = Prefab()
        return prefab.create_from_object(obj, name)

    def save_prefab(self, obj, path):
        prefab = self.create_prefab_from_object(obj)
        return prefab.save_to_file(path)

    def load_prefab(self, path):
        return self.prefab_manager.load_prefab(path)

    # Scripting system
    def add_script_component(self, obj, script_path):
        from .scripting import ScriptComponent
        script_component = ScriptComponent(script_path)
        if script_component.load_script(script_path):
            if not hasattr(obj, 'scripts'):
                obj.scripts = []
            obj.scripts.append(script_component)
            
            # Call start method
            script_component.call_method('start', obj)
            return True
        return False

    def update_scripts(self, delta_time):
        for obj in self.objects:
            if hasattr(obj, 'scripts'):
                for script in obj.scripts:
                    if script.enabled:
                        script.call_method('update', delta_time)

    def start_scripts(self):
        for obj in self.objects:
            if hasattr(obj, 'scripts'):
                for script in obj.scripts:
                    script.call_method('start', obj)

    # PBR Materials
    def add_pbr_material(self, name):
        material = PBRMaterial(name)
        self.pbr_materials[name] = material
        return material

    def get_pbr_material(self, name):
        return self.pbr_materials.get(name)

    # Optimization system
    def optimize_scene(self):
        # Calculate scene bounds for spatial partitioning
        scene_bounds = self._calculate_scene_bounds()
        self.spatial_partitioning.initialize(scene_bounds)
        
        # Add objects to spatial partitioning
        for obj in self.objects:
            bounds = self._calculate_object_bounds(obj)
            self.spatial_partitioning.add_object(obj, bounds)

    def get_visible_objects(self):
        if not self.use_optimization or not hasattr(self, 'camera_position'):
            return self.objects
            
        # Simple frustum approximation (would need proper frustum culling)
        return self.objects

    def _calculate_scene_bounds(self):
        # Calculate overall scene bounds
        if not self.objects:
            return [-100, -100, -100, 100, 100, 100]
            
        min_bounds = [float('inf')] * 3
        max_bounds = [float('-inf')] * 3
        
        for obj in self.objects:
            for i in range(3):
                min_bounds[i] = min(min_bounds[i], obj.position[i] - 5)
                max_bounds[i] = max(max_bounds[i], obj.position[i] + 5)
                
        return min_bounds + max_bounds

    def _calculate_object_bounds(self, obj):
        # Simple AABB calculation
        size = 1.0  # Default size
        if hasattr(obj, 'collider') and obj.collider:
            size = max(obj.collider.size) / 2
        else:
            size = max(obj.scale) / 2
            
        return [
            obj.position[0] - size, obj.position[1] - size, obj.position[2] - size,
            obj.position[0] + size, obj.position[1] + size, obj.position[2] + size
        ]

    # Post-processing
    def add_post_effect(self, effect):
        self.post_processing.add_effect(effect)

    def remove_post_effect(self, index):
        return self.post_processing.remove_effect(index)

    # LOD system
    def add_lod_level(self, object_name, distance, mesh_complexity):
        self.lod_system.add_lod_level(object_name, distance, mesh_complexity)

    # Asset management
    def import_asset(self, asset_path, asset_type):
        return self.asset_manager.import_asset(asset_path, asset_type)

    def get_asset(self, asset_id):
        return self.asset_manager.get_asset(asset_id)

    # Raycasting
    def raycast(self, origin, direction, max_distance=1000.0):
        closest_hit = None
        closest_distance = max_distance
        
        for obj in self.objects:
            if hasattr(obj, 'collider') and obj.collider and obj.collider.type == "BOX":
                hit, distance = self.ray_aabb_intersection(origin, direction, obj)
                if hit and distance < closest_distance:
                    closest_hit = obj
                    closest_distance = distance
        
        return closest_hit, closest_distance

    def ray_aabb_intersection(self, origin, direction, obj):
        if not hasattr(obj, 'collider') or not obj.collider:
            return False, float('inf')
        
        # Get AABB bounds in world space
        min_bound = [
            obj.position[0] - obj.collider.size[0] / 2 + obj.collider.center[0],
            obj.position[1] - obj.collider.size[1] / 2 + obj.collider.center[1],
            obj.position[2] - obj.collider.size[2] / 2 + obj.collider.center[2]
        ]
        max_bound = [
            obj.position[0] + obj.collider.size[0] / 2 + obj.collider.center[0],
            obj.position[1] + obj.collider.size[1] / 2 + obj.collider.center[1],
            obj.position[2] + obj.collider.size[2] / 2 + obj.collider.center[2]
        ]
        
        tmin = 0.0
        tmax = float('inf')
        
        for i in range(3):
            if abs(direction[i]) < 1e-6:
                # Ray is parallel to this axis
                if origin[i] < min_bound[i] or origin[i] > max_bound[i]:
                    return False, float('inf')
            else:
                ood = 1.0 / direction[i]
                t1 = (min_bound[i] - origin[i]) * ood
                t2 = (max_bound[i] - origin[i]) * ood
                
                if t1 > t2:
                    t1, t2 = t2, t1
                
                if t1 > tmin:
                    tmin = t1
                if t2 < tmax:
                    tmax = t2
                
                if tmin > tmax:
                    return False, float('inf')
        
        return True, tmin

    # Serialization
    def save_to_file(self, filename):
        """Save scene to JSON file"""
        try:
            scene_data = {
                'name': self.name,
                'objects': [],
                'settings': {
                    'ambient_light': self.ambient_light,
                    'gravity': self.gravity,
                    'fog_enabled': self.fog_enabled,
                    'fog_color': self.fog_color,
                    'fog_density': self.fog_density
                },
                'lighting': {
                    'lights': []
                },
                'metadata': {
                    'saved_date': datetime.now().isoformat(),
                    'version': '2.0',
                    'object_count': len(self.objects)
                }
            }
            
            # Save objects
            for obj in self.objects:
                obj_data = {
                    'name': obj.name,
                    'position': obj.position,
                    'rotation': obj.rotation,
                    'scale': obj.scale,
                    'color': obj.color,
                    'primitive_type': obj.primitive_type,
                    'material_name': obj.material_name,
                    'visible': obj.visible,
                    'static': obj.static,
                    'has_collider': obj.collider is not None,
                    'has_rigidbody': obj.rigidbody is not None,
                    'has_scripts': hasattr(obj, 'scripts') and bool(obj.scripts)
                }
                
                if obj.collider:
                    obj_data['collider'] = {
                        'type': obj.collider.type,
                        'size': obj.collider.size,
                        'center': obj.collider.center,
                        'is_trigger': obj.collider.is_trigger
                    }
                
                if obj.rigidbody:
                    obj_data['rigidbody'] = {
                        'mass': obj.rigidbody.mass,
                        'drag': obj.rigidbody.drag,
                        'use_gravity': obj.rigidbody.use_gravity,
                        'is_kinematic': obj.rigidbody.is_kinematic
                    }
                
                if hasattr(obj, 'scripts') and obj.scripts:
                    obj_data['scripts'] = [script.script_path for script in obj.scripts]
                
                scene_data['objects'].append(obj_data)
            
            # Save lights
            for light in self.lighting.lights:
                light_data = {
                    'type': light.type,
                    'position': light.position,
                    'color': light.color,
                    'intensity': light.intensity,
                    'enabled': light.enabled,
                    'range': light.range,
                    'spot_angle': light.spot_angle
                }
                scene_data['lighting']['lights'].append(light_data)
            
            with open(filename, 'w') as f:
                json.dump(scene_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving scene: {e}")
            return False

    def load_from_file(self, filename):
        """Load scene from JSON file"""
        try:
            with open(filename, 'r') as f:
                scene_data = json.load(f)
            
            self.clear()
            self.name = scene_data.get('name', 'Untitled')
            
            # Load settings
            if 'settings' in scene_data:
                settings = scene_data['settings']
                self.ambient_light = settings.get('ambient_light', [0.2, 0.2, 0.2, 1.0])
                self.gravity = settings.get('gravity', [0, -9.81, 0])
                self.fog_enabled = settings.get('fog_enabled', False)
                self.fog_color = settings.get('fog_color', [0.5, 0.5, 0.5, 1.0])
                self.fog_density = settings.get('fog_density', 0.01)
            
            # Load objects
            from .objects import GameObject
            from .physics import Collider, Rigidbody
            
            for obj_data in scene_data['objects']:
                obj = GameObject(
                    obj_data['name'],
                    obj_data['position'],
                    obj_data['color'],
                    obj_data['primitive_type'],
                    obj_data.get('material_name', 'Default')
                )
                obj.rotation = obj_data['rotation']
                obj.scale = obj_data['scale']
                obj.visible = obj_data.get('visible', True)
                obj.static = obj_data.get('static', False)
                
                # Load collider
                if obj_data.get('has_collider', False) and 'collider' in obj_data:
                    collider_data = obj_data['collider']
                    obj.add_collider(
                        collider_data.get('type', 'BOX'),
                        collider_data.get('size', [1, 1, 1])
                    )
                    obj.collider.center = collider_data.get('center', [0, 0, 0])
                    obj.collider.is_trigger = collider_data.get('is_trigger', False)
                
                # Load rigidbody
                if obj_data.get('has_rigidbody', False) and 'rigidbody' in obj_data:
                    rb_data = obj_data['rigidbody']
                    obj.add_rigidbody(
                        rb_data.get('mass', 1.0),
                        rb_data.get('use_gravity', True)
                    )
                    obj.rigidbody.drag = rb_data.get('drag', 0.1)
                    obj.rigidbody.is_kinematic = rb_data.get('is_kinematic', False)
                
                # Load scripts
                if obj_data.get('has_scripts', False) and 'scripts' in obj_data:
                    for script_path in obj_data['scripts']:
                        self.add_script_component(obj, script_path)
                
                self.objects.append(obj)
            
            # Load lights
            if 'lighting' in scene_data:
                from .lighting import Light
                for light_data in scene_data['lighting']['lights']:
                    light = Light(
                        light_data.get('type', 'DIRECTIONAL'),
                        light_data.get('position', [0, 5, 0]),
                        light_data.get('color', [1, 1, 1]),
                        light_data.get('intensity', 1.0)
                    )
                    light.enabled = light_data.get('enabled', True)
                    light.range = light_data.get('range', 10.0)
                    light.spot_angle = light_data.get('spot_angle', 45.0)
                    self.lighting.add_light(light)
            
            # Re-optimize scene
            self.optimize_scene()
            
            return True
            
        except Exception as e:
            print(f"Error loading scene: {e}")
            return False