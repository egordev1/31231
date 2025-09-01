from .scripting import MonoBehaviour

class Rigidbody(MonoBehaviour):
    """Компонент физического тела"""
    
    def Awake(self):
        self.velocity = Vector3()
        self.angularVelocity = Vector3()
        self.mass = 1.0
        self.useGravity = True
        self.isKinematic = False
        self.drag = 0.1
        self.angularDrag = 0.05
    
    def AddForce(self, force: Vector3, force_mode: str = "Force"):
        """Добавить силу"""
        if force_mode == "Force":
            self.velocity += force / self.mass
        elif force_mode == "Impulse":
            self.velocity += force
    
    def AddTorque(self, torque: Vector3, force_mode: str = "Force"):
        """Добавить крутящий момент"""
        if force_mode == "Force":
            self.angularVelocity += torque / self.mass
        elif force_mode == "Impulse":
            self.angularVelocity += torque

class Collider(MonoBehaviour):
    """Компонент коллайдера"""
    
    def Awake(self):
        self.isTrigger = False
        self.bounds = None
        self.contactOffset = 0.01

class Camera(MonoBehaviour):
    """Компонент камеры"""
    
    def Awake(self):
        self.fieldOfView = 60.0
        self.nearClipPlane = 0.1
        self.farClipPlane = 1000.0
        self.backgroundColor = Color(0.2, 0.2, 0.2, 1.0)

class Light(MonoBehaviour):
    """Компонент источника света"""
    
    def Awake(self):
        self.type = "Point"  # Point, Directional, Spot
        self.color = Color(1.0, 1.0, 1.0, 1.0)
        self.intensity = 1.0
        self.range = 10.0
        self.spotAngle = 30.0

class Color:
    """Аналог UnityEngine.Color"""
    
    def __init__(self, r: float = 0.0, g: float = 0.0, b: float = 0.0, a: float = 1.0):
        self.r = r
        self.g = g
        self.b = b
        self.a = a