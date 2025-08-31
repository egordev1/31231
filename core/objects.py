from OpenGL.GL import *
import math
from .material import MaterialLibrary

class GameObject:
    PRIMITIVE_CUBE = 0
    PRIMITIVE_SPHERE = 1
    PRIMITIVE_CYLINDER = 2
    
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
        self.collider_type = None
        self.collider_size = [1.0, 1.0, 1.0]
        self.collider_center = [0.0, 0.0, 0.0]
        self.collider_is_trigger = False
        
        self.has_rigidbody = False
        self.rigidbody_mass = 1.0
        self.rigidbody_use_gravity = True
        self.rigidbody_is_kinematic = False
        self.rigidbody_drag = 0.1
        self.rigidbody_angular_drag = 0.05
        
        # Velocity attributes for physics
        self.velocity = [0.0, 0.0, 0.0]
        self.angular_velocity = [0.0, 0.0, 0.0]
        
        # Render properties
        self.visible = True
        self.static = False
        
        # Material library
        self.material_lib = MaterialLibrary()
        
    def draw(self):
        if not self.visible:
            return
            
        glPushMatrix()
        glTranslatef(*self.position)
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glScalef(*self.scale)

        # Apply material
        material = self.material_lib.get_material(self.material_name)
        material.apply()
        
        glColor3f(*self.color)

        if self.primitive_type == self.PRIMITIVE_CUBE:
            self.draw_cube()
        elif self.primitive_type == self.PRIMITIVE_SPHERE:
            self.draw_sphere(0.5, 16, 16)
        elif self.primitive_type == self.PRIMITIVE_CYLINDER:
            self.draw_cylinder(0.3, 1.0, 16)

        glPopMatrix()

    def add_collider(self, collider_type="BOX", size=(1.0, 1.0, 1.0), center=(0.0, 0.0, 0.0), is_trigger=False):
        self.collider_type = collider_type
        self.collider_size = list(size)
        self.collider_center = list(center)
        self.collider_is_trigger = is_trigger
        return self
        
    def add_rigidbody(self, mass=1.0, use_gravity=True, is_kinematic=False, drag=0.1, angular_drag=0.05):
        self.has_rigidbody = True
        self.rigidbody_mass = mass
        self.rigidbody_use_gravity = use_gravity
        self.rigidbody_is_kinematic = is_kinematic
        self.rigidbody_drag = drag
        self.rigidbody_angular_drag = angular_drag
        return self

    def draw_cube(self):
        vertices = [
            [(-0.5, -0.5, 0.5), (0, 0, 1)],
            [(0.5, -0.5, 0.5), (0, 0, 1)],
            [(0.5, 0.5, 0.5), (0, 0, 1)],
            [(-0.5, 0.5, 0.5), (0, 0, 1)],
            
            [(-0.5, -0.5, -0.5), (0, 0, -1)],
            [(-0.5, 0.5, -0.5), (0, 0, -1)],
            [(0.5, 0.5, -0.5), (0, 0, -1)],
            [(0.5, -0.5, -0.5), (0, 0, -1)],
            
            [(-0.5, -0.5, -0.5), (-1, 0, 0)],
            [(-0.5, -0.5, 0.5), (-1, 0, 0)],
            [(-0.5, 0.5, 0.5), (-1, 0, 0)],
            [(-0.5, 0.5, -0.5), (-1, 0, 0)],
            
            [(0.5, -0.5, -0.5), (1, 0, 0)],
            [(0.5, 0.5, -0.5), (1, 0, 0)],
            [(0.5, 0.5, 0.5), (1, 0, 0)],
            [(0.5, -0.5, 0.5), (1, 0, 0)],
            
            [(-0.5, 0.5, -0.5), (0, 1, 0)],
            [(-0.5, 0.5, 0.5), (0, 1, 0)],
            [(0.5, 0.5, 0.5), (0, 1, 0)],
            [(0.5, 0.5, -0.5), (0, 1, 0)],
            
            [(-0.5, -0.5, -0.5), (0, -1, 0)],
            [(0.5, -0.5, -0.5), (0, -1, 0)],
            [(0.5, -0.5, 0.5), (0, -1, 0)],
            [(-0.5, -0.5, 0.5), (0, -1, 0)]
        ]
        
        glBegin(GL_QUADS)
        for vertex, normal in vertices:
            glNormal3f(*normal)
            glVertex3f(*vertex)
        glEnd()

    def draw_sphere(self, radius, slices, stacks):
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

    def draw_cylinder(self, radius, height, segments):
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