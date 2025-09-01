# core/renderer.py
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import ctypes

class Shader:
    def __init__(self, vertex_source, fragment_source):
        try:
            self.program = compileProgram(
                compileShader(vertex_source, GL_VERTEX_SHADER),
                compileShader(fragment_source, GL_FRAGMENT_SHADER)
            )
            self.valid = True
            print("✓ Shader compiled successfully")
        except Exception as e:
            print(f"✗ Shader compilation failed: {e}")
            self.valid = False
            self.program = 0
    
    def use(self):
        if self.valid:
            glUseProgram(self.program)
    
    def set_uniform(self, name, value):
        if not self.valid:
            return
            
        location = glGetUniformLocation(self.program, name)
        if location == -1:
            return
            
        if isinstance(value, (int, bool)):
            glUniform1i(location, value)
        elif isinstance(value, float):
            glUniform1f(location, value)
        elif isinstance(value, (list, tuple, np.ndarray)):
            if len(value) == 2:
                glUniform2f(location, *value)
            elif len(value) == 3:
                glUniform3f(location, *value)
            elif len(value) == 4:
                glUniform4f(location, *value)
            elif len(value) == 9:
                glUniformMatrix3fv(location, 1, GL_FALSE, np.array(value, dtype=np.float32))
            elif len(value) == 16:
                glUniformMatrix4fv(location, 1, GL_FALSE, np.array(value, dtype=np.float32))

class Mesh:
    def __init__(self, vertices, indices=None):
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = None
        self.vertex_count = len(vertices) // 8  # 8 floats per vertex
        
        glBindVertexArray(self.vao)
        
        # Вершинный буфер
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        
        # Атрибуты вершин
        # position (location = 0)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(0))
        # normal (location = 1)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(3 * 4))
        # texcoord (location = 2)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(6 * 4))
        
        glBindVertexArray(0)
        print(f"✓ Mesh created with {self.vertex_count} vertices")
    
    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        glBindVertexArray(0)

class Renderer:
    def __init__(self):
        self.shaders = {}
        self.meshes = {}
        print("✓ Renderer initialized")