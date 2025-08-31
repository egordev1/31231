from OpenGL.GL import *
import numpy as np
from .texture import Texture

class Skybox:
    def __init__(self, size=100.0):
        self.size = size
        self.texture = None
        self.color = [0.53, 0.81, 0.98, 1.0]
        
    def load_cubemap(self, texture_paths):
        # texture_paths should be list of 6 paths: [right, left, top, bottom, front, back]
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)
        
        for i in range(6):
            try:
                image = Image.open(texture_paths[i])
                image = image.transpose(Image.FLIP_TOP_BOTTOM)
                img_data = np.array(list(image.getdata()), np.uint8)
                
                glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB,
                            image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
            except Exception as e:
                print(f"Error loading cubemap texture {texture_paths[i]}: {e}")
        
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
    
    def draw(self):
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glDepthMask(GL_FALSE)
        
        if self.texture:
            glEnable(GL_TEXTURE_CUBE_MAP)
            glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)
            glColor4f(1, 1, 1, 1)
        else:
            glColor4f(*self.color)
        
        # Draw skybox cube
        glBegin(GL_QUADS)
        
        # Front
        glTexCoord3f(0, 0, -1); glVertex3f(-self.size, -self.size, -self.size)
        glTexCoord3f(1, 0, -1); glVertex3f(self.size, -self.size, -self.size)
        glTexCoord3f(1, 1, -1); glVertex3f(self.size, self.size, -self.size)
        glTexCoord3f(0, 1, -1); glVertex3f(-self.size, self.size, -self.size)
        
        # Back
        glTexCoord3f(0, 0, 1); glVertex3f(-self.size, -self.size, self.size)
        glTexCoord3f(0, 1, 1); glVertex3f(-self.size, self.size, self.size)
        glTexCoord3f(1, 1, 1); glVertex3f(self.size, self.size, self.size)
        glTexCoord3f(1, 0, 1); glVertex3f(self.size, -self.size, self.size)
        
        # Left
        glTexCoord3f(-1, 0, 0); glVertex3f(-self.size, -self.size, -self.size)
        glTexCoord3f(-1, 1, 0); glVertex3f(-self.size, self.size, -self.size)
        glTexCoord3f(-1, 1, 1); glVertex3f(-self.size, self.size, self.size)
        glTexCoord3f(-1, 0, 1); glVertex3f(-self.size, -self.size, self.size)
        
        # Right
        glTexCoord3f(1, 0, 0); glVertex3f(self.size, -self.size, -self.size)
        glTexCoord3f(1, 0, 1); glVertex3f(self.size, -self.size, self.size)
        glTexCoord3f(1, 1, 1); glVertex3f(self.size, self.size, self.size)
        glTexCoord3f(1, 1, 0); glVertex3f(self.size, self.size, -self.size)
        
        # Top
        glTexCoord3f(0, 1, 0); glVertex3f(-self.size, self.size, -self.size)
        glTexCoord3f(0, 1, 1); glVertex3f(-self.size, self.size, self.size)
        glTexCoord3f(1, 1, 1); glVertex3f(self.size, self.size, self.size)
        glTexCoord3f(1, 1, 0); glVertex3f(self.size, self.size, -self.size)
        
        # Bottom
        glTexCoord3f(0, -1, 0); glVertex3f(-self.size, -self.size, -self.size)
        glTexCoord3f(1, -1, 0); glVertex3f(self.size, -self.size, -self.size)
        glTexCoord3f(1, -1, 1); glVertex3f(self.size, -self.size, self.size)
        glTexCoord3f(0, -1, 1); glVertex3f(-self.size, -self.size, self.size)
        
        glEnd()
        
        if self.texture:
            glDisable(GL_TEXTURE_CUBE_MAP)
        
        glDepthMask(GL_TRUE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)