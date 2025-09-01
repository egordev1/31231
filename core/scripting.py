import os
import sys
import importlib.util
import inspect
import time
from typing import Dict, List, Optional, Any, Callable, Type
from enum import Enum

class ExecutionOrder(Enum):
    """Порядок выполнения скриптов, как в Unity"""
    AWAKE = -1000
    ON_ENABLE = -900
    START = -800
    FIXED_UPDATE = -500
    UPDATE = 0
    LATE_UPDATE = 500
    ON_DISABLE = 900
    ON_DESTROY = 1000

class MonoBehaviour:
    """Базовый класс для всех скриптов, аналог MonoBehaviour из Unity"""
    
    def __init__(self):
        self.gameObject = None
        self.transform = None
        self.enabled = True
        self._started = False
        self._execution_order = 0
        
        # Автоматически определяем порядок выполнения
        self._determine_execution_order()
    
    def _determine_execution_order(self):
        """Определяем порядок выполнения на основе методов"""
        if hasattr(self, 'Awake'):
            self._execution_order = ExecutionOrder.AWAKE.value
        elif hasattr(self, 'OnEnable'):
            self._execution_order = ExecutionOrder.ON_ENABLE.value
        elif hasattr(self, 'Start'):
            self._execution_order = ExecutionOrder.START.value
        elif hasattr(self, 'FixedUpdate'):
            self._execution_order = ExecutionOrder.FIXED_UPDATE.value
        elif hasattr(self, 'Update'):
            self._execution_order = ExecutionOrder.UPDATE.value
        elif hasattr(self, 'LateUpdate'):
            self._execution_order = ExecutionOrder.LATE_UPDATE.value
    
    def _set_game_object(self, game_object):
        """Установить ссылку на игровой объект (вызывается системой)"""
        self.gameObject = game_object
        if hasattr(game_object, 'position'):
            self.transform = game_object
    
    # ========== СТАНДАРТНЫЕ МЕТОДЫ UNITY ==========
    
    def Awake(self):
        """Вызывается при создании скрипта"""
        pass
    
    def OnEnable(self):
        """Вызывается при включении скрипта"""
        pass
    
    def Start(self):
        """Вызывается перед первым Update"""
        pass
    
    def FixedUpdate(self):
        """Вызывается с фиксированным интервалом для физики"""
        pass
    
    def Update(self):
        """Вызывается каждый кадр"""
        pass
    
    def LateUpdate(self):
        """Вызывается после всех Update"""
        pass
    
    def OnDisable(self):
        """Вызывается при выключении скрипта"""
        pass
    
    def OnDestroy(self):
        """Вызывается при уничтожении скрипта"""
        pass
    
    # ========== СОБЫТИЯ ФИЗИКИ ==========
    
    def OnCollisionEnter(self, collision):
        """При начале столкновения"""
        pass
    
    def OnCollisionExit(self, collision):
        """При окончании столкновения"""
        pass
    
    def OnCollisionStay(self, collision):
        """Пока объекты соприкасаются"""
        pass
    
    def OnTriggerEnter(self, other):
        """При входе в триггер"""
        pass
    
    def OnTriggerExit(self, other):
        """При выходе из триггера"""
        pass
    
    def OnTriggerStay(self, other):
        """Пока объект в триггере"""
        pass
    
    # ========== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ==========
    
    def GetComponent(self, component_type: Type) -> Any:
        """Получить компонент указанного типа"""
        if not self.gameObject:
            return None
        
        # Проверяем атрибуты GameObject
        if hasattr(self.gameObject, component_type.__name__.lower()):
            return getattr(self.gameObject, component_type.__name__.lower())
        
        # Ищем в scripts
        if hasattr(self.gameObject, 'scripts'):
            for script in self.gameObject.scripts:
                if isinstance(script, component_type):
                    return script
        
        return None
    
    def GetComponents(self, component_type: Type) -> List[Any]:
        """Получить все компоненты указанного типа"""
        components = []
        if not self.gameObject:
            return components
        
        # Проверяем атрибуты GameObject
        if hasattr(self.gameObject, component_type.__name__.lower()):
            comp = getattr(self.gameObject, component_type.__name__.lower())
            if comp:
                components.append(comp)
        
        # Ищем в scripts
        if hasattr(self.gameObject, 'scripts'):
            for script in self.gameObject.scripts:
                if isinstance(script, component_type):
                    components.append(script)
        
        return components
    
    def AddComponent(self, component_type: Type) -> Any:
        """Добавить компонент указанного типа"""
        if not self.gameObject:
            return None
        
        # Создаем экземпляр компонента
        component = component_type()
        
        # Добавляем к GameObject
        if not hasattr(self.gameObject, 'scripts'):
            self.gameObject.scripts = []
        
        self.gameObject.scripts.append(component)
        component._set_game_object(self.gameObject)
        
        return component
    
    def Instantiate(self, original, position=None, rotation=None):
        """Создать копию объекта"""
        # Заглушка - в реальной реализации нужно клонировать объект
        print(f"Instantiating {original.name}")
        return original
    
    def Destroy(self, obj, delay: float = 0.0):
        """Уничтожить объект"""
        # Заглушка - в реальной реализации нужно удалять объект
        print(f"Destroying {obj.name} with delay {delay}")
    
    def FindObjectOfType(self, component_type: Type) -> Any:
        """Найти объект с компонентом указанного типа"""
        if not self.gameObject or not hasattr(self.gameObject, '_scene'):
            return None
        
        scene = self.gameObject._scene
        for obj in scene.objects:
            if hasattr(obj, 'scripts'):
                for script in obj.scripts:
                    if isinstance(script, component_type):
                        return script
        
        return None
    
    def FindObjectsOfType(self, component_type: Type) -> List[Any]:
        """Найти все объекты с компонентом указанного типа"""
        objects = []
        if not self.gameObject or not hasattr(self.gameObject, '_scene'):
            return objects
        
        scene = self.gameObject._scene
        for obj in scene.objects:
            if hasattr(obj, 'scripts'):
                for script in obj.scripts:
                    if isinstance(script, component_type):
                        objects.append(script)
        
        return objects

class ScriptEngine:
    """Движок выполнения скриптов, аналог Unity Scripting Engine"""
    
    def __init__(self):
        self.scripts: List[MonoBehaviour] = []
        self.fixed_time_step = 0.02  # 50 FPS для FixedUpdate
        self._fixed_time_accumulator = 0.0
        self._execution_groups: Dict[int, List[MonoBehaviour]] = {}
        
        # Глобальные переменные, аналог Unity API
        self.globals = {
            'Time': Time(),
            'Input': Input(),
            'Debug': Debug(),
            'Mathf': Mathf(),
            'Vector3': Vector3,
            'Quaternion': Quaternion,
        }
    
    def register_script(self, script: MonoBehaviour):
        """Зарегистрировать скрипт для выполнения"""
        self.scripts.append(script)
        
        # Группируем по порядку выполнения
        if script._execution_order not in self._execution_groups:
            self._execution_groups[script._execution_order] = []
        self._execution_groups[script._execution_order].append(script)
    
    def unregister_script(self, script: MonoBehaviour):
        """Убрать скрипт из выполнения"""
        if script in self.scripts:
            self.scripts.remove(script)
            if script._execution_order in self._execution_groups:
                self._execution_groups[script._execution_order].remove(script)
    
    def execute_method(self, method_name: str, delta_time: float = 0.0):
        """Выполнить метод у всех скриптов в правильном порядке"""
        for order in sorted(self._execution_groups.keys()):
            for script in self._execution_groups[order]:
                if script.enabled and hasattr(script, method_name):
                    try:
                        method = getattr(script, method_name)
                        if delta_time > 0:
                            method(delta_time)
                        else:
                            method()
                    except Exception as e:
                        print(f"Error in {script.__class__.__name__}.{method_name}: {e}")
                        import traceback
                        traceback.print_exc()
    
    def update(self, delta_time: float):
        """Обновить все скрипты"""
        # FixedUpdate с фиксированным шагом
        self._fixed_time_accumulator += delta_time
        while self._fixed_time_accumulator >= self.fixed_time_step:
            self.execute_method('FixedUpdate', self.fixed_time_step)
            self._fixed_time_accumulator -= self.fixed_time_step
        
        # Стандартное обновление
        self.execute_method('Update', delta_time)
        self.execute_method('LateUpdate', delta_time)
    
    def start_all(self):
        """Запустить все скрипты"""
        # Awake и OnEnable
        self.execute_method('Awake')
        self.execute_method('OnEnable')
        
        # Start (только один раз)
        for script in self.scripts:
            if script.enabled and hasattr(script, 'Start') and not script._started:
                try:
                    script.Start()
                    script._started = True
                except Exception as e:
                    print(f"Error in {script.__class__.__name__}.Start: {e}")
    
    def load_script_from_file(self, file_path: str) -> Type[MonoBehaviour]:
        """Загрузить скрипт из файла"""
        try:
            # Создаем уникальное имя модуля
            module_name = f"script_{os.path.basename(file_path).replace('.', '_')}"
            
            # Загружаем исходный код
            with open(file_path, 'r', encoding='utf-8') as f:
                script_code = f.read()
            
            # Добавляем импорты для Unity-like API
            script_code = f"""
from core.scripting import MonoBehaviour, Time, Input, Debug, Mathf, Vector3
import math

{script_code}
"""
            # Создаем модуль
            spec = importlib.util.spec_from_loader(module_name, loader=None)
            module = importlib.util.module_from_spec(spec)
            
            # Добавляем глобальные переменные
            module.__dict__.update(self.globals)
            
            # Выполняем код
            exec(script_code, module.__dict__)
            
            # Ищем классы, наследующиеся от MonoBehaviour
            script_classes = []
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, MonoBehaviour) and 
                    obj != MonoBehaviour):
                    script_classes.append(obj)
            
            if script_classes:
                return script_classes[0]  # Возвращаем первый найденный класс
            
            return None
            
        except Exception as e:
            print(f"Error loading script from {file_path}: {e}")
            import traceback
            traceback.print_exc()
            return None

# ========== UNITY-LIKE API CLASSES ==========

class Time:
    """Аналог UnityEngine.Time"""
    
    def __init__(self):
        self.time = 0.0
        self.deltaTime = 0.0
        self.fixedTime = 0.0
        self.fixedDeltaTime = 0.02
        self.timeScale = 1.0
        self.frameCount = 0
        self.realtimeSinceStartup = time.time()
        self.unscaledTime = 0.0
        self.unscaledDeltaTime = 0.0
    
    def update(self, delta_time: float):
        """Обновить время"""
        self.deltaTime = delta_time * self.timeScale
        self.time += self.deltaTime
        self.unscaledDeltaTime = delta_time
        self.unscaledTime += delta_time
        self.frameCount += 1

class Input:
    """Аналог UnityEngine.Input"""
    
    @staticmethod
    def GetKey(key: str) -> bool:
        """Проверить нажатие клавиши"""
        # Заглушка - в реальной реализации нужно интегрировать с системой ввода
        return False
    
    @staticmethod
    def GetKeyDown(key: str) -> bool:
        """Проверить момент нажатия клавиши"""
        return False
    
    @staticmethod
    def GetKeyUp(key: str) -> bool:
        """Проверить момент отпускания клавиши"""
        return False
    
    @staticmethod
    def GetMouseButton(button: int) -> bool:
        """Проверить нажатие кнопки мыши"""
        return False
    
    @staticmethod
    def GetMouseButtonDown(button: int) -> bool:
        """Проверить момент нажатия кнопки мыши"""
        return False
    
    @staticmethod
    def GetMouseButtonUp(button: int) -> bool:
        """Проверить момент отпускания кнопки мыши"""
        return False
    
    @staticmethod
    def GetAxis(axis_name: str) -> float:
        """Получить значение оси ввода"""
        return 0.0

class Debug:
    """Аналог UnityEngine.Debug"""
    
    @staticmethod
    def Log(message: str):
        print(f"[LOG] {message}")
    
    @staticmethod
    def LogWarning(message: str):
        print(f"[WARNING] {message}")
    
    @staticmethod
    def LogError(message: str):
        print(f"[ERROR] {message}")

class Mathf:
    """Аналог UnityEngine.Mathf"""
    
    @staticmethod
    def Clamp(value: float, min_val: float, max_val: float) -> float:
        return max(min_val, min(value, max_val))
    
    @staticmethod
    def Lerp(a: float, b: float, t: float) -> float:
        return a + (b - a) * Mathf.Clamp(t, 0, 1)
    
    @staticmethod
    def LerpUnclamped(a: float, b: float, t: float) -> float:
        return a + (b - a) * t
    
    @staticmethod
    def MoveTowards(current: float, target: float, max_delta: float) -> float:
        if abs(target - current) <= max_delta:
            return target
        return current + math.copysign(max_delta, target - current)
    
    @staticmethod
    def SmoothDamp(current: float, target: float, current_velocity: float, 
                  smooth_time: float, max_speed: float = float('inf'), 
                  delta_time: float = 0.02) -> float:
        # Упрощенная реализация
        smooth_time = max(0.0001, smooth_time)
        omega = 2.0 / smooth_time
        
        x = omega * delta_time
        exp = 1.0 / (1.0 + x + 0.48 * x * x + 0.235 * x * x * x)
        
        change = current - target
        original_to = target
        
        max_change = max_speed * smooth_time
        change = Mathf.Clamp(change, -max_change, max_change)
        target = current - change
        
        temp = (current_velocity + omega * change) * delta_time
        current_velocity = (current_velocity - omega * temp) * exp
        output = target + (change + temp) * exp
        
        if (original_to - current > 0.0) == (output > original_to):
            output = original_to
            current_velocity = (output - original_to) / delta_time
        
        return output

class Vector3:
    """Аналог UnityEngine.Vector3"""
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __truediv__(self, scalar):
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def normalized(self):
        mag = self.magnitude()
        if mag > 0:
            return self / mag
        return Vector3()
    
    def dot(self, other) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    @staticmethod
    def distance(a, b) -> float:
        return (a - b).magnitude()
    
    @staticmethod
    def lerp(a, b, t: float):
        t = Mathf.Clamp(t, 0, 1)
        return Vector3(
            a.x + (b.x - a.x) * t,
            a.y + (b.y - a.y) * t,
            a.z + (b.z - a.z) * t
        )
    
    @staticmethod
    def move_towards(current, target, max_distance_delta: float):
        to_vector = target - current
        distance = to_vector.magnitude()
        
        if distance <= max_distance_delta or distance == 0:
            return target
        
        return current + to_vector / distance * max_distance_delta
    
    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

class Quaternion:
    """Аналог UnityEngine.Quaternion"""
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 1.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w
    
    @staticmethod
    def euler(x: float, y: float, z: float):
        """Создать из углов Эйлера"""
        # Упрощенная реализация
        return Quaternion()
    
    @staticmethod
    def angle_axis(angle: float, axis: Vector3):
        """Создать из угла и оси"""
        # Упрощенная реализация
        return Quaternion()
    
    def __mul__(self, other):
        """Умножение кватернионов"""
        # Упрощенная реализация
        return Quaternion()
    
    def euler_angles(self):
        """Получить углы Эйлера"""
        # Упрощенная реализация
        return Vector3()

# Глобальные инстансы
_time = Time()
_input = Input()
_debug = Debug()
_mathf = Mathf()

# Глобальные переменные для скриптов
Time = _time
Input = _input
Debug = _debug
Mathf = _mathf