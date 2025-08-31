import numpy as np

class PhysicsEngine:
    def __init__(self):
        self.gravity = [0.0, -9.81, 0.0]
        self.collisions = []
    
    def update(self, dt, objects):
        self.collisions.clear()
        
        for obj in objects:
            if hasattr(obj, 'has_rigidbody') and obj.has_rigidbody and not obj.rigidbody_is_kinematic:
                self._apply_physics(obj, dt)
        
        self._check_collisions(objects)
    
    def _apply_physics(self, obj, dt):
        if not hasattr(obj, 'velocity'):
            obj.velocity = [0.0, 0.0, 0.0]
        if not hasattr(obj, 'angular_velocity'):
            obj.angular_velocity = [0.0, 0.0, 0.0]
        
        if obj.rigidbody_use_gravity:
            for i in range(3):
                obj.velocity[i] += self.gravity[i] * dt * obj.rigidbody_mass
        
        for i in range(3):
            obj.velocity[i] *= (1.0 - obj.rigidbody_drag * dt)
            obj.angular_velocity[i] *= (1.0 - obj.rigidbody_angular_drag * dt)
        
        for i in range(3):
            obj.position[i] += obj.velocity[i] * dt
            obj.rotation[i] += obj.angular_velocity[i] * dt
    
    def _check_collisions(self, objects):
        for i in range(len(objects)):
            obj1 = objects[i]
            if not hasattr(obj1, 'collider_type') or not obj1.collider_type:
                continue
                
            for j in range(i + 1, len(objects)):
                obj2 = objects[j]
                if not hasattr(obj2, 'collider_type') or not obj2.collider_type:
                    continue
                
                if self._check_collision(obj1, obj2):
                    self.collisions.append((obj1, obj2))
    
    def _check_collision(self, obj1, obj2):
        if obj1.collider_type == "BOX" and obj2.collider_type == "BOX":
            return self._check_aabb_collision(obj1, obj2)
        return False
    
    def _check_aabb_collision(self, obj1, obj2):
        min1 = [
            obj1.position[0] - obj1.collider_size[0] / 2 + obj1.collider_center[0],
            obj1.position[1] - obj1.collider_size[1] / 2 + obj1.collider_center[1],
            obj1.position[2] - obj1.collider_size[2] / 2 + obj1.collider_center[2]
        ]
        max1 = [
            obj1.position[0] + obj1.collider_size[0] / 2 + obj1.collider_center[0],
            obj1.position[1] + obj1.collider_size[1] / 2 + obj1.collider_center[1],
            obj1.position[2] + obj1.collider_size[2] / 2 + obj1.collider_center[2]
        ]
        
        min2 = [
            obj2.position[0] - obj2.collider_size[0] / 2 + obj2.collider_center[0],
            obj2.position[1] - obj2.collider_size[1] / 2 + obj2.collider_center[1],
            obj2.position[2] - obj2.collider_size[2] / 2 + obj2.collider_center[2]
        ]
        max2 = [
            obj2.position[0] + obj2.collider_size[0] / 2 + obj2.collider_center[0],
            obj2.position[1] + obj2.collider_size[1] / 2 + obj2.collider_center[1],
            obj2.position[2] + obj2.collider_size[2] / 2 + obj2.collider_center[2]
        ]
        
        return (min1[0] <= max2[0] and max1[0] >= min2[0] and
                min1[1] <= max2[1] and max1[1] >= min2[1] and
                min1[2] <= max2[2] and max1[2] >= min2[2])
    
    def add_force(self, obj, force, force_mode="FORCE"):
        if hasattr(obj, 'has_rigidbody') and obj.has_rigidbody:
            if force_mode == "FORCE":
                acceleration = [f / obj.rigidbody_mass for f in force]
                for i in range(3):
                    obj.velocity[i] += acceleration[i]
            elif force_mode == "IMPULSE":
                for i in range(3):
                    obj.velocity[i] += force[i]
    
    def add_torque(self, obj, torque, force_mode="FORCE"):
        if hasattr(obj, 'has_rigidbody') and obj.has_rigidbody:
            if force_mode == "FORCE":
                angular_acceleration = [t / obj.rigidbody_mass for t in torque]
                for i in range(3):
                    obj.angular_velocity[i] += angular_acceleration[i]
            elif force_mode == "IMPULSE":
                for i in range(3):
                    obj.angular_velocity[i] += torque[i]
    
    def raycast(self, origin, direction, max_distance=1000.0, objects=None):
        if objects is None:
            return None, max_distance
        
        closest_hit = None
        closest_distance = max_distance
        
        for obj in objects:
            if hasattr(obj, 'collider_type') and obj.collider_type:
                hit, distance = self.ray_aabb_intersection(origin, direction, obj)
                if hit and distance < closest_distance:
                    closest_hit = obj
                    closest_distance = distance
        
        return closest_hit, closest_distance
    
    def ray_aabb_intersection(self, origin, direction, obj):
        if not hasattr(obj, 'collider_type') or obj.collider_type != "BOX":
            return False, float('inf')
        
        origin = np.array(origin)
        direction = np.array(direction)
        
        min_bound = np.array([
            obj.position[0] - obj.collider_size[0] / 2 + obj.collider_center[0],
            obj.position[1] - obj.collider_size[1] / 2 + obj.collider_center[1],
            obj.position[2] - obj.collider_size[2] / 2 + obj.collider_center[2]
        ])
        max_bound = np.array([
            obj.position[0] + obj.collider_size[0] / 2 + obj.collider_center[0],
            obj.position[1] + obj.collider_size[1] / 2 + obj.collider_center[1],
            obj.position[2] + obj.collider_size[2] / 2 + obj.collider_center[2]
        ])
        
        tmin = 0.0
        tmax = float('inf')
        
        for i in range(3):
            if abs(direction[i]) < 1e-6:
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