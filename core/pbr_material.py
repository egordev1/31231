from OpenGL.GL import *

class PBRMaterial:
    def __init__(self, name="PBR_Material"):
        self.name = name
        self.albedo = [0.8, 0.8, 0.8, 1.0]
        self.metallic = 0.0
        self.roughness = 0.5
        self.ao = 1.0
        self.emissive = [0.0, 0.0, 0.0]
        self.normal_scale = 1.0
        
        self.albedo_map = None
        self.metallic_map = None
        self.roughness_map = None
        self.normal_map = None
        self.ao_map = None
        self.emissive_map = None
        
    def apply(self):
        # Set material properties
        glMaterialfv(GL_FRONT, GL_DIFFUSE, self.albedo)
        glMaterialfv(GL_FRONT, GL_SPECULAR, [self.metallic, self.metallic, self.metallic, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, (1.0 - self.roughness) * 128.0)
        
        # Bind textures if available
        if self.albedo_map:
            self.albedo_map.bind(0)
        if self.normal_map:
            self.normal_map.bind(1)
        if self.metallic_map:
            self.metallic_map.bind(2)
        if self.roughness_map:
            self.roughness_map.bind(3)