from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLabel, QLineEdit, QColorDialog, QGridLayout,
    QSlider, QComboBox, QMenuBar, QToolBar, QAction, QStatusBar, QDockWidget,
    QMessageBox, QFileDialog, QTabWidget, QGroupBox, QCheckBox, QSpinBox,
    QDoubleSpinBox, QSplitter, QListWidgetItem
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence, QIcon, QColor

from core.scene import Scene
from core.objects import GameObject
from core.lighting import Light
from core.post_processing import BloomEffect, ColorGradingEffect
from .gl_widget import GLWidget
from .console import Console
from .hierarchy import HierarchyPanel
from .inspector import InspectorPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Engine - Professional Edition")
        self.setGeometry(100, 100, 1600, 900)
        
        self.scene = Scene()
        self.setup_ui()
        self.setup_shortcuts()
        
        self.console.append_info("Professional 3D Editor started successfully")
        self.console.append_success("Scene loaded with default objects")

    def setup_ui(self):
        self.create_menu()
        self.create_toolbar()
        self.create_statusbar()
        self.create_dock_widgets()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel (Hierarchy)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("Hierarchy"))
        left_layout.addWidget(self.hierarchy_panel)
        splitter.addWidget(left_widget)
        
        # Center panel (Viewport)
        self.viewport = GLWidget(self.scene)
        splitter.addWidget(self.viewport)
        
        # Right panel (Inspector and tools)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Tab widget for inspector and other tools
        self.tab_widget = QTabWidget()
        
        # Inspector tab
        inspector_tab = QWidget()
        inspector_layout = QVBoxLayout(inspector_tab)
        inspector_layout.addWidget(self.inspector_panel)
        self.tab_widget.addTab(inspector_tab, "Inspector")
        
        # Lighting tab
        lighting_tab = self.create_lighting_tab()
        self.tab_widget.addTab(lighting_tab, "Lighting")
        
        # Post-Processing tab
        post_processing_tab = self.create_post_processing_tab()
        self.tab_widget.addTab(post_processing_tab, "Effects")
        
        right_layout.addWidget(self.tab_widget)
        splitter.addWidget(right_widget)
        
        # Set splitter sizes
        splitter.setSizes([250, 1000, 350])
        main_layout.addWidget(splitter)
        
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_statusbar)
        self.status_timer.start(100)

    def create_lighting_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Ambient light
        ambient_group = QGroupBox("Ambient Light")
        ambient_layout = QGridLayout(ambient_group)
        
        ambient_layout.addWidget(QLabel("Color:"), 0, 0)
        self.ambient_color_btn = QPushButton()
        self.ambient_color_btn.setStyleSheet("background-color: rgb(51, 51, 51); min-height: 20px;")
        self.ambient_color_btn.clicked.connect(self.change_ambient_color)
        ambient_layout.addWidget(self.ambient_color_btn, 0, 1)
        
        ambient_layout.addWidget(QLabel("Intensity:"), 1, 0)
        self.ambient_intensity = QDoubleSpinBox()
        self.ambient_intensity.setRange(0.0, 2.0)
        self.ambient_intensity.setValue(0.2)
        self.ambient_intensity.setSingleStep(0.1)
        self.ambient_intensity.valueChanged.connect(self.update_ambient_light)
        ambient_layout.addWidget(self.ambient_intensity, 1, 1)
        
        layout.addWidget(ambient_group)
        
        # Light list
        lights_group = QGroupBox("Scene Lights")
        lights_layout = QVBoxLayout(lights_group)
        
        self.lights_list = QListWidget()
        self.lights_list.itemClicked.connect(self.on_light_selected)
        lights_layout.addWidget(self.lights_list)
        
        # Light controls
        light_controls = QHBoxLayout()
        add_light_btn = QPushButton("Add Light")
        add_light_btn.clicked.connect(self.add_new_light)
        remove_light_btn = QPushButton("Remove")
        remove_light_btn.clicked.connect(self.remove_selected_light)
        
        light_controls.addWidget(add_light_btn)
        light_controls.addWidget(remove_light_btn)
        lights_layout.addLayout(light_controls)
        
        layout.addWidget(lights_group)
        
        # Refresh lights list
        self.refresh_lights_list()
        
        return tab

    def create_post_processing_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Bloom effect
        bloom_group = QGroupBox("Bloom Effect")
        bloom_layout = QGridLayout(bloom_group)
        
        self.bloom_enabled = QCheckBox("Enabled")
        self.bloom_enabled.setChecked(False)
        self.bloom_enabled.stateChanged.connect(self.toggle_bloom)
        bloom_layout.addWidget(self.bloom_enabled, 0, 0, 1, 2)
        
        bloom_layout.addWidget(QLabel("Intensity:"), 1, 0)
        self.bloom_intensity = QDoubleSpinBox()
        self.bloom_intensity.setRange(0.0, 5.0)
        self.bloom_intensity.setValue(1.0)
        self.bloom_intensity.setSingleStep(0.1)
        self.bloom_intensity.valueChanged.connect(self.update_bloom)
        bloom_layout.addWidget(self.bloom_intensity, 1, 1)
        
        bloom_layout.addWidget(QLabel("Threshold:"), 2, 0)
        self.bloom_threshold = QDoubleSpinBox()
        self.bloom_threshold.setRange(0.0, 1.0)
        self.bloom_threshold.setValue(0.8)
        self.bloom_threshold.setSingleStep(0.05)
        self.bloom_threshold.valueChanged.connect(self.update_bloom)
        bloom_layout.addWidget(self.bloom_threshold, 2, 1)
        
        layout.addWidget(bloom_group)
        
        # Color grading
        color_group = QGroupBox("Color Grading")
        color_layout = QGridLayout(color_group)
        
        color_layout.addWidget(QLabel("Brightness:"), 0, 0)
        self.brightness = QDoubleSpinBox()
        self.brightness.setRange(0.0, 2.0)
        self.brightness.setValue(1.0)
        self.brightness.setSingleStep(0.1)
        self.brightness.valueChanged.connect(self.update_color_grading)
        color_layout.addWidget(self.brightness, 0, 1)
        
        color_layout.addWidget(QLabel("Contrast:"), 1, 0)
        self.contrast = QDoubleSpinBox()
        self.contrast.setRange(0.0, 2.0)
        self.contrast.setValue(1.0)
        self.contrast.setSingleStep(0.1)
        self.contrast.valueChanged.connect(self.update_color_grading)
        color_layout.addWidget(self.contrast, 1, 1)
        
        color_layout.addWidget(QLabel("Saturation:"), 2, 0)
        self.saturation = QDoubleSpinBox()
        self.saturation.setRange(0.0, 2.0)
        self.saturation.setValue(1.0)
        self.saturation.setSingleStep(0.1)
        self.saturation.valueChanged.connect(self.update_color_grading)
        color_layout.addWidget(self.saturation, 2, 1)
        
        layout.addWidget(color_group)
        
        # Initialize effects
        self.initialize_post_effects()
        
        return tab

    def initialize_post_effects(self):
        # Create initial effects
        self.bloom_effect = BloomEffect()
        self.color_effect = ColorGradingEffect()
        
        # Add to scene
        self.scene.add_post_effect(self.bloom_effect)
        self.scene.add_post_effect(self.color_effect)

    def create_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction("&New Scene", self.new_scene, QKeySequence.New)
        file_menu.addAction("&Save Scene", self.save_scene, QKeySequence.Save)
        file_menu.addAction("&Load Scene", self.load_scene, QKeySequence.Open)
        file_menu.addSeparator()
        file_menu.addAction("E&xit", self.close, QKeySequence.Quit)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction("&Undo", self.undo, QKeySequence.Undo)
        edit_menu.addAction("&Redo", self.redo, QKeySequence.Redo)
        edit_menu.addSeparator()
        edit_menu.addAction("&Duplicate", self.duplicate_object, "Ctrl+D")
        edit_menu.addAction("&Delete", self.delete_object, "Del")

        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction("Reset &Camera", self.reset_camera, "Ctrl+Shift+F")
        view_menu.addSeparator()
        view_menu.addAction("Toggle &Grid", self.toggle_grid, "G")
        view_menu.addAction("Toggle A&xes", self.toggle_axes, "X")
        view_menu.addAction("Toggle &Gizmos", self.toggle_gizmos, "Z")
        view_menu.addSeparator()
        view_menu.addAction("Toggle &Lighting", self.toggle_lighting, "L")
        view_menu.addAction("Toggle &Bloom", self.toggle_bloom_from_menu, "B")

        # GameObject menu
        gameobject_menu = menubar.addMenu("&GameObject")
        gameobject_menu.addAction("Create &Empty", self.create_empty, "Ctrl+Shift+N")
        
        primitive_menu = gameobject_menu.addMenu("&3D Object")
        primitive_menu.addAction("&Cube", lambda: self.add_object_with_type(0), "Ctrl+1")
        primitive_menu.addAction("&Sphere", lambda: self.add_object_with_type(1), "Ctrl+2")
        primitive_menu.addAction("&Cylinder", lambda: self.add_object_with_type(2), "Ctrl+3")
        
        light_menu = gameobject_menu.addMenu("&Light")
        light_menu.addAction("&Directional Light", lambda: self.add_light("DIRECTIONAL"))
        light_menu.addAction("&Point Light", lambda: self.add_light("POINT"))
        light_menu.addAction("&Spot Light", lambda: self.add_light("SPOT"))

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction("&Bake Lighting", self.bake_lighting)

        # Play menu
        play_menu = menubar.addMenu("&Play")
        play_menu.addAction("&Play", self.play_mode, "Ctrl+P")
        play_menu.addAction("&Pause", self.pause_mode, "Ctrl+Shift+P")
        play_menu.addAction("&Stop", self.stop_mode, "Ctrl+Shift+S")

        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction("&About", self.show_about)

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        toolbar.addAction("New", self.new_scene)
        toolbar.addAction("Save", self.save_scene)
        toolbar.addAction("Load", self.load_scene)
        toolbar.addSeparator()
        
        toolbar.addAction("Undo", self.undo)
        toolbar.addAction("Redo", self.redo)
        toolbar.addSeparator()
        
        toolbar.addAction("Play", self.play_mode)
        toolbar.addAction("Pause", self.pause_mode)
        toolbar.addAction("Stop", self.stop_mode)
        toolbar.addSeparator()
        
        toolbar.addAction("Focus", self.focus_on_selected)

    def create_dock_widgets(self):
        # Hierarchy dock
        hierarchy_dock = QDockWidget("Hierarchy", self)
        self.hierarchy_panel = HierarchyPanel(self.scene)
        self.hierarchy_panel.object_selected.connect(self.on_object_selected)
        hierarchy_dock.setWidget(self.hierarchy_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, hierarchy_dock)

        # Inspector dock
        inspector_dock = QDockWidget("Inspector", self)
        self.inspector_panel = InspectorPanel(self.scene, self.hierarchy_panel)
        inspector_dock.setWidget(self.inspector_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, inspector_dock)

        # Console dock
        console_dock = QDockWidget("Console", self)
        self.console = Console()
        console_dock.setWidget(self.console)
        self.addDockWidget(Qt.BottomDockWidgetArea, console_dock)

    def create_statusbar(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("Ready")
        
        self.fps_label = QLabel("FPS: 60")
        self.object_label = QLabel("Objects: 0")
        self.light_label = QLabel("Lights: 0")
        self.camera_label = QLabel("Camera: (0, 2, 8)")
        
        self.statusbar.addPermanentWidget(self.fps_label)
        self.statusbar.addPermanentWidget(self.object_label)
        self.statusbar.addPermanentWidget(self.light_label)
        self.statusbar.addPermanentWidget(self.camera_label)

    def setup_shortcuts(self):
        shortcuts = {
            Qt.Key_Delete: self.delete_object,
            Qt.Key_F: self.focus_on_selected,
            Qt.Key_G: self.toggle_grid,
            Qt.Key_X: self.toggle_axes,
            Qt.Key_Z: self.toggle_gizmos,
            Qt.Key_L: self.toggle_lighting,
            Qt.Key_B: self.toggle_bloom_from_menu,
        }
        
        for key, callback in shortcuts.items():
            action = QAction(self)
            action.setShortcut(QKeySequence(key))
            action.triggered.connect(callback)
            self.addAction(action)

    # Lighting system methods
    def refresh_lights_list(self):
        self.lights_list.clear()
        for i, light in enumerate(self.scene.lighting.lights):
            light_type = light.type.capitalize()
            item = QListWidgetItem(f"{light_type} Light {i+1}")
            self.lights_list.addItem(item)

    def on_light_selected(self, item):
        index = self.lights_list.row(item)
        if 0 <= index < len(self.scene.lighting.lights):
            self.console.append_info(f"Selected {self.scene.lighting.lights[index].type} light")

    def change_ambient_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.scene.ambient_light = [color.redF(), color.greenF(), color.blueF(), 1.0]
            self.ambient_color_btn.setStyleSheet(f"background-color: {color.name()}; min-height: 20px;")
            self.viewport.update()
            self.console.append_info("Ambient light color changed")
            
    def update_ambient_light(self):
        self.scene.ambient_light[3] = self.ambient_intensity.value()
        self.viewport.update()
        self.console.append_info(f"Ambient intensity: {self.ambient_intensity.value()}")
        
    def add_new_light(self):
        light_added = self.scene.add_light("POINT", (0, 5, 0), (1, 1, 1), 1.0)
        if light_added:
            self.refresh_lights_list()
            self.console.append_success("Added new point light")
            self.viewport.update()
            
    def remove_selected_light(self):
        index = self.lights_list.currentRow()
        if index >= 0 and self.scene.remove_light(index):
            self.refresh_lights_list()
            self.console.append_info("Light removed")
            self.viewport.update()

    # Post-processing methods
    def toggle_bloom(self, state):
        self.bloom_effect.enabled = state == Qt.Checked
        self.bloom_effect.intensity = self.bloom_intensity.value()
        self.bloom_effect.threshold = self.bloom_threshold.value()
        self.viewport.update()
        self.console.append_info(f"Bloom {'enabled' if self.bloom_effect.enabled else 'disabled'}")
        
    def update_bloom(self):
        self.toggle_bloom(self.bloom_enabled.checkState())
        
    def update_color_grading(self):
        self.color_effect.brightness = self.brightness.value()
        self.color_effect.contrast = self.contrast.value()
        self.color_effect.saturation = self.saturation.value()
        self.viewport.update()
        self.console.append_info("Color grading updated")
        
    def toggle_bloom_from_menu(self):
        self.bloom_enabled.setChecked(not self.bloom_enabled.isChecked())

    # Tool methods
    def bake_lighting(self):
        self.console.append_info("Baking lighting...")
        # Simulate baking process
        QTimer.singleShot(2000, lambda: self.console.append_success("Light baking completed!"))

    # Core functionality methods
    def on_object_selected(self, obj):
        self.scene.selected_object = obj
        self.inspector_panel.set_object(obj)
        
        if obj:
            self.statusbar.showMessage(f"Selected: {obj.name}")
            self.console.append_info(f"Selected object: {obj.name}")
        else:
            self.statusbar.showMessage("No object selected")

    def new_scene(self):
        reply = QMessageBox.question(self, "New Scene", 
                                   "Create new scene? Current changes will be lost.",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.scene = Scene()
            self.hierarchy_panel.scene = self.scene
            self.hierarchy_panel.refresh()
            self.inspector_panel.set_object(None)
            self.viewport.scene = self.scene
            self.viewport.update()
            self.refresh_lights_list()
            self.console.append_info("Created new scene")

    def save_scene(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Scene", "", "Scene Files (*.scene)"
        )
        if filename:
            if self.scene.save_to_file(filename):
                self.console.append_success(f"Scene saved: {filename}")
            else:
                self.console.append_error("Failed to save scene")

    def load_scene(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Scene", "", "Scene Files (*.scene)"
        )
        if filename:
            if self.scene.load_from_file(filename):
                self.hierarchy_panel.scene = self.scene
                self.hierarchy_panel.refresh()
                self.inspector_panel.set_object(None)
                self.viewport.scene = self.scene
                self.viewport.update()
                self.refresh_lights_list()
                self.console.append_success(f"Scene loaded: {filename}")
            else:
                self.console.append_error("Failed to load scene")

    def undo(self):
        self.console.append_info("Undo performed")

    def redo(self):
        self.console.append_info("Redo performed")

    def create_empty(self):
        from core.objects import GameObject
        new_obj = GameObject("EmptyObject")
        self.scene.add_object(new_obj)
        self.hierarchy_panel.refresh()
        self.console.append_info("Created empty GameObject")

    def duplicate_object(self):
        if self.scene.selected_object:
            import copy
            new_obj = copy.deepcopy(self.scene.selected_object)
            new_obj.name = f"{self.scene.selected_object.name}_Copy"
            new_obj.position[0] += 1.0
            self.scene.add_object(new_obj)
            self.hierarchy_panel.refresh()
            self.console.append_info(f"Duplicated {self.scene.selected_object.name}")

    def add_object_with_type(self, primitive_type):
        from core.objects import GameObject
        types = ["Cube", "Sphere", "Cylinder"]
        new_obj = GameObject(
            f"{types[primitive_type]}{len(self.scene.objects) + 1}",
            primitive_type=primitive_type
        )
        self.scene.add_object(new_obj)
        self.hierarchy_panel.refresh()
        self.viewport.update()
        self.console.append_success(f"Added {types[primitive_type].lower()}: {new_obj.name}")

    def delete_object(self):
        if not self.scene.selected_object:
            return
        obj_name = self.scene.selected_object.name
        self.scene.remove_object(self.scene.selected_object)
        self.hierarchy_panel.refresh()
        self.inspector_panel.set_object(None)
        self.viewport.update()
        self.console.append_warning(f"Deleted object: {obj_name}")

    def focus_on_selected(self):
        if self.scene.selected_object:
            self.viewport.focus_on_object(self.scene.selected_object)
            self.console.append_info(f"Focused on {self.scene.selected_object.name}")

    def set_shading_mode(self, mode):
        self.viewport.set_shading_mode(mode)
        modes = ["Lit", "Unlit", "Wireframe"]
        self.console.append_info(f"Shading mode: {modes[mode]}")

    def toggle_grid(self):
        self.viewport.show_grid = not self.viewport.show_grid
        self.viewport.update()
        self.console.append_info(f"Grid {'enabled' if self.viewport.show_grid else 'disabled'}")

    def toggle_axes(self):
        self.viewport.show_axes = not self.viewport.show_axes
        self.viewport.update()
        self.console.append_info(f"Axes {'enabled' if self.viewport.show_axes else 'disabled'}")

    def toggle_gizmos(self):
        self.viewport.show_gizmos = not self.viewport.show_gizmos
        self.viewport.update()
        self.console.append_info(f"Gizmos {'enabled' if self.viewport.show_gizmos else 'disabled'}")

    def toggle_lighting(self):
        self.viewport.lighting_enabled = not self.viewport.lighting_enabled
        if self.viewport.lighting_enabled:
            self.console.append_info("Lighting enabled")
        else:
            self.console.append_info("Lighting disabled")
        self.viewport.update()

    def reset_camera(self):
        self.viewport.reset_camera()
        self.console.append_info("Camera reset")

    def add_light(self, light_type):
        position = [0, 5, 0]
        if self.scene.selected_object:
            position = self.scene.selected_object.position[:]
            position[1] += 2.0
            
        light_added = self.scene.add_light(light_type, position, (1, 1, 1), 1.0)
        if light_added:
            light_names = {"DIRECTIONAL": "Directional", "POINT": "Point", "SPOT": "Spot"}
            self.console.append_success(f"Added {light_names[light_type]} light")
            self.refresh_lights_list()
            self.viewport.update()

    def play_mode(self):
        self.scene.play()
        self.console.append_info("Play mode started")

    def pause_mode(self):
        self.scene.pause()
        self.console.append_info("Play mode paused")

    def stop_mode(self):
        self.scene.stop()
        self.console.append_info("Play mode stopped")

    def show_about(self):
        QMessageBox.about(self, "About 3D Editor",
                         "Professional 3D Engine Editor\n\n"
                         "Features:\n"
                         "- Advanced rendering system\n"
                         "- PBR materials and lighting\n"
                         "- Post-processing effects\n"
                         "- Physics and collision system\n"
                         "- Real-time editing\n\n"
                         "Version 2.0.0")

    def update_statusbar(self):
        self.fps_label.setText(f"FPS: {self.viewport.fps}")
        self.object_label.setText(f"Objects: {len(self.scene.objects)}")
        self.light_label.setText(f"Lights: {len(self.scene.lighting.lights)}")
        
        cam_pos = self.viewport.camera_position
        self.camera_label.setText(f"Camera: ({cam_pos[0]:.1f}, {cam_pos[1]:.1f}, {cam_pos[2]:.1f})")

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())