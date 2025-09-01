from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSlider, 
                             QPushButton, QLabel, QDoubleSpinBox, QGroupBox,
                             QFormLayout, QComboBox, QCheckBox, QToolBar,
                             QAction, QSplitter, QScrollArea, QFrame,
                             QSizePolicy, QTabWidget, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, QPoint, QSize, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QImage, QPixmap, QIcon
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
import noise
import random
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import json

class TerrainBrushType(Enum):
    RAISE = "raise"
    LOWER = "lower"
    SMOOTH = "smooth"
    FLATTEN = "flatten"
    TEXTURE = "texture"

@dataclass
class TerrainBrush:
    size: float = 10.0
    strength: float = 1.0
    brush_type: TerrainBrushType = TerrainBrushType.RAISE
    falloff: float = 0.5  # 0.0 - резкий, 1.0 - плавный
    texture_index: int = 0

class TerrainLayer:
    def __init__(self, name: str, texture_path: str = None):
        self.name = name
        self.texture_path = texture_path
        self.texture_id = None
        self.tiling = 10.0
        self.metallic = 0.0
        self.roughness = 0.8
        self.normal_strength = 1.0
        self.enabled = True
        
    def load_texture(self):
        if self.texture_path:
            try:
                image = Image.open(self.texture_path)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image = image.transpose(Image.FLIP_TOP_BOTTOM)
                img_data = np.array(image, np.uint8)
                
                self.texture_id = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, self.texture_id)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 
                            0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
                
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                
                glGenerateMipmap(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, 0)
                
            except Exception as e:
                print(f"Error loading terrain texture {self.texture_path}: {e}")

class Terrain:
    def __init__(self, width=100, height=100, resolution=1.0):
        self.width = width
        self.height = height
        self.resolution = resolution
        self.heightmap = np.zeros((height, width), dtype=np.float32)
        self.texture_map = np.zeros((height, width, 4), dtype=np.float32)  # RGBA splatmap
        self.normal_map = None
        self.layers: List[TerrainLayer] = []
        self.vertex_buffer = None
        self.normal_buffer = None
        self.uv_buffer = None
        self.index_buffer = None
        self.dirty = True  # Флаг необходимости пересчета геометрии
        
    def generate_from_heightmap(self, heightmap_path: str):
        try:
            image = Image.open(heightmap_path).convert('L')
            image = image.resize((self.width, self.height))
            self.heightmap = np.array(image, dtype=np.float32) / 255.0
            self.dirty = True
        except Exception as e:
            print(f"Error loading heightmap: {e}")
            
    def generate_perlin_noise(self, scale=50.0, octaves=6, persistence=0.5, lacunarity=2.0):
        """Генерация террейна на основе шума Перлина"""
        world_x = np.linspace(0, scale, self.width)
        world_y = np.linspace(0, scale, self.height)
        x, y = np.meshgrid(world_x, world_y)
        
        self.heightmap = np.zeros((self.height, self.width))
        
        for i in range(self.height):
            for j in range(self.width):
                self.heightmap[i][j] = noise.pnoise2(
                    x[i][j], y[i][j],
                    octaves=octaves,
                    persistence=persistence,
                    lacunarity=lacunarity,
                    repeatx=scale,
                    repeaty=scale,
                    base=42
                )
        
        # Нормализуем высоты от 0 до 1
        self.heightmap = (self.heightmap - self.heightmap.min()) / (self.heightmap.max() - self.heightmap.min())
        self.dirty = True
        
    def add_layer(self, layer: TerrainLayer):
        self.layers.append(layer)
        layer.load_texture()
        
    def update_normals(self):
        """Вычисление нормалей для террейна"""
        self.normal_map = np.zeros((self.height, self.width, 3), dtype=np.float32)
        
        for z in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                # Высоты соседних точек
                left = self.heightmap[z][x-1]
                right = self.heightmap[z][x+1]
                down = self.heightmap[z-1][x]
                up = self.heightmap[z+1][x]
                
                # Вектора нормали
                normal_x = (left - right) * 0.5
                normal_y = 1.0  # Вертикальная компонента
                normal_z = (down - up) * 0.5
                
                # Нормализуем
                length = max(1e-6, np.sqrt(normal_x**2 + normal_y**2 + normal_z**2))
                self.normal_map[z][x] = [normal_x/length, normal_y/length, normal_z/length]
        
    def build_mesh(self):
        """Построение mesh для террейна"""
        if not self.dirty:
            return
            
        self.update_normals()
        
        vertices = []
        normals = []
        uvs = []
        indices = []
        
        # Генерация вершин
        for z in range(self.height):
            for x in range(self.width):
                # Позиция вершины
                y = self.heightmap[z][x]
                vertices.extend([x * self.resolution, y, z * self.resolution])
                
                # Нормаль
                normal = self.normal_map[z][x] if self.normal_map is not None else [0, 1, 0]
                normals.extend(normal)
                
                # UV координаты
                uvs.extend([x / (self.width - 1), z / (self.height - 1)])
        
        # Генерация индексов
        for z in range(self.height - 1):
            for x in range(self.width - 1):
                # Два треугольника на квад
                i0 = z * self.width + x
                i1 = z * self.width + x + 1
                i2 = (z + 1) * self.width + x
                i3 = (z + 1) * self.width + x + 1
                
                indices.extend([i0, i1, i2])  # Первый треугольник
                indices.extend([i2, i1, i3])  # Второй треугольник
        
        # Создание OpenGL буферов
        if self.vertex_buffer is None:
            self.vertex_buffer = glGenBuffers(1)
            self.normal_buffer = glGenBuffers(1)
            self.uv_buffer = glGenBuffers(1)
            self.index_buffer = glGenBuffers(1)
        
        # Заполнение буферов
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glBufferData(GL_ARRAY_BUFFER, np.array(vertices, dtype=np.float32), GL_STATIC_DRAW)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.normal_buffer)
        glBufferData(GL_ARRAY_BUFFER, np.array(normals, dtype=np.float32), GL_STATIC_DRAW)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.uv_buffer)
        glBufferData(GL_ARRAY_BUFFER, np.array(uvs, dtype=np.float32), GL_STATIC_DRAW)
        
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, np.array(indices, dtype=np.uint32), GL_STATIC_DRAW)
        
        self.dirty = False
        
    def draw(self):
        """Отрисовка террейна"""
        if self.dirty:
            self.build_mesh()
            
        if self.vertex_buffer is None:
            return
            
        # Включаем текстуры слоев
        for i, layer in enumerate(self.layers):
            if layer.enabled and layer.texture_id:
                glActiveTexture(GL_TEXTURE0 + i)
                glBindTexture(GL_TEXTURE_2D, layer.texture_id)
        
        # Рисуем mesh
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glVertexPointer(3, GL_FLOAT, 0, None)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.normal_buffer)
        glNormalPointer(GL_FLOAT, 0, None)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.uv_buffer)
        glTexCoordPointer(2, GL_FLOAT, 0, None)
        
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
        glDrawElements(GL_TRIANGLES, (self.width - 1) * (self.height - 1) * 6, GL_UNSIGNED_INT, None)
        
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        
        # Отключаем текстуры
        for i in range(len(self.layers)):
            glActiveTexture(GL_TEXTURE0 + i)
            glBindTexture(GL_TEXTURE_2D, 0)
            
    def apply_brush(self, brush: TerrainBrush, position: Tuple[float, float]):
        """Применение кисти к террейну"""
        center_x, center_z = position
        center_x /= self.resolution
        center_z /= self.resolution
        
        brush_size = int(brush.size / self.resolution)
        brush_strength = brush.strength * 0.1
        
        for dz in range(-brush_size, brush_size + 1):
            for dx in range(-brush_size, brush_size + 1):
                x = int(center_x + dx)
                z = int(center_z + dz)
                
                if 0 <= x < self.width and 0 <= z < self.height:
                    # Расстояние от центра кисти
                    distance = np.sqrt(dx**2 + dz**2) / brush_size
                    if distance > 1.0:
                        continue
                        
                    # Коэффициент влияния (с falloff)
                    influence = 1.0 - distance
                    influence = pow(influence, 1.0 / max(0.1, brush.falloff))
                    influence *= brush_strength
                    
                    # Применяем эффект в зависимости от типа кисти
                    if brush.brush_type == TerrainBrushType.RAISE:
                        self.heightmap[z][x] += influence
                    elif brush.brush_type == TerrainBrushType.LOWER:
                        self.heightmap[z][x] -= influence
                    elif brush.brush_type == TerrainBrushType.SMOOTH:
                        # Сглаживание - усреднение с соседями
                        neighbors = 0
                        total = 0
                        for nz in range(max(0, z-1), min(self.height, z+2)):
                            for nx in range(max(0, x-1), min(self.width, x+2)):
                                if nz != z or nx != x:
                                    neighbors += 1
                                    total += self.heightmap[nz][nx]
                        if neighbors > 0:
                            average = total / neighbors
                            self.heightmap[z][x] += (average - self.heightmap[z][x]) * influence
                    elif brush.brush_type == TerrainBrushType.FLATTEN:
                        # Выравнивание к заданной высоте
                        target_height = 0.5  # Можно сделать настраиваемым
                        self.heightmap[z][x] += (target_height - self.heightmap[z][x]) * influence
                    
                    # Ограничиваем высоты
                    self.heightmap[z][x] = max(0.0, min(1.0, self.heightmap[z][x]))
        
        self.dirty = True
        
    def get_height_at(self, x: float, z: float) -> float:
        """Получить высоту в точке"""
        grid_x = x / self.resolution
        grid_z = z / self.resolution
        
        if grid_x < 0 or grid_x >= self.width - 1 or grid_z < 0 or grid_z >= self.height - 1:
            return 0.0
            
        # Билинейная интерполяция
        x1 = int(grid_x)
        z1 = int(grid_z)
        x2 = min(x1 + 1, self.width - 1)
        z2 = min(z1 + 1, self.height - 1)
        
        dx = grid_x - x1
        dz = grid_z - z1
        
        h11 = self.heightmap[z1][x1]
        h12 = self.heightmap[z1][x2]
        h21 = self.heightmap[z2][x1]
        h22 = self.heightmap[z2][x2]
        
        # Интерполяция по X
        h1 = h11 * (1 - dx) + h12 * dx
        h2 = h21 * (1 - dx) + h22 * dx
        
        # Интерполяция по Z
        return h1 * (1 - dz) + h2 * dz

class TerrainEditor(QWidget):
    """Редактор террейна"""
    def __init__(self, terrain: Terrain):
        super().__init__()
        self.terrain = terrain
        self.brush = TerrainBrush()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Панель инструментов
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        
        # Кисти
        brush_actions = [
            ("Raise", TerrainBrushType.RAISE, "terrain_raise.png"),
            ("Lower", TerrainBrushType.LOWER, "terrain_lower.png"),
            ("Smooth", TerrainBrushType.SMOOTH, "terrain_smooth.png"),
            ("Flatten", TerrainBrushType.FLATTEN, "terrain_flatten.png"),
            ("Texture", TerrainBrushType.TEXTURE, "terrain_texture.png")
        ]
        
        self.brush_group = QButtonGroup(self)
        for text, brush_type, icon in brush_actions:
            action = QAction(QIcon(f"icons/{icon}"), text, self)
            action.setCheckable(True)
            action.setData(brush_type)
            action.triggered.connect(lambda checked, t=brush_type: self.set_brush_type(t))
            toolbar.addAction(action)
            self.brush_group.addAction(action)
        
        # Выбираем первую кисть по умолчанию
        if self.brush_group.actions():
            self.brush_group.actions()[0].setChecked(True)
        
        toolbar.addSeparator()
        
        # Настройки кисти
        toolbar.addWidget(QLabel("Size:"))
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(1, 100)
        self.size_slider.setValue(int(self.brush.size))
        self.size_slider.valueChanged.connect(self.set_brush_size)
        toolbar.addWidget(self.size_slider)
        
        toolbar.addWidget(QLabel("Strength:"))
        self.strength_slider = QSlider(Qt.Horizontal)
        self.strength_slider.setRange(1, 100)
        self.strength_slider.setValue(int(self.brush.strength * 10))
        self.strength_slider.valueChanged.connect(self.set_brush_strength)
        toolbar.addWidget(self.strength_slider)
        
        layout.addWidget(toolbar)
        
        # Основная область
        splitter = QSplitter(Qt.Horizontal)
        
        # Панель слоев
        layers_panel = QGroupBox("Terrain Layers")
        layers_layout = QVBoxLayout(layers_panel)
        
        self.layers_list = QListWidget()
        layers_layout.addWidget(self.layers_list)
        
        layer_buttons = QHBoxLayout()
        self.add_layer_btn = QPushButton("Add Layer")
        self.remove_layer_btn = QPushButton("Remove Layer")
        self.move_up_btn = QPushButton("↑")
        self.move_down_btn = QPushButton("↓")
        
        layer_buttons.addWidget(self.add_layer_btn)
        layer_buttons.addWidget(self.remove_layer_btn)
        layer_buttons.addWidget(self.move_up_btn)
        layer_buttons.addWidget(self.move_down_btn)
        
        layers_layout.addLayout(layer_buttons)
        splitter.addWidget(layers_panel)
        
        # Панель свойств
        properties_panel = QGroupBox("Layer Properties")
        properties_layout = QFormLayout(properties_panel)
        
        self.layer_name_edit = QLineEdit()
        self.layer_texture_edit = QLineEdit()
        self.layer_texture_btn = QPushButton("Browse...")
        self.layer_tiling_spin = QDoubleSpinBox()
        self.layer_tiling_spin.setRange(0.1, 100.0)
        self.layer_metallic_spin = QDoubleSpinBox()
        self.layer_metallic_spin.setRange(0.0, 1.0)
        self.layer_roughness_spin = QDoubleSpinBox()
        self.layer_roughness_spin.setRange(0.0, 1.0)
        
        texture_layout = QHBoxLayout()
        texture_layout.addWidget(self.layer_texture_edit)
        texture_layout.addWidget(self.layer_texture_btn)
        
        properties_layout.addRow("Name:", self.layer_name_edit)
        properties_layout.addRow("Texture:", texture_layout)
        properties_layout.addRow("Tiling:", self.layer_tiling_spin)
        properties_layout.addRow("Metallic:", self.layer_metallic_spin)
        properties_layout.addRow("Roughness:", self.layer_roughness_spin)
        
        splitter.addWidget(properties_panel)
        
        splitter.setSizes([200, 300])
        layout.addWidget(splitter)
        
        # Кнопки генерации
        generate_group = QGroupBox("Terrain Generation")
        generate_layout = QHBoxLayout(generate_group)
        
        self.generate_noise_btn = QPushButton("Generate Noise")
        self.import_heightmap_btn = QPushButton("Import Heightmap")
        self.export_heightmap_btn = QPushButton("Export Heightmap")
        self.reset_btn = QPushButton("Reset Terrain")
        
        generate_layout.addWidget(self.generate_noise_btn)
        generate_layout.addWidget(self.import_heightmap_btn)
        generate_layout.addWidget(self.export_heightmap_btn)
        generate_layout.addWidget(self.reset_btn)
        
        layout.addWidget(generate_group)
        
        # Подключаем сигналы
        self.add_layer_btn.clicked.connect(self.add_layer)
        self.remove_layer_btn.clicked.connect(self.remove_layer)
        self.generate_noise_btn.clicked.connect(self.generate_noise)
        self.reset_btn.clicked.connect(self.reset_terrain)
        self.layers_list.currentRowChanged.connect(self.select_layer)
        
    def set_brush_type(self, brush_type: TerrainBrushType):
        self.brush.brush_type = brush_type
        
    def set_brush_size(self, size: int):
        self.brush.size = size
        
    def set_brush_strength(self, strength: int):
        self.brush.strength = strength / 10.0
        
    def add_layer(self):
        new_layer = TerrainLayer(f"Layer {len(self.terrain.layers) + 1}")
        self.terrain.add_layer(new_layer)
        self.update_layers_list()
        
    def remove_layer(self):
        current_row = self.layers_list.currentRow()
        if current_row >= 0 and current_row < len(self.terrain.layers):
            self.terrain.layers.pop(current_row)
            self.update_layers_list()
            
    def update_layers_list(self):
        self.layers_list.clear()
        for layer in self.terrain.layers:
            item = QListWidgetItem(layer.name)
            item.setCheckState(Qt.Checked if layer.enabled else Qt.Unchecked)
            self.layers_list.addItem(item)
            
    def select_layer(self, row: int):
        if row >= 0 and row < len(self.terrain.layers):
            layer = self.terrain.layers[row]
            self.layer_name_edit.setText(layer.name)
            self.layer_texture_edit.setText(layer.texture_path or "")
            self.layer_tiling_spin.setValue(layer.tiling)
            self.layer_metallic_spin.setValue(layer.metallic)
            self.layer_roughness_spin.setValue(layer.roughness)
            
    def generate_noise(self):
        self.terrain.generate_perlin_noise()
        
    def reset_terrain(self):
        self.terrain.heightmap = np.zeros((self.terrain.height, self.terrain.width), dtype=np.float32)
        self.terrain.dirty = True

class TerrainPlugin(Plugin):
    """Плагин системы террейна"""
    def __init__(self):
        super().__init__()
        self.name = "Terrain System"
        self.version = "1.0.0"
        self.description = "Advanced terrain editing and rendering system"
        
    def initialize(self, app):
        # Создаем тестовый террейн
        self.terrain = Terrain(256, 256, 0.5)
        self.terrain.generate_perlin_noise()
        
        # Добавляем слои по умолчанию
        grass_layer = TerrainLayer("Grass", "textures/terrain/grass.jpg")
        rock_layer = TerrainLayer("Rock", "textures/terrain/rock.jpg")
        snow_layer = TerrainLayer("Snow", "textures/terrain/snow.jpg")
        
        self.terrain.add_layer(grass_layer)
        self.terrain.add_layer(rock_layer)
        self.terrain.add_layer(snow_layer)
        
        # Создаем редактор
        self.editor = TerrainEditor(self.terrain)
        
        # Добавляем в интерфейс
        terrain_dock = QDockWidget("Terrain Editor", app)
        terrain_dock.setWidget(self.editor)
        app.addDockWidget(Qt.RightDockWidgetArea, terrain_dock)
        
        # Регистрируем террейн в сцене
        if hasattr(app, 'scene'):
            app.scene.terrain = self.terrain
            
    def update(self, delta_time: float):
        # Обновление террейна (если нужно)
        pass