import random
from OpenGL.GL import *
import numpy as np

class Particle:
    def __init__(self):
        self.position = [0, 0, 0]
        self.velocity = [0, 0, 0]
        self.acceleration = [0, 0, 0]
        self.color = [1, 1, 1, 1]
        self.start_color = [1, 1, 1, 1]
        self.end_color = [1, 1, 1, 0]
        self.size = 1.0
        self.start_size = 1.0
        self.end_size = 0.1
        self.lifetime = 1.0
        self.age = 0.0
        self.rotation = 0.0
        self.angular_velocity = 0.0

class ParticleSystem:
    def __init__(self, max_particles=1000):
        self.max_particles = max_particles
        self.particles = []
        self.emission_rate = 10.0
        self.emission_time = 0.0
        self.position = [0, 0, 0]
        self.emission_shape = "POINT"  # POINT, SPHERE, BOX
        self.emission_radius = 1.0
        self.emission_size = [1.0, 1.0, 1.0]
        
        self.start_color = [1, 0.5, 0.2, 1]
        self.end_color = [1, 1, 1, 0]
        self.start_size = 0.1
        self.end_size = 0.01
        self.start_lifetime = 2.0
        self.velocity_range = [-1, 1]
        self.acceleration = [0, -9.8, 0]
        
        self.playing = True
        self.looping = True
        self.duration = 5.0
        self.system_age = 0.0
        
    def update(self, dt):
        self.system_age += dt
        
        if not self.looping and self.system_age >= self.duration:
            self.playing = False
            return
            
        for particle in self.particles[:]:
            particle.age += dt
            if particle.age >= particle.lifetime:
                self.particles.remove(particle)
                continue
                
            # Update physics
            for i in range(3):
                particle.velocity[i] += particle.acceleration[i] * dt
                particle.position[i] += particle.velocity[i] * dt
                
            # Update rotation
            particle.rotation += particle.angular_velocity * dt
                
            # Update visual properties
            t = particle.age / particle.lifetime
            particle.color = [
                particle.start_color[i] + t * (particle.end_color[i] - particle.start_color[i])
                for i in range(4)
            ]
            particle.size = particle.start_size + t * (particle.end_size - particle.start_size)
        
        # Emit new particles
        if self.playing:
            self.emission_time += dt
            particles_to_emit = int(self.emission_rate * self.emission_time)
            
            for _ in range(particles_to_emit):
                if len(self.particles) < self.max_particles:
                    self.emit_particle()
                    
            self.emission_time -= particles_to_emit / self.emission_rate
    
    def emit_particle(self):
        particle = Particle()
        
        # Set emission position based on shape
        if self.emission_shape == "POINT":
            particle.position = self.position[:]
        elif self.emission_shape == "SPHERE":
            angle1 = random.uniform(0, 2 * 3.14159)
            angle2 = random.uniform(0, 3.14159)
            distance = random.uniform(0, self.emission_radius)
            particle.position = [
                self.position[0] + distance * sin(angle2) * cos(angle1),
                self.position[1] + distance * cos(angle2),
                self.position[2] + distance * sin(angle2) * sin(angle1)
            ]
        elif self.emission_shape == "BOX":
            particle.position = [
                self.position[0] + random.uniform(-self.emission_size[0]/2, self.emission_size[0]/2),
                self.position[1] + random.uniform(-self.emission_size[1]/2, self.emission_size[1]/2),
                self.position[2] + random.uniform(-self.emission_size[2]/2, self.emission_size[2]/2)
            ]
        
        particle.velocity = [
            random.uniform(*self.velocity_range),
            random.uniform(*self.velocity_range),
            random.uniform(*self.velocity_range)
        ]
        particle.acceleration = self.acceleration[:]
        particle.color = self.start_color[:]
        particle.start_color = self.start_color[:]
        particle.end_color = self.end_color[:]
        particle.size = self.start_size
        particle.start_size = self.start_size
        particle.end_size = self.end_size
        particle.lifetime = random.uniform(0.8, 1.2) * self.start_lifetime
        particle.age = 0.0
        particle.rotation = random.uniform(0, 360)
        particle.angular_velocity = random.uniform(-180, 180)
        
        self.particles.append(particle)
    
    def draw(self):
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glEnable(GL_TEXTURE_2D)
        
        for particle in self.particles:
            glColor4f(*particle.color)
            size = particle.size
            
            glPushMatrix()
            glTranslatef(*particle.position)
            glRotatef(particle.rotation, 0, 0, 1)
            
            # Billboarded quad
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex3f(-size, -size, 0)
            glTexCoord2f(1, 0); glVertex3f(size, -size, 0)
            glTexCoord2f(1, 1); glVertex3f(size, size, 0)
            glTexCoord2f(0, 1); glVertex3f(-size, size, 0)
            glEnd()
            
            glPopMatrix()
        
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
    
    def play(self):
        self.playing = True
        self.system_age = 0.0
    
    def stop(self):
        self.playing = False
        self.particles.clear()
    
    def pause(self):
        self.playing = False
    
    def set_position(self, position):
        self.position = position[:]
    
    def set_emission_shape(self, shape, radius=1.0, size=None):
        self.emission_shape = shape
        self.emission_radius = radius
        if size:
            self.emission_size = size