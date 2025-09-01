from OpenGL.GL import *
import numpy as np

class PostProcessingEffect:
    def __init__(self):
        self.enabled = True
        self.intensity = 1.0
        
    def apply(self, framebuffer):
        pass

class BloomEffect(PostProcessingEffect):
    def __init__(self):
        super().__init__()
        self.threshold = 0.8
        self.blur_strength = 5.0
        
    def apply(self, framebuffer):
        if not self.enabled:
            return
            
        # Simple bloom implementation
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        
        # Draw bright parts
        glColor4f(1, 1, 1, self.intensity * 0.1)
        glBegin(GL_QUADS)
        glVertex2f(-1, -1)
        glVertex2f(1, -1)
        glVertex2f(1, 1)
        glVertex2f(-1, 1)
        glEnd()
        
        glDisable(GL_BLEND)

class ColorGradingEffect(PostProcessingEffect):
    def __init__(self):
        super().__init__()
        self.brightness = 1.0
        self.contrast = 1.0
        self.saturation = 1.0
        
    def apply(self, framebuffer):
        if not self.enabled:
            return
            
        # Color grading implementation
        glColor4f(self.brightness, self.contrast, self.saturation, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(-1, -1)
        glVertex2f(1, -1)
        glVertex2f(1, 1)
        glVertex2f(-1, 1)
        glEnd()

class PostProcessingStack:
    def __init__(self):
        self.effects = []
        self.framebuffer = None
        
    def add_effect(self, effect):
        self.effects.append(effect)
        
    def remove_effect(self, index):
        if 0 <= index < len(self.effects):
            return self.effects.pop(index)
        return None
        
    def apply_effects(self):
        if not self.framebuffer:
            self._create_framebuffer()
            
        # Render to framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebuffer)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Apply effects
        for effect in self.effects:
            if effect.enabled:
                effect.apply(self.framebuffer)
                
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        
    def _create_framebuffer(self):
        self.framebuffer = glGenFramebuffers(1)
        # ... implementation for creating FBO