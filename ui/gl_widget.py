from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QCursor
from OpenGL.GL import *
from OpenGL.GLU import *
from math import sin, cos, radians, sqrt, atan2, degrees
import time
import numpy as np

class GLWidget(QOpenGLWidget):
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.scene = scene
        
        self.camera_position = [0.0, 2.0, 8.0]
        self.camera_rotation = [-15.0, 0.0]
        self.camera_speed = 2.0
        self.rotation_speed = 0.3
        self.camera_near = 0.1
        self.camera_far = 1000.0
        self.camera_fov = 60.0
        
        self.is_rotating = False
        self.is_panning = False
        self.is_orbiting = False
        self.last_mouse_pos = QPoint()
        self.mouse_sensitivity = 0.1
        
        self.show_grid = True
        self.show_axes = True
        self.show_gizmos = True
        self.show_colliders = False
        self.show_normals = False
        self.lighting_enabled = True
        self.wireframe_mode = False
        self.shading_mode = 0
        
        self.msaa_samples = 4
        self.vsync_enabled = True
        
        self.last_time = time.time()
        self.delta_time = 0.0
        self.fps = 60
        self.frame_count = 0
        self.fps_time = 0.0
        
        self.hovered_object = None
        self.dragging = False
        self.drag_start_pos = QPoint()
        
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        
        format = self.format()
        format.setSamples(self.msaa_samples)
        self.setFormat(format)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glEnable(GL_POLYGON_OFFSET_LINE)
        glPolygonOffset(-1.0, -1.0)
        
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glShadeModel(GL_SMOOTH)
        
        glLightfv(GL_LIGHT0, GL_POSITION, [0.5, 1.0, 0.5, 0.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        
        glClearColor(0.22, 0.22, 0.22, 1.0)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        aspect = w / h if h > 0 else 1
        gluPerspective(self.camera_fov, aspect, self.camera_near, self.camera_far)
        
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        current_time = time.time()
        self.delta_time = current_time - self.last_time
        self.last_time = current_time
        self.frame_count += 1
        self.fps_time += self.delta_time
        
        if self.fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_time = 0.0
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        self.scene.update(self.delta_time)
        
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, self.scene.ambient_light)
        
        self.update_camera()
        
        if self.wireframe_mode or self.shading_mode == 2:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            
        if self.lighting_enabled and self.shading_mode == 0:
            glEnable(GL_LIGHTING)
        else:
            glDisable(GL_LIGHTING)
        
        if self.show_grid:
            self.draw_grid()
        if self.show_axes:
            self.draw_axes()
        
        for obj in self.scene.objects:
            self.draw_object(obj)
        
        if self.show_colliders:
            self.draw_colliders()
        
        if self.show_gizmos:
            self.draw_gizmos()
        
        for ps in self.scene.particle_systems:
            ps.draw()

    def update_camera(self):
        glRotatef(self.camera_rotation[0], 1, 0, 0)
        glRotatef(self.camera_rotation[1], 0, 1, 0)
        glTranslatef(-self.camera_position[0], -self.camera_position[1], -self.camera_position[2])

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.is_rotating = True
            self.setCursor(Qt.ClosedHandCursor)
        elif event.button() == Qt.MiddleButton:
            self.is_panning = True
            self.setCursor(Qt.SizeAllCursor)
        elif event.button() == Qt.LeftButton and event.modifiers() & Qt.AltModifier:
            self.is_orbiting = True
            self.setCursor(Qt.SizeAllCursor)
        elif event.button() == Qt.LeftButton:
            self.handle_object_selection(event.pos())
        
        self.last_mouse_pos = event.pos()

    def mouseReleaseEvent(self, event):
        self.is_rotating = False
        self.is_panning = False
        self.is_orbiting = False
        self.setCursor(Qt.ArrowCursor)

    def mouseMoveEvent(self, event):
        dx = event.x() - self.last_mouse_pos.x()
        dy = event.y() - self.last_mouse_pos.y()
        
        if self.is_rotating:
            self.camera_rotation[1] += dx * self.rotation_speed
            self.camera_rotation[0] += dy * self.rotation_speed
            self.camera_rotation[0] = max(-89, min(89, self.camera_rotation[0]))
            
        elif self.is_panning:
            right = self.get_right_vector()
            up = self.get_up_vector()
            
            pan_speed = 0.01 * self.get_camera_distance()
            self.camera_position[0] -= right[0] * dx * pan_speed
            self.camera_position[1] -= right[1] * dx * pan_speed
            self.camera_position[2] -= right[2] * dx * pan_speed
            
            self.camera_position[0] += up[0] * dy * pan_speed
            self.camera_position[1] += up[1] * dy * pan_speed
            self.camera_position[2] += up[2] * dy * pan_speed
            
        elif self.is_orbiting:
            if self.scene.selected_object:
                target = self.scene.selected_object.position
                distance = self.get_camera_distance()
                
                self.camera_rotation[1] += dx * self.rotation_speed
                self.camera_rotation[0] += dy * self.rotation_speed
                self.camera_rotation[0] = max(-89, min(89, self.camera_rotation[0]))
                
                forward = self.get_forward_vector()
                self.camera_position = [
                    target[0] - forward[0] * distance,
                    target[1] - forward[1] * distance,
                    target[2] - forward[2] * distance
                ]
        
        self.last_mouse_pos = event.pos()
        self.update()

    def wheelEvent(self, event):
        zoom_speed = 0.002 * self.get_camera_distance()
        forward = self.get_forward_vector()
        
        self.camera_position[0] += forward[0] * event.angleDelta().y() * zoom_speed
        self.camera_position[1] += forward[1] * event.angleDelta().y() * zoom_speed
        self.camera_position[2] += forward[2] * event.angleDelta().y() * zoom_speed
        
        self.update()

    def keyPressEvent(self, event):
        move_speed = self.camera_speed * self.delta_time
        forward = self.get_forward_vector()
        right = self.get_right_vector()
        
        if event.key() == Qt.Key_W:
            self.camera_position[0] += forward[0] * move_speed
            self.camera_position[1] += forward[1] * move_speed
            self.camera_position[2] += forward[2] * move_speed
        elif event.key() == Qt.Key_S:
            self.camera_position[0] -= forward[0] * move_speed
            self.camera_position[1] -= forward[1] * move_speed
            self.camera_position[2] -= forward[2] * move_speed
        elif event.key() == Qt.Key_A:
            self.camera_position[0] -= right[0] * move_speed
            self.camera_position[1] -= right[1] * move_speed
            self.camera_position[2] -= right[2] * move_speed
        elif event.key() == Qt.Key_D:
            self.camera_position[0] += right[0] * move_speed
            self.camera_position[1] += right[1] * move_speed
            self.camera_position[2] += right[2] * move_speed
        elif event.key() == Qt.Key_Q:
            self.camera_position[1] -= move_speed
        elif event.key() == Qt.Key_E:
            self.camera_position[1] += move_speed
        elif event.key() == Qt.Key_G:
            self.show_grid = not self.show_grid
        elif event.key() == Qt.Key_X:
            self.show_axes = not self.show_axes
        elif event.key() == Qt.Key_Z:
            self.show_gizmos = not self.show_gizmos
        elif event.key() == Qt.Key_C:
            self.show_colliders = not self.show_colliders
        elif event.key() == Qt.Key_L:
            self.lighting_enabled = not self.lighting_enabled
        
        self.update()

    def get_forward_vector(self):
        pitch = radians(self.camera_rotation[0])
        yaw = radians(self.camera_rotation[1])
        
        x = sin(yaw) * cos(pitch)
        y = -sin(pitch)
        z = -cos(yaw) * cos(pitch)
        
        length = sqrt(x*x + y*y + z*z)
        if length > 0:
            return [x/length, y/length, z/length]
        return [0, 0, -1]

    def get_right_vector(self):
        forward = self.get_forward_vector()
        up = [0, 1, 0]
        
        rx = forward[1] * up[2] - forward[2] * up[1]
        ry = forward[2] * up[0] - forward[0] * up[2]
        rz = forward[0] * up[1] - forward[1] * up[0]
        
        length = sqrt(rx*rx + ry*ry + rz*rz)
        if length > 0:
            return [rx/length, ry/length, rz/length]
        return [1, 0, 0]

    def get_up_vector(self):
        forward = self.get_forward_vector()
        right = self.get_right_vector()
        
        ux = right[1] * forward[2] - right[2] * forward[1]
        uy = right[2] * forward[0] - right[0] * forward[2]
        uz = right[0] * forward[1] - right[1] * forward[0]
        
        length = sqrt(ux*ux + uy*uy + uz*uz)
        if length > 0:
            return [ux/length, uy/length, uz/length]
        return [0, 1, 0]

    def get_camera_distance(self):
        return sqrt(self.camera_position[0]**2 + 
                   self.camera_position[1]**2 + 
                   self.camera_position[2]**2)

    def handle_object_selection(self, mouse_pos):
        x = mouse_pos.x()
        y = self.height() - mouse_pos.y()
        normalized_x = (2.0 * x) / self.width() - 1.0
        normalized_y = (2.0 * y) / self.height() - 1.0
        
        ray_origin, ray_direction = self.screen_to_world_ray(normalized_x, normalized_y)
        
        closest_obj = None
        closest_distance = float('inf')
        
        for obj in self.scene.objects:
            if not obj.visible or not obj.collider_type:
                continue
                
            hit, distance = self.scene.physics.ray_aabb_intersection(ray_origin, ray_direction, obj)
            if hit and distance < closest_distance:
                closest_obj = obj
                closest_distance = distance
        
        if closest_obj:
            self.scene.selected_object = closest_obj
            if hasattr(self.parent(), 'on_object_selected'):
                self.parent().on_object_selected(closest_obj)

    def screen_to_world_ray(self, normalized_x, normalized_y):
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        
        near_point = gluUnProject(normalized_x, normalized_y, 0.0, modelview, projection, viewport)
        far_point = gluUnProject(normalized_x, normalized_y, 1.0, modelview, projection, viewport)
        
        if near_point and far_point:
            ray_origin = np.array(near_point)
            ray_direction = np.array(far_point) - ray_origin
            ray_direction = ray_direction / np.linalg.norm(ray_direction)
            return ray_origin, ray_direction
        
        return np.array([0, 0, 0]), np.array([0, 0, -1])

    def draw_grid(self):
        glDisable(GL_LIGHTING)
        glLineWidth(1.0)
        
        glColor4f(0.4, 0.4, 0.4, 0.6)
        glBegin(GL_LINES)
        size = 50
        for i in range(-size, size + 1, 5):
            if i == 0:
                continue
            glVertex3f(i, 0, -size)
            glVertex3f(i, 0, size)
            glVertex3f(-size, 0, i)
            glVertex3f(size, 0, i)
        glEnd()
        
        glColor4f(0.3, 0.3, 0.3, 0.3)
        glBegin(GL_LINES)
        for i in range(-size, size + 1):
            if i % 5 != 0:
                glVertex3f(i, 0, -size)
                glVertex3f(i, 0, size)
                glVertex3f(-size, 0, i)
                glVertex3f(size, 0, i)
        glEnd()
        
        glLineWidth(2.0)
        glColor4f(0.8, 0.8, 0.8, 0.8)
        glBegin(GL_LINES)
        glVertex3f(-size, 0, 0)
        glVertex3f(size, 0, 0)
        glVertex3f(0, 0, -size)
        glVertex3f(0, 0, size)
        glEnd()
        
        glEnable(GL_LIGHTING)

    def draw_axes(self):
        glDisable(GL_LIGHTING)
        glLineWidth(3.0)
        
        glBegin(GL_LINES)
        glColor3f(1, 0.2, 0.2)
        glVertex3f(0, 0, 0)
        glVertex3f(3, 0, 0)
        
        glColor3f(0.2, 1, 0.2)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 3, 0)
        
        glColor3f(0.2, 0.4, 1)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 3)
        glEnd()
        
        glPointSize(6.0)
        glBegin(GL_POINTS)
        glColor3f(1, 0, 0)
        glVertex3f(3.2, 0, 0)
        glColor3f(0, 1, 0)
        glVertex3f(0, 3.2, 0)
        glColor3f(0.2, 0.4, 1)
        glVertex3f(0, 0, 3.2)
        glEnd()
        
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

    def draw_colliders(self):
        glDisable(GL_LIGHTING)
        glLineWidth(1.5)
        
        for obj in self.scene.objects:
            if hasattr(obj, 'collider_type') and obj.collider_type and obj.visible:
                glPushMatrix()
                glTranslatef(*obj.position)
                
                if obj == self.scene.selected_object:
                    glColor4f(0, 1, 0, 0.8)
                else:
                    glColor4f(1, 0.5, 0, 0.6)
                
                if obj.collider_type == "BOX":
                    size = obj.collider_size
                    glBegin(GL_LINE_LOOP)
                    glVertex3f(-size[0]/2, -size[1]/2, -size[2]/2)
                    glVertex3f(size[0]/2, -size[1]/2, -size[2]/2)
                    glVertex3f(size[0]/2, size[1]/2, -size[2]/2)
                    glVertex3f(-size[0]/2, size[1]/2, -size[2]/2)
                    glEnd()
                    
                    glBegin(GL_LINE_LOOP)
                    glVertex3f(-size[0]/2, -size[1]/2, size[2]/2)
                    glVertex3f(size[0]/2, -size[1]/2, size[2]/2)
                    glVertex3f(size[0]/2, size[1]/2, size[2]/2)
                    glVertex3f(-size[0]/2, size[1]/2, size[2]/2)
                    glEnd()
                    
                    glBegin(GL_LINES)
                    glVertex3f(-size[0]/2, -size[1]/2, -size[2]/2)
                    glVertex3f(-size[0]/2, -size[1]/2, size[2]/2)
                    
                    glVertex3f(size[0]/2, -size[1]/2, -size[2]/2)
                    glVertex3f(size[0]/2, -size[1]/2, size[2]/2)
                    
                    glVertex3f(size[0]/2, size[1]/2, -size[2]/2)
                    glVertex3f(size[0]/2, size[1]/2, size[2]/2)
                    
                    glVertex3f(-size[0]/2, size[1]/2, -size[2]/2)
                    glVertex3f(-size[0]/2, size[1]/2, size[2]/2)
                    glEnd()
                
                glPopMatrix()
        
        glEnable(GL_LIGHTING)

    def draw_gizmos(self):
        if not self.scene.selected_object:
            return
            
        obj = self.scene.selected_object
        glDisable(GL_LIGHTING)
        
        glPushMatrix()
        glTranslatef(*obj.position)
        
        glLineWidth(3.0)
        glBegin(GL_LINES)
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(2, 0, 0)
        
        glColor3f(0, 1, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 2, 0)
        
        glColor3f(0, 0.5, 1)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 2)
        glEnd()
        
        glColor4f(1, 1, 1, 0.5)
        glLineWidth(1.5)
        glBegin(GL_LINE_LOOP)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glEnd()
        
        glBegin(GL_LINE_LOOP)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glEnd()
        
        glBegin(GL_LINES)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, 0.5)
        
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glEnd()
        
        glPopMatrix()
        glEnable(GL_LIGHTING)

    def draw_object(self, obj):
        if not obj.visible:
            return
            
        glPushMatrix()
        glTranslatef(*obj.position)
        glRotatef(obj.rotation[0], 1, 0, 0)
        glRotatef(obj.rotation[1], 0, 1, 0)
        glRotatef(obj.rotation[2], 0, 0, 1)
        glScalef(*obj.scale)

        is_selected = obj == self.scene.selected_object
        if is_selected:
            glColor3f(1, 0.8, 0.2)
        else:
            glColor3f(*obj.color)
        
        obj.draw()
        glPopMatrix()

    def reset_camera(self):
        self.camera_position = [0.0, 2.0, 8.0]
        self.camera_rotation = [-15.0, 0.0]
        self.update()

    def set_shading_mode(self, mode):
        self.shading_mode = mode
        if mode == 2:
            self.wireframe_mode = True
            self.lighting_enabled = False
        else:
            self.wireframe_mode = False
            self.lighting_enabled = (mode == 0)
        self.update()

    def focus_on_object(self, obj):
        if obj:
            target_pos = obj.position
            distance = 5.0
            
            self.camera_position = [
                target_pos[0],
                target_pos[1] + 2.0,
                target_pos[2] + distance
            ]
            
            dx = target_pos[0] - self.camera_position[0]
            dy = target_pos[1] - self.camera_position[1]
            dz = target_pos[2] - self.camera_position[2]
            
            self.camera_rotation[1] = degrees(atan2(dx, dz))
            self.camera_rotation[0] = degrees(atan2(dy, sqrt(dx*dx + dz*dz)))
            
            self.update()

    def toggle_grid(self):
        self.show_grid = not self.show_grid
        self.update()

    def toggle_axes(self):
        self.show_axes = not self.show_axes
        self.update()

    def toggle_gizmos(self):
        self.show_gizmos = not self.show_gizmos
        self.update()

    def toggle_colliders(self):
        self.show_colliders = not self.show_colliders
        self.update()

    def toggle_lighting(self):
        self.lighting_enabled = not self.lighting_enabled
        self.update()

    def set_wireframe(self, enabled):
        self.wireframe_mode = enabled
        self.update()

    def get_camera_info(self):
        return {
            'position': self.camera_position.copy(),
            'rotation': self.camera_rotation.copy(),
            'fov': self.camera_fov
        }

    def set_camera_info(self, position, rotation, fov=None):
        self.camera_position = position.copy()
        self.camera_rotation = rotation.copy()
        if fov:
            self.camera_fov = fov
        self.update()