from OpenGL.GL import *
import math
import numpy as np

class GameObject:
    PRIMITIVE_CUBE = 0
    PRIMITIVE_SPHERE = 1
    PRIMITIVE_CYLINDER = 2
    PRIMITIVE_PLANE = 3
    
    def __init__(self, name="GameObject", position=(0.0, 0.0, 0.0), 
                 color=(1.0, 0.5, 0.3), primitive_type=0, material_name="Default"):
        self.name = name
        self.position = list(position)
        self.rotation = [0.0, 0.0, 0.0]
        self.scale = [1.0, 1.0, 1.0]
        self.color = list(color)
        self.primitive_type = primitive_type
        self.material_name = material_name
        
        # Physics components
        self.collider = None
        self.rigidbody = None
        
        # Velocity attributes for physics
        self.velocity = [0.0, 0.0, 0.0]
        self.angular_velocity = [0.0, 0.0, 0.0]
        
        # Render properties
        self.visible = True
        self.static = False
        self.tag = "Untagged"
        
        # Modern OpenGL properties
        self.mesh = None
        self.material_lib = None
        self._scene = None  # Reference to parent scene
        
        # Scripts
        self.scripts = []
    
    def draw(self, shader=None):
        if not self.visible:
            return
            
        if self.mesh and hasattr(self, '_scene') and self._scene and hasattr(self._scene, 'camera_position'):
            # Modern OpenGL rendering
            self._draw_modern(shader)
        else:
            # Fallback to legacy rendering
            self._draw_legacy()
    
    def _draw_modern(self, shader):
        """Modern OpenGL rendering"""
        if not self.mesh or not shader:
            return
            
        # Set material
        material = self.material_lib.get_material(self.material_name) if self.material_lib else None
        if material:
            material.apply(shader)
        else:
            # Default material properties
            shader.set_uniform("material.albedo", self.color + [1.0])
            shader.set_uniform("material.metallic", 0.0)
            shader.set_uniform("material.roughness", 0.8)
        
        # Set model matrix
        model_matrix = self._get_model_matrix()
        shader.set_uniform("model", model_matrix)
        
        # Draw mesh
        self.mesh.draw()
    
    def _draw_legacy(self):
        """Legacy OpenGL rendering (fallback)"""
        glPushMatrix()
        glTranslatef(*self.position)
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glScalef(*self.scale)

        glColor3f(*self.color)

        if self.primitive_type == self.PRIMITIVE_CUBE:
            self._draw_cube_legacy()
        elif self.primitive_type == self.PRIMITIVE_SPHERE:
            self._draw_sphere_legacy(0.5, 16, 16)
        elif self.primitive_type == self.PRIMITIVE_CYLINDER:
            self._draw_cylinder_legacy(0.3, 1.0, 16)
        elif self.primitive_type == self.PRIMITIVE_PLANE:
            self._draw_plane_legacy(1.0, 1.0)

        glPopMatrix()
    
    def _get_model_matrix(self):
        """Calculate model matrix for modern rendering"""
        model = np.identity(4, dtype=np.float32)
        
        # Translation
        model[0, 3] = self.position[0]
        model[1, 3] = self.position[1]
        model[2, 3] = self.position[2]
        
        # Scale
        model[0, 0] = self.scale[0]
        model[1, 1] = self.scale[1]
        model[2, 2] = self.scale[2]
        
        # Rotation (simplified)
        # TODO: Proper rotation matrix
        return model
    
    def add_collider(self, collider_type="BOX", size=(1.0, 1.0, 1.0), center=(0.0, 0.0, 0.0), is_trigger=False):
        # Create a simple collider object
        self.collider = type('Collider', (), {
            'type': collider_type,
            'size': list(size),
            'center': list(center),
            'is_trigger': is_trigger
        })()
        return self
        
    def add_rigidbody(self, mass=1.0, use_gravity=True, is_kinematic=False, drag=0.1, angular_drag=0.05):
        # Create a simple rigidbody object
        self.rigidbody = type('Rigidbody', (), {
            'mass': mass,
            'use_gravity': use_gravity,
            'is_kinematic': is_kinematic,
            'drag': drag,
            'angular_drag': angular_drag,
            'velocity': [0.0, 0.0, 0.0],
            'angular_velocity': [0.0, 0.0, 0.0]
        })()
        return self

    # Legacy drawing methods (keep for compatibility)
    def _draw_cube_legacy(self):
        vertices = [
            [(-0.5, -0.5, 0.5), (0, 0, 1)],
            [(0.5, -0.5, 0.5), (0, 0, 1)],
            # ... keep your existing vertex data
        ]
        
        glBegin(GL_QUADS)
        for vertex, normal in vertices:
            glNormal3f(*normal)
            glVertex3f(*vertex)
        glEnd()

    def _draw_sphere_legacy(self, radius, slices, stacks):
        for i in range(stacks):
            lat0 = math.pi * (-0.5 + (i) / stacks)
            z0 = radius * math.sin(lat0)
            zr0 = radius * math.cos(lat0)

            lat1 = math.pi * (-0.5 + (i+1) / stacks)
            z1 = radius * math.sin(lat1)
            zr1 = radius * math.cos(lat1)

            glBegin(GL_QUAD_STRIP)
            for j in range(slices + 1):
                lng = 2 * math.pi * (j) / slices
                x = math.cos(lng)
                y = math.sin(lng)

                glNormal3f(x * zr0, y * zr0, z0)
                glVertex3f(x * zr0, y * zr0, z0)
                glNormal3f(x * zr1, y * zr1, z1)
                glVertex3f(x * zr1, y * zr1, z1)
            glEnd()

    def _draw_cylinder_legacy(self, radius, height, segments):
        glBegin(GL_QUAD_STRIP)
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            
            glNormal3f(math.cos(angle), 0, math.sin(angle))
            glVertex3f(x, -height/2, z)
            glVertex3f(x, height/2, z)
        glEnd()

        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 1, 0)
        glVertex3f(0, height/2, 0)
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            glVertex3f(x, height/2, z)
        glEnd()

        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, -1, 0)
        glVertex3f(0, -height/2, 0)
        for i in range(segments + 1):
            angle = 2.0 * math.pi * i / segments
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            glVertex3f(x, -height/2, z)
        glEnd()

    def _draw_plane_legacy(self, width, height):
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(-width/2, 0, -height/2)
        glVertex3f(width/2, 0, -height/2)
        glVertex3f(width/2, 0, height/2)
        glVertex3f(-width/2, 0, height/2)
        glEnd()

    def add_script(self, script):
        """Add script component"""
        self.scripts.append(script)
        if hasattr(script, 'set_game_object'):
            script.set_game_object(self)

    def get_component(self, component_type):
        """Get component of specific type"""
        if component_type == 'Transform':
            return self
        elif component_type == 'Collider':
            return self.collider
        elif component_type == 'Rigidbody':
            return self.rigidbody
        # Check scripts
        for script in self.scripts:
            if isinstance(script, component_type):
                return script
        return None

    def __str__(self):
        return f"GameObject '{self.name}' (Position: {self.position})"