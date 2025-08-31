from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QColorDialog, QPushButton, QSlider,
                             QGroupBox, QFormLayout, QFileDialog)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

class MaterialEditor(QWidget):
    def __init__(self, material_lib):
        super().__init__()
        self.material_lib = material_lib
        self.current_material = None
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Material selection
        selection_group = QGroupBox("Material Selection")
        selection_layout = QHBoxLayout(selection_group)
        
        self.material_combo = QComboBox()
        self.material_combo.addItems(list(self.material_lib.materials.keys()))
        self.material_combo.currentTextChanged.connect(self.on_material_selected)
        
        self.new_btn = QPushButton("New")
        self.new_btn.clicked.connect(self.create_new_material)
        
        selection_layout.addWidget(QLabel("Material:"))
        selection_layout.addWidget(self.material_combo)
        selection_layout.addWidget(self.new_btn)
        
        layout.addWidget(selection_group)
        
        # Material properties
        props_group = QGroupBox("Material Properties")
        props_layout = QFormLayout(props_group)
        
        self.name_edit = QLineEdit()
        props_layout.addRow("Name:", self.name_edit)
        
        self.diffuse_btn = QPushButton("Diffuse Color")
        self.diffuse_btn.clicked.connect(self.set_diffuse_color)
        props_layout.addRow("Diffuse:", self.diffuse_btn)
        
        self.specular_btn = QPushButton("Specular Color")
        self.specular_btn.clicked.connect(self.set_specular_color)
        props_layout.addRow("Specular:", self.specular_btn)
        
        self.shininess_slider = QSlider(Qt.Horizontal)
        self.shininess_slider.setRange(0, 128)
        self.shininess_slider.setValue(32)
        props_layout.addRow("Shininess:", self.shininess_slider)
        
        self.texture_btn = QPushButton("Load Texture")
        self.texture_btn.clicked.connect(self.load_texture)
        props_layout.addRow("Texture:", self.texture_btn)
        
        layout.addWidget(props_group)
        
        # Actions
        self.save_btn = QPushButton("Save Material")
        self.save_btn.clicked.connect(self.save_material)
        
        self.delete_btn = QPushButton("Delete Material")
        self.delete_btn.clicked.connect(self.delete_material)
        
        layout.addWidget(self.save_btn)
        layout.addWidget(self.delete_btn)
    
    def on_material_selected(self, name):
        if name in self.material_lib.materials:
            self.current_material = self.material_lib.materials[name]
            self.update_ui()
    
    def update_ui(self):
        if self.current_material:
            self.name_edit.setText(self.current_material.name)
            self.shininess_slider.setValue(int(self.current_material.shininess))
    
    def set_diffuse_color(self):
        if self.current_material:
            color = QColorDialog.getColor()
            if color.isValid():
                self.current_material.diffuse_color = [
                    color.redF(), color.greenF(), color.blueF(), 1.0
                ]
    
    def set_specular_color(self):
        if self.current_material:
            color = QColorDialog.getColor()
            if color.isValid():
                self.current_material.specular_color = [
                    color.redF(), color.greenF(), color.blueF(), 1.0
                ]
    
    def load_texture(self):
        if self.current_material:
            path, _ = QFileDialog.getOpenFileName(
                self, "Open Texture", "", "Image Files (*.png *.jpg *.bmp *.tga)"
            )
            if path:
                print(f"Loading texture: {path}")
                # Здесь будет загрузка текстуры
    
    def create_new_material(self):
        from core.material import Material
        new_material = Material("New_Material")
        self.material_lib.materials[new_material.name] = new_material
        self.material_combo.addItem(new_material.name)
        self.material_combo.setCurrentText(new_material.name)
    
    def save_material(self):
        if self.current_material:
            self.current_material.name = self.name_edit.text()
            self.current_material.shininess = self.shininess_slider.value()
            # Обновляем комбобокс
            self.material_combo.clear()
            self.material_combo.addItems(list(self.material_lib.materials.keys()))
            self.material_combo.setCurrentText(self.current_material.name)
    
    def delete_material(self):
        if self.current_material and self.current_material.name != "Default":
            del self.material_lib.materials[self.current_material.name]
            self.current_material = None
            self.material_combo.clear()
            self.material_combo.addItems(list(self.material_lib.materials.keys()))