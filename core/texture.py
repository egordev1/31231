from OpenGL.GL import *
from PIL import Image
import numpy as np

class Texture:
    def __init__(self, path=None, texture_type="DIFFUSE"):
        self.texture_id = glGenTextures(1)
        self.width = 0
        self.height = 0
        self.path = path
        self.type = texture_type  # DIFFUSE, SPECULAR, NORMAL, HEIGHT
        
        if path:
            self.load_texture(path)
    
    def load_texture(self, path):
        try:
            image = Image.open(path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            img_data = np.array(image, np.uint8)
            
            self.width = image.width
            self.height = image.height
            
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width, self.height, 0,
                        GL_RGB, GL_UNSIGNED_BYTE, img_data)
            
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            
            glGenerateMipmap(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, 0)
            
        except Exception as e:
            print(f"Error loading texture {path}: {e}")
    
    def bind(self, unit=0):
        glActiveTexture(GL_TEXTURE0 + unit)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
    
    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)

class TextureManager:
    def __init__(self):
        self.textures = {}
        self.texture_units = {}
        
    def load_texture(self, path, texture_type="DIFFUSE"):
        if path in self.textures:
            return self.textures[path]
        
        texture = Texture(path, texture_type)
        self.textures[path] = texture
        return texture
    
    def get_texture(self, path):
        return self.textures.get(path)
    
    def bind_texture(self, path, unit=0):
        if path in self.textures:
            self.textures[path].bind(unit)
            return True
        return False