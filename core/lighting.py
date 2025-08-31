from OpenGL.GL import *
import numpy as np

class Light:
    def __init__(self, light_type="DIRECTIONAL", position=(0, 5, 0), color=(1, 1, 1), intensity=1.0):
        self.type = light_type  # DIRECTIONAL, POINT, SPOT
        self.position = list(position)
        self.color = list(color)
        self.intensity = intensity
        self.enabled = True
        self.range = 10.0
        self.spot_angle = 45.0
        
    def apply(self, light_id):
        if not self.enabled:
            return
            
        glEnable(light_id)
        
        if self.type == "DIRECTIONAL":
            glLightfv(light_id, GL_POSITION, [self.position[0], self.position[1], self.position[2], 0.0])
        else:
            glLightfv(light_id, GL_POSITION, [self.position[0], self.position[1], self.position[2], 1.0])
            glLightf(light_id, GL_CONSTANT_ATTENUATION, 1.0)
            glLightf(light_id, GL_LINEAR_ATTENUATION, 0.1)
            glLightf(light_id, GL_QUADRATIC_ATTENUATION, 0.01)
        
        glLightfv(light_id, GL_DIFFUSE, [self.color[0] * self.intensity, 
                                        self.color[1] * self.intensity, 
                                        self.color[2] * self.intensity, 1.0])
        glLightfv(light_id, GL_SPECULAR, [self.color[0] * self.intensity, 
                                         self.color[1] * self.intensity, 
                                         self.color[2] * self.intensity, 1.0])
        
        if self.type == "SPOT":
            glLightf(light_id, GL_SPOT_CUTOFF, self.spot_angle)
            glLightfv(light_id, GL_SPOT_DIRECTION, [0, -1, 0])

class LightingSystem:
    def __init__(self):
        self.lights = []
        self.ambient_color = [0.2, 0.2, 0.2, 1.0]
        self.max_lights = 8
        
    def add_light(self, light):
        if len(self.lights) < self.max_lights:
            self.lights.append(light)
            return True
        return False
    
    def apply_lights(self):
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, self.ambient_color)
        
        for i, light in enumerate(self.lights):
            if i < self.max_lights:
                light.apply(GL_LIGHT0 + i)
            else:
                break