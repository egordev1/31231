import importlib
import inspect
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal

class Plugin:
    """Базовый класс для всех плагинов"""
    def __init__(self):
        self.name = "Unnamed Plugin"
        self.version = "1.0.0"
        self.author = "Unknown"
        self.description = "No description"
        self.enabled = True
        
    def initialize(self, app):
        """Инициализация плагина"""
        pass
        
    def shutdown(self):
        """Завершение работы плагина"""
        pass
        
    def update(self, delta_time: float):
        """Обновление плагина (вызывается каждый кадр)"""
        pass

class PluginManager:
    """Менеджер плагинов"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.plugins = {}
            cls._instance.plugin_order = []
        return cls._instance
    
    def load_plugin(self, plugin_path: str) -> bool:
        """Загрузка плагина из файла"""
        try:
            spec = importlib.util.spec_from_file_location("plugin_module", plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Ищем классы-наследники Plugin
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, Plugin) and 
                    obj != Plugin):
                    plugin_instance = obj()
                    self.plugins[plugin_instance.name] = plugin_instance
                    self.plugin_order.append(plugin_instance.name)
                    return True
                    
        except Exception as e:
            print(f"Error loading plugin {plugin_path}: {e}")
        return False
    
    def load_plugins_from_directory(self, directory: str):
        """Загрузка всех плагинов из директории"""
        plugin_dir = Path(directory)
        if not plugin_dir.exists():
            plugin_dir.mkdir(parents=True)
            
        for file_path in plugin_dir.glob("*.py"):
            self.load_plugin(str(file_path))
    
    def initialize_plugins(self, app):
        """Инициализация всех плагинов"""
        for plugin_name in self.plugin_order:
            plugin = self.plugins[plugin_name]
            if plugin.enabled:
                try:
                    plugin.initialize(app)
                    print(f"Initialized plugin: {plugin_name}")
                except Exception as e:
                    print(f"Error initializing plugin {plugin_name}: {e}")
    
    def shutdown_plugins(self):
        """Завершение работы всех плагинов"""
        for plugin_name in reversed(self.plugin_order):
            plugin = self.plugins[plugin_name]
            if plugin.enabled:
                try:
                    plugin.shutdown()
                except Exception as e:
                    print(f"Error shutting down plugin {plugin_name}: {e}")
    
    def update_plugins(self, delta_time: float):
        """Обновление всех плагинов"""
        for plugin_name in self.plugin_order:
            plugin = self.plugins[plugin_name]
            if plugin.enabled:
                try:
                    plugin.update(delta_time)
                except Exception as e:
                    print(f"Error updating plugin {plugin_name}: {e}")
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Получить плагин по имени"""
        return self.plugins.get(name)
    
    def enable_plugin(self, name: str):
        """Включить плагин"""
        if name in self.plugins:
            self.plugins[name].enabled = True
    
    def disable_plugin(self, name: str):
        """Выключить плагин"""
        if name in self.plugins:
            self.plugins[name].enabled = False

class PluginManagerUI(QWidget):
    """UI для управления плагинами"""
    plugin_toggled = pyqtSignal(str, bool)
    
    def __init__(self, plugin_manager: PluginManager):
        super().__init__()
        self.plugin_manager = plugin_manager
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Plugin Manager")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.plugin_list = QListWidget()
        layout.addWidget(self.plugin_list)
        
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_list)
        
        self.enable_btn = QPushButton("Enable")
        self.enable_btn.clicked.connect(self.enable_selected)
        
        self.disable_btn = QPushButton("Disable")
        self.disable_btn.clicked.connect(self.disable_selected)
        
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.enable_btn)
        button_layout.addWidget(self.disable_btn)
        
        layout.addLayout(button_layout)
        
        self.refresh_list()
    
    def refresh_list(self):
        """Обновить список плагинов"""
        self.plugin_list.clear()
        for plugin_name in self.plugin_manager.plugin_order:
            plugin = self.plugin_manager.plugins[plugin_name]
            item_text = f"{plugin_name} ({'Enabled' if plugin.enabled else 'Disabled'})"
            self.plugin_list.addItem(item_text)
    
    def enable_selected(self):
        """Включить выбранный плагин"""
        current_row = self.plugin_list.currentRow()
        if current_row >= 0:
            plugin_name = self.plugin_manager.plugin_order[current_row]
            self.plugin_manager.enable_plugin(plugin_name)
            self.refresh_list()
            self.plugin_toggled.emit(plugin_name, True)
    
    def disable_selected(self):
        """Выключить выбранный плагин"""
        current_row = self.plugin_list.currentRow()
        if current_row >= 0:
            plugin_name = self.plugin_manager.plugin_order[current_row]
            self.plugin_manager.disable_plugin(plugin_name)
            self.refresh_list()
            self.plugin_toggled.emit(plugin_name, False)