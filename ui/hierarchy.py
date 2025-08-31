from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import pyqtSignal

class HierarchyPanel(QWidget):
    object_selected = pyqtSignal(object)

    def __init__(self, scene):
        super().__init__()
        self.scene = scene
        
        layout = QVBoxLayout(self)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.clear_btn = QPushButton("Clear")
        
        self.refresh_btn.clicked.connect(self.refresh)
        self.clear_btn.clicked.connect(self.clear_selection)
        
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.clear_btn)
        layout.addLayout(button_layout)
        
        # Object list
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)
        
        self.refresh()

    def refresh(self):
        self.list_widget.clear()
        for obj in self.scene.objects:
            self.list_widget.addItem(obj.name)

    def on_item_clicked(self, item):
        name = item.text()
        obj = self.scene.find_object(name)
        if obj:
            self.scene.selected_object = obj
            self.object_selected.emit(obj)

    def clear_selection(self):
        self.scene.selected_object = None
        self.list_widget.clearSelection()
        self.object_selected.emit(None)

    def add_object(self, obj):
        self.scene.add_object(obj)
        self.refresh()
        self.object_selected.emit(obj)