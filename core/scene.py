import json
import os
import time
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple

# Базовые импорты
from .skybox import Skybox
from .physics import PhysicsEngine
from .animation import AnimationController
from .particle_system import ParticleSystem
from .lighting import LightingSystem
from .prefab import PrefabManager

# Ленивые импорты для избежания циклических зависимостей
def import_scripting():
    try:
        from .scripting import ScriptEngine, MonoBehaviour, Time, Vector3
        return ScriptEngine, MonoBehaviour, Time, Vector3
    except ImportError:
        return None, None, None, None

def import_post_processing():
    try:
        from .post_processing import PostProcessingStack
        return PostProcessingStack
    except ImportError:
        return None

def import_lod_system():
    try:
        from .lod_system import LODSystem
        return LODSystem
    except ImportError:
        return None

def import_asset_manager():
    try:
        from .asset_manager import AssetManager
        return AssetManager
    except ImportError:
        return None

def import_optimization():
    try:
        from .optimization import SpatialPartitioning
        return SpatialPartitioning
    except ImportError:
        return None

def import_pbr_material():
    try:
        from .pbr_material import PBRMaterial
        return PBRMaterial
    except ImportError:
        return None

class Scene:
    def __init__(self):
        # Основные свойства сцены
        self.name = "Untitled"
        self.objects: List[Any] = []
        self.selected_object = None
        
        # Системы
        self.skybox = Skybox()
        self.physics = PhysicsEngine()
        self.animations = AnimationController()
        self.particle_systems: List[ParticleSystem] = []
        self.lighting = LightingSystem()
        self.prefab_manager = PrefabManager()
        
        # Ленивая инициализация систем
        self.script_engine, self.MonoBehaviour, self.Time, self.Vector3 = import_scripting()
        self.PostProcessingStack = import_post_processing()
        self.LODSystem = import_lod_system()
        self.AssetManager = import_asset_manager()
        self.SpatialPartitioning = import_optimization()
        self.PBRMaterial = import_pbr_material()
        
        # Инициализация систем
        self.post_processing = self.PostProcessingStack() if self.PostProcessingStack else None
        self.lod_system = self.LODSystem() if self.LODSystem else None
        self.asset_manager = self.AssetManager() if self.AssetManager else None
        self.spatial_partitioning = self.SpatialPartitioning() if self.SpatialPartitioning else None
        
        # PBR материалы
        self.pbr_materials: Dict[str, Any] = {}
        
        # Настройки сцены
        self.ambient_light = [0.2, 0.2, 0.2, 1.0]
        self.gravity = [0, -9.81, 0]
        self.fog_enabled = False
        self.fog_color = [0.5, 0.5, 0.5, 1.0]
        self.fog_density = 0.01
        
        # Состояние сцены
        self.is_playing = False
        self.play_time = 0.0
        self.delta_time = 0.0
        self.use_optimization = True
        self._last_update_time = time.time()
        
        # Инициализация
        self.setup_scripting()
        self.create_default_scene()
        self.setup_default_lighting()
        self.optimize_scene()

    def setup_scripting(self):
        """Настроить систему скриптинга"""
        if self.script_engine:
            # Добавляем ссылку на сцену для всех объектов
            for obj in self.objects:
                obj._scene = self
            
            # Регистрируем стандартные скрипты
            self.register_default_scripts()

    def register_default_scripts(self):
        """Зарегистрировать стандартные скрипты"""
        if not self.script_engine:
            return
            
        try:
            from .scripting import PlayerController, Rotator, Mover
            self.script_engine.register_script_type("PlayerController", PlayerController)
            self.script_engine.register_script_type("Rotator", Rotator)
            self.script_engine.register_script_type("Mover", Mover)
        except ImportError:
            print("Warning: Default scripts not available")

    def create_default_scene(self):
        """Создать сцену по умолчанию"""
        from .objects import GameObject
        
        # Создаем объекты
        self.objects = [
            self.create_game_object("Ground", (0, -1, 0), (10, 1, 10), (0.3, 0.6, 0.3), 3, "Ground"),
            self.create_game_object("Player", (0, 1, 0), (1, 2, 1), (0.2, 0.5, 0.8), 0, "Player"),
            self.create_game_object("Enemy", (3, 1, 0), (1, 2, 1), (0.8, 0.2, 0.2), 0, "Enemy"),
            self.create_game_object("Obstacle", (-3, 1, 0), (1, 2, 1), (0.7, 0.7, 0.2), 0, "Obstacle"),
        ]
        
        # Добавляем физику
        for obj in self.objects:
            obj.add_collider("BOX", obj.scale)
            obj.add_rigidbody(mass=1.0 if obj.name != "Ground" else 0.0)
            
            # Ground не должен двигаться
            if obj.name == "Ground":
                obj.rigidbody.is_kinematic = True
        
        # Создаем систему частиц
        fire_ps = self.create_particle_system((0, 2, 0))
        fire_ps.start_color = [1.0, 0.3, 0.1, 1.0]
        fire_ps.end_color = [1.0, 1.0, 0.0, 0.0]
        fire_ps.start_size = 0.3
        fire_ps.end_size = 0.05
        fire_ps.start_lifetime = 1.5
        fire_ps.emission_rate = 20.0
        fire_ps.velocity_range = [-0.2, 0.2]

    def create_game_object(self, name, position, scale, color, primitive_type, tag="Untagged"):
        """Создать игровой объект"""
        from .objects import GameObject
        
        obj = GameObject(name, position, color, primitive_type)
        obj.scale = list(scale)
        obj.tag = tag
        obj._scene = self  # Ссылка на сцену для скриптов
        
        return obj

    def setup_default_lighting(self):
        """Настроить освещение по умолчанию"""
        from .lighting import Light
        
        # Основной направленный свет (солнце)
        sun_light = Light("DIRECTIONAL", (0.5, 1.0, 0.5), (1.0, 1.0, 0.9), 1.0)
        self.lighting.add_light(sun_light)
        
        # Заполняющий свет
        fill_light = Light("DIRECTIONAL", (-0.5, 0.5, -0.5), (0.4, 0.4, 0.6), 0.3)
        self.lighting.add_light(fill_light)
        
        # Точечный свет
        point_light = Light("POINT", (0, 3, 0), (1.0, 0.8, 0.6), 0.8)
        self.lighting.add_light(point_light)

    def update(self, dt: Optional[float] = None):
        """Обновить сцену"""
        if dt is None:
            current_time = time.time()
            self.delta_time = current_time - self._last_update_time
            self._last_update_time = current_time
        else:
            self.delta_time = dt
        
        if self.is_playing:
            self.play_time += self.delta_time
            
            # Обновляем физику
            self.physics.gravity = self.gravity
            self.physics.update(self.delta_time, self.objects)
            
            # Обновляем анимации
            self.animations.update(self.delta_time)
            
            # Обновляем скрипты
            self.update_scripts()
            
            # Обрабатываем коллизии для скриптов
            self.handle_script_collisions()
        
        # Всегда обновляем системы частиц
        for ps in self.particle_systems:
            ps.update(self.delta_time)
            
        # Обновляем LOD систему
        if self.lod_system and hasattr(self, 'camera_position'):
            self.lod_system.update_lod(self.camera_position, self.objects)
            
        # Обновляем время для скриптов
        if self.Time:
            self.Time.update(self.delta_time)

    def update_scripts(self):
        """Обновить все скрипты"""
        if not self.script_engine:
            return
            
        self.script_engine.update(self.delta_time)

    def handle_script_collisions(self):
        """Обработать коллизии для скриптов"""
        if not self.script_engine:
            return
            
        # Здесь должна быть логика обработки коллизий и вызова
        # методов OnCollisionEnter/Exit в скриптах
        pass

    def draw(self):
        """Отрисовать сцену"""
        # Пост-обработка
        if self.post_processing and self.post_processing.effects:
            self.post_processing.apply_effects()
        
        # Небо
        self.skybox.draw()
        
        # Освещение
        self.lighting.apply_lights()
        
        # Туман
        if self.fog_enabled:
            from OpenGL.GL import glFogfv, glFogf, GL_FOG, GL_FOG_COLOR, GL_FOG_DENSITY
            glFogfv(GL_FOG_COLOR, self.fog_color)
            glFogf(GL_FOG_DENSITY, self.fog_density)
        
        # Видимые объекты (с оптимизацией)
        visible_objects = self.get_visible_objects()
        
        # Отрисовка объектов
        for obj in visible_objects:
            obj.draw()
        
        # Отрисовка систем частиц
        for ps in self.particle_systems:
            ps.draw()

    def get_visible_objects(self):
        """Получить видимые объекты"""
        if not self.use_optimization or not hasattr(self, 'camera_position'):
            return self.objects
            
        if self.spatial_partitioning:
            return self.spatial_partitioning.get_visible_objects(self.camera_position)
        
        return self.objects

    def play(self):
        """Запустить воспроизведение сцены"""
        self.is_playing = True
        self.play_time = 0.0
        self._last_update_time = time.time()
        
        # Запускаем анимации
        self.animations.play_all()
        
        # Запускаем скрипты
        self.start_scripts()
        
        # Сбрасываем физику
        for obj in self.objects:
            if hasattr(obj, 'rigidbody') and obj.rigidbody:
                obj.rigidbody.velocity = [0, 0, 0]
                obj.rigidbody.angular_velocity = [0, 0, 0]
        
        print(f"Scene '{self.name}' started")

    def pause(self):
        """Приостановить воспроизведение"""
        self.is_playing = False
        self.animations.stop_all()
        print(f"Scene '{self.name}' paused")

    def stop(self):
        """Остановить воспроизведение"""
        self.is_playing = False
        self.play_time = 0.0
        self.animations.stop_all()
        self.stop_scripts()
        
        # Восстанавливаем исходное состояние
        self.create_default_scene()
        print(f"Scene '{self.name}' stopped")

    def start_scripts(self):
        """Запустить все скрипты"""
        if self.script_engine:
            self.script_engine.start_all()

    def stop_scripts(self):
        """Остановить все скрипты"""
        if self.script_engine:
            self.script_engine.stop_all()

    # Управление объектами
    def find_object(self, name: str):
        """Найти объект по имени"""
        for obj in self.objects:
            if obj.name == name:
                return obj
        return None

    def find_objects_with_tag(self, tag: str):
        """Найти все объекты с тегом"""
        return [obj for obj in self.objects if hasattr(obj, 'tag') and obj.tag == tag]

    def add_object(self, obj):
        """Добавить объект в сцену"""
        obj._scene = self  # Добавляем ссылку на сцену
        self.objects.append(obj)
        
        # Добавляем в пространственное разбиение
        if self.use_optimization and self.spatial_partitioning:
            bounds = self._calculate_object_bounds(obj)
            self.spatial_partitioning.add_object(obj, bounds)
            
        # Регистрируем скрипты объекта
        if self.script_engine and hasattr(obj, 'scripts'):
            for script in obj.scripts:
                self.script_engine.register_script(script)
        
        return obj

    def remove_object(self, obj):
        """Удалить объект из сцены"""
        if obj in self.objects:
            self.objects.remove(obj)
            
            # Убираем из пространственного разбиения
            if self.spatial_partitioning:
                self.spatial_partitioning.remove_object(obj)
                
            # Убираем скрипты объекта
            if self.script_engine and hasattr(obj, 'scripts'):
                for script in obj.scripts:
                    self.script_engine.unregister_script(script)
            
            if self.selected_object == obj:
                self.selected_object = None
                
            return True
        return False

    def clear(self):
        """Очистить сцену"""
        # Убираем все скрипты
        if self.script_engine:
            self.script_engine.clear()
        
        self.objects.clear()
        self.particle_systems.clear()
        self.animations = AnimationController()
        self.selected_object = None
        
        # Очищаем пространственное разбиение
        if self.spatial_partitioning:
            self.spatial_partitioning.clear()

    # Системы частиц
    def create_particle_system(self, position=(0, 0, 0)):
        """Создать систему частиц"""
        ps = ParticleSystem()
        ps.position = list(position)
        self.particle_systems.append(ps)
        return ps

    # Скриптинг
    def add_script_component(self, obj, script_type: str):
        """Добавить компонент скрипта к объекту"""
        if not self.script_engine:
            return False
            
        success = self.script_engine.add_script_to_object(obj, script_type)
        if success:
            print(f"Added {script_type} to {obj.name}")
            return True
        return False

    def load_script_from_file(self, obj, script_path: str):
        """Загрузить скрипт из файла"""
        if not self.script_engine:
            return False
            
        success = self.script_engine.load_script_from_file(obj, script_path)
        if success:
            print(f"Loaded script from {script_path} to {obj.name}")
            return True
        return False

    def get_script_components(self, obj):
        """Получить все компоненты скриптов объекта"""
        if hasattr(obj, 'scripts'):
            return obj.scripts
        return []

    # Оптимизация
    def optimize_scene(self):
        """Оптимизировать сцену"""
        if not self.spatial_partitioning:
            return
            
        # Рассчитываем границы сцены
        scene_bounds = self._calculate_scene_bounds()
        self.spatial_partitioning.initialize(scene_bounds)
        
        # Добавляем объекты в пространственное разбиение
        for obj in self.objects:
            bounds = self._calculate_object_bounds(obj)
            self.spatial_partitioning.add_object(obj, bounds)

    def _calculate_scene_bounds(self):
        """Рассчитать границы сцены"""
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
        """Рассчитать границы объекта"""
        size = 1.0
        if hasattr(obj, 'collider') and obj.collider:
            size = max(obj.collider.size) / 2
        else:
            size = max(obj.scale) / 2
            
        return [
            obj.position[0] - size, obj.position[1] - size, obj.position[2] - size,
            obj.position[0] + size, obj.position[1] + size, obj.position[2] + size
        ]

    # Сериализация
    def save_to_file(self, filename: str) -> bool:
        """Сохранить сцену в файл"""
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
                    'lights': [self._light_to_dict(light) for light in self.lighting.lights]
                },
                'metadata': {
                    'saved_date': datetime.now().isoformat(),
                    'version': '2.0',
                    'object_count': len(self.objects)
                }
            }
            
            # Сохраняем объекты
            for obj in self.objects:
                scene_data['objects'].append(self._object_to_dict(obj))
            
            with open(filename, 'w') as f:
                json.dump(scene_data, f, indent=2)
            
            print(f"Scene saved to {filename}")
            return True
            
        except Exception as e:
            print(f"Error saving scene: {e}")
            return False

    def load_from_file(self, filename: str) -> bool:
        """Загрузить сцену из файла"""
        try:
            with open(filename, 'r') as f:
                scene_data = json.load(f)
            
            self.clear()
            self.name = scene_data.get('name', 'Untitled')
            
            # Загружаем настройки
            if 'settings' in scene_data:
                settings = scene_data['settings']
                self.ambient_light = settings.get('ambient_light', [0.2, 0.2, 0.2, 1.0])
                self.gravity = settings.get('gravity', [0, -9.81, 0])
                self.fog_enabled = settings.get('fog_enabled', False)
                self.fog_color = settings.get('fog_color', [0.5, 0.5, 0.5, 1.0])
                self.fog_density = settings.get('fog_density', 0.01)
            
            # Загружаем объекты
            from .objects import GameObject
            for obj_data in scene_data['objects']:
                obj = self._object_from_dict(obj_data)
                self.add_object(obj)
            
            # Загружаем освещение
            if 'lighting' in scene_data:
                from .lighting import Light
                for light_data in scene_data['lighting']['lights']:
                    light = self._light_from_dict(light_data)
                    self.lighting.add_light(light)
            
            # Реоптимизируем сцену
            self.optimize_scene()
            self.setup_scripting()
            
            print(f"Scene loaded from {filename}")
            return True
            
        except Exception as e:
            print(f"Error loading scene: {e}")
            return False

    def _object_to_dict(self, obj):
        """Конвертировать объект в словарь"""
        obj_data = {
            'name': obj.name,
            'position': obj.position,
            'rotation': obj.rotation,
            'scale': obj.scale,
            'color': obj.color,
            'primitive_type': obj.primitive_type,
            'material_name': getattr(obj, 'material_name', 'Default'),
            'visible': getattr(obj, 'visible', True),
            'static': getattr(obj, 'static', False),
            'tag': getattr(obj, 'tag', 'Untagged'),
        }
        
        # Физические компоненты
        if hasattr(obj, 'collider') and obj.collider:
            obj_data['collider'] = {
                'type': getattr(obj.collider, 'type', 'BOX'),
                'size': getattr(obj.collider, 'size', [1, 1, 1]),
                'center': getattr(obj.collider, 'center', [0, 0, 0]),
                'is_trigger': getattr(obj.collider, 'is_trigger', False)
            }
        
        if hasattr(obj, 'rigidbody') and obj.rigidbody:
            obj_data['rigidbody'] = {
                'mass': getattr(obj.rigidbody, 'mass', 1.0),
                'drag': getattr(obj.rigidbody, 'drag', 0.1),
                'use_gravity': getattr(obj.rigidbody, 'use_gravity', True),
                'is_kinematic': getattr(obj.rigidbody, 'is_kinematic', False)
            }
        
        # Скрипты
        if hasattr(obj, 'scripts') and obj.scripts:
            obj_data['scripts'] = [
                {
                    'type': script.__class__.__name__,
                    'enabled': getattr(script, 'enabled', True)
                }
                for script in obj.scripts
            ]
        
        return obj_data

    def _object_from_dict(self, obj_data):
        """Создать объект из словаря"""
        from .objects import GameObject
        
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
        obj.tag = obj_data.get('tag', 'Untagged')
        
        # Физические компоненты
        if 'collider' in obj_data:
            collider_data = obj_data['collider']
            obj.add_collider(
                collider_data.get('type', 'BOX'),
                collider_data.get('size', [1, 1, 1]),
                collider_data.get('center', [0, 0, 0]),
                collider_data.get('is_trigger', False)
            )
        
        if 'rigidbody' in obj_data:
            rb_data = obj_data['rigidbody']
            obj.add_rigidbody(
                rb_data.get('mass', 1.0),
                rb_data.get('use_gravity', True),
                rb_data.get('is_kinematic', False),
                rb_data.get('drag', 0.1)
            )
        
        return obj

    def _light_to_dict(self, light):
        """Конвертировать свет в словарь"""
        return {
            'type': light.type,
            'position': light.position,
            'color': light.color,
            'intensity': light.intensity,
            'enabled': getattr(light, 'enabled', True),
            'range': getattr(light, 'range', 10.0),
            'spot_angle': getattr(light, 'spot_angle', 45.0)
        }

    def _light_from_dict(self, light_data):
        """Создать свет из словаря"""
        from .lighting import Light
        
        light = Light(
            light_data.get('type', 'DIRECTIONAL'),
            light_data.get('position', [0, 5, 0]),
            light_data.get('color', [1, 1, 1]),
            light_data.get('intensity', 1.0)
        )
        
        light.enabled = light_data.get('enabled', True)
        light.range = light_data.get('range', 10.0)
        light.spot_angle = light_data.get('spot_angle', 45.0)
        
        return light

    # Свойства для удобства
    @property
    def object_count(self) -> int:
        """Количество объектов в сцене"""
        return len(self.objects)
    
    @property
    def light_count(self) -> int:
        """Количество источников света"""
        return len(self.lighting.lights)
    
    @property
    def particle_system_count(self) -> int:
        """Количество систем частиц"""
        return len(self.particle_systems)

    def __str__(self) -> str:
        """Строковое представление сцены"""
        return (f"Scene '{self.name}' ({self.object_count} objects, "
                f"{self.light_count} lights, {self.particle_system_count} particle systems)")