from OpenGL.GL import *
import numpy as np

class Material:
    def __init__(self, name="DefaultMaterial"):
        self.name = name
        self.shader = None
        self.textures = {}
        
        # PBR свойства
        self.albedo = [1.0, 1.0, 1.0, 1.0]
        self.metallic = 0.0
        self.roughness = 0.5
        self.ao = 1.0
        self.emissive = [0.0, 0.0, 0.0]
        self.normal_scale = 1.0
        self.tiling = [1.0, 1.0]
        
        # Флаги
        self.use_albedo_map = False
        self.use_metallic_map = False
        self.use_roughness_map = False
        self.use_normal_map = False
        self.use_ao_map = False
        self.use_emissive_map = False
        
    def apply(self, shader=None):
        """Применить материал к шейдеру"""
        if shader is None:
            shader = self.shader
            
        if shader is None:
            return
            
        shader.use()
        
        # Устанавливаем свойства материала
        shader.set_uniform("material.albedo", self.albedo)
        shader.set_uniform("material.metallic", self.metallic)
        shader.set_uniform("material.roughness", self.roughness)
        shader.set_uniform("material.ao", self.ao)
        shader.set_uniform("material.emissive", self.emissive)
        shader.set_uniform("material.normal_scale", self.normal_scale)
        shader.set_uniform("material.tiling", self.tiling)
        
        # Флаги текстур
        shader.set_uniform("material.use_albedo_map", self.use_albedo_map)
        shader.set_uniform("material.use_metallic_map", self.use_metallic_map)
        shader.set_uniform("material.use_roughness_map", self.use_roughness_map)
        shader.set_uniform("material.use_normal_map", self.use_normal_map)
        shader.set_uniform("material.use_ao_map", self.use_ao_map)
        shader.set_uniform("material.use_emissive_map", self.use_emissive_map)
        
        # Активируем текстуры
        for unit, (texture_type, texture) in enumerate(self.textures.items()):
            if texture:
                texture.bind(unit)
                shader.set_uniform(f"material.{texture_type}", unit)

class MaterialLibrary:
    def __init__(self):
        self.materials = {}
        self.create_default_materials()
    
    def create_default_materials(self):
        # Default material
        default = Material("Default")
        default.albedo = [0.8, 0.8, 0.8, 1.0]
        
        # Metal material
        metal = Material("Metal")
        metal.albedo = [0.4, 0.4, 0.4, 1.0]
        metal.metallic = 0.9
        metal.roughness = 0.3
        
        # Plastic material
        plastic = Material("Plastic")
        plastic.albedo = [0.8, 0.8, 0.8, 1.0]
        plastic.metallic = 0.1
        plastic.roughness = 0.4
        
        # Rubber material
        rubber = Material("Rubber")
        rubber.albedo = [0.1, 0.1, 0.1, 1.0]
        rubber.metallic = 0.0
        rubber.roughness = 0.9
        
        self.materials = {
            "Default": default,
            "Metal": metal,
            "Plastic": plastic,
            "Rubber": rubber
        }
    
    def get_material(self, name):
        return self.materials.get(name, self.materials["Default"])
    
    def add_material(self, name, material):
        self.materials[name] = material
    
    def remove_material(self, name):
        if name in self.materials and name != "Default":
            del self.materials[name]