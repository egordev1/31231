from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QPushButton, QSlider, QComboBox, QGroupBox
from PyQt5.QtCore import Qt

class InspectorPanel(QWidget):
    def __init__(self, scene, hierarchy):
        super().__init__()
        self.scene = scene
        self.hierarchy = hierarchy
        self.obj = None

        layout = QVBoxLayout(self)
        
        # Object info
        self.info_label = QLabel("No object selected")
        layout.addWidget(self.info_label)
        
        # Transform group
        transform_group = QGroupBox("Transform")
        transform_layout = QFormLayout(transform_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Object name")
        transform_layout.addRow("Name:", self.name_edit)
        
        self.pos_edits = []
        for i, axis in enumerate(["X", "Y", "Z"]):
            edit = QLineEdit("0.0")
            edit.setPlaceholderText(f"{axis} position")
            self.pos_edits.append(edit)
            transform_layout.addRow(f"Position {axis}:", edit)
        
        self.rot_sliders = []
        for i, axis in enumerate(["X", "Y", "Z"]):
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 360)
            slider.setValue(0)
            self.rot_sliders.append(slider)
            transform_layout.addRow(f"Rotation {axis}:", slider)
        
        self.scale_edits = []
        for i, axis in enumerate(["X", "Y", "Z"]):
            edit = QLineEdit("1.0")
            edit.setPlaceholderText(f"{axis} scale")
            self.scale_edits.append(edit)
            transform_layout.addRow(f"Scale {axis}:", edit)
        
        layout.addWidget(transform_group)
        
        # Properties group
        props_group = QGroupBox("Properties")
        props_layout = QFormLayout(props_group)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Cube", "Sphere", "Cylinder"])
        props_layout.addRow("Primitive Type:", self.type_combo)
        
        self.material_combo = QComboBox()
        self.material_combo.addItems(["Default", "Metal", "Plastic", "Rubber"])
        props_layout.addRow("Material:", self.material_combo)
        
        layout.addWidget(props_group)
        
        # Actions
        self.color_btn = QPushButton("Change Color")
        self.delete_btn = QPushButton("Delete Object")
        
        layout.addWidget(self.color_btn)
        layout.addWidget(self.delete_btn)
        
        # Connect signals
        self.name_edit.editingFinished.connect(self.rename_object)
        for edit in self.pos_edits:
            edit.editingFinished.connect(self.update_transform)
        for slider in self.rot_sliders:
            slider.valueChanged.connect(self.update_rotation)
        for edit in self.scale_edits:
            edit.editingFinished.connect(self.update_transform)
        
        self.type_combo.currentIndexChanged.connect(self.change_primitive)
        self.material_combo.currentIndexChanged.connect(self.change_material)
        self.color_btn.clicked.connect(self.change_color)
        self.delete_btn.clicked.connect(self.delete_object)

    def set_object(self, obj):
        self.obj = obj
        if obj:
            self.info_label.setText(f"Editing: {obj.name}")
            self.name_edit.setText(obj.name)
            self.type_combo.setCurrentIndex(obj.primitive_type)
            
            # Set material combo correctly
            materials = ["Default", "Metal", "Plastic", "Rubber"]
            if hasattr(obj, 'material_name') and obj.material_name in materials:
                self.material_combo.setCurrentIndex(materials.index(obj.material_name))
            else:
                self.material_combo.setCurrentIndex(0)
            
            # Set transform values
            for i in range(3):
                self.pos_edits[i].setText(f"{obj.position[i]:.2f}")
                self.rot_sliders[i].setValue(int(obj.rotation[i]))
                self.scale_edits[i].setText(f"{obj.scale[i]:.2f}")
            
            self.setEnabled(True)
        else:
            self.info_label.setText("No object selected")
            self.name_edit.clear()
            self.type_combo.setCurrentIndex(0)
            self.material_combo.setCurrentIndex(0)
            for i in range(3):
                self.pos_edits[i].clear()
                self.rot_sliders[i].setValue(0)
                self.scale_edits[i].setText("1.0")
            self.setEnabled(False)

    def rename_object(self):
        if self.obj:
            new_name = self.name_edit.text().strip()
            if new_name:
                self.obj.name = new_name
                self.hierarchy.refresh()

    def update_transform(self):
        if self.obj:
            try:
                # Update position
                new_position = []
                for edit in self.pos_edits:
                    try:
                        new_position.append(float(edit.text()))
                    except ValueError:
                        new_position.append(0.0)
                self.obj.position = new_position
                
                # Update scale
                new_scale = []
                for edit in self.scale_edits:
                    try:
                        new_scale.append(float(edit.text()))
                    except ValueError:
                        new_scale.append(1.0)
                self.obj.scale = new_scale
                
            except Exception as e:
                print(f"Error updating transform: {e}")

    def update_rotation(self):
        if self.obj:
            self.obj.rotation = [slider.value() for slider in self.rot_sliders]

    def change_primitive(self, index):
        if self.obj:
            self.obj.primitive_type = index

    def change_material(self, index):
        if self.obj:
            materials = ["Default", "Metal", "Plastic", "Rubber"]
            if index < len(materials):
                self.obj.material_name = materials[index]

    def change_color(self):
        if self.obj:
            from PyQt5.QtWidgets import QColorDialog
            color = QColorDialog.getColor()
            if color.isValid():
                self.obj.color = [color.redF(), color.greenF(), color.blueF()]

    def delete_object(self):
        if self.obj:
            self.scene.remove_object(self.obj)
            self.hierarchy.refresh()
            self.set_object(None)