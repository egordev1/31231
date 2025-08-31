from OpenGL.GL import *

class Material:
    def __init__(self, name="DefaultMaterial"):
        self.name = name
        self.diffuse_color = [1.0, 1.0, 1.0, 1.0]
        self.specular_color = [1.0, 1.0, 1.0, 1.0]
        self.shininess = 32.0
        
    def apply(self):
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, self.diffuse_color)
        glMaterialfv(GL_FRONT, GL_SPECULAR, self.specular_color)
        glMaterialfv(GL_FRONT, GL_SHININESS, [self.shininess])

class MaterialLibrary:
    def __init__(self):
        self.materials = {}
        self.create_default_materials()
    
    def create_default_materials(self):
        # Default materials
        default = Material("Default")
        default.diffuse_color = [0.8, 0.8, 0.8, 1.0]
        
        metal = Material("Metal")
        metal.diffuse_color = [0.4, 0.4, 0.4, 1.0]
        metal.specular_color = [0.774597, 0.774597, 0.774597, 1.0]
        metal.shininess = 76.8
        
        plastic = Material("Plastic")
        plastic.diffuse_color = [0.55, 0.55, 0.55, 1.0]
        plastic.specular_color = [0.70, 0.70, 0.70, 1.0]
        plastic.shininess = 32.0
        
        rubber = Material("Rubber")
        rubber.diffuse_color = [0.01, 0.01, 0.01, 1.0]
        rubber.specular_color = [0.4, 0.4, 0.4, 1.0]
        rubber.shininess = 10.0
        
        self.materials = {
            "Default": default,
            "Metal": metal,
            "Plastic": plastic,
            "Rubber": rubber
        }
    
    def get_material(self, name):
        return self.materials.get(name, self.materials["Default"])