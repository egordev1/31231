import json
import os
import shutil
from datetime import datetime

class Project:
    def __init__(self, name="NewProject"):
        self.name = name
        self.path = ""
        self.created = datetime.now()
        self.modified = datetime.now()
        self.scenes = []
        self.last_scene = ""
        self.settings = {
            "render_quality": "High",
            "physics_quality": "Medium", 
            "lighting_quality": "High",
            "texture_quality": "High",
            "shadow_quality": "Medium",
            "anti_aliasing": "MSAA4x"
        }
        self.recent_scenes = []
    
    def to_dict(self):
        """Конвертировать проект в словарь"""
        return {
            "name": self.name,
            "created": self.created.isoformat(),
            "modified": self.modified.isoformat(),
            "scenes": self.scenes,
            "last_scene": self.last_scene,
            "recent_scenes": self.recent_scenes,
            "settings": self.settings
        }
    
    def from_dict(self, data):
        """Загрузить проект из словаря"""
        self.name = data.get("name", "NewProject")
        self.created = datetime.fromisoformat(data.get("created", datetime.now().isoformat()))
        self.modified = datetime.fromisoformat(data.get("modified", datetime.now().isoformat()))
        self.scenes = data.get("scenes", [])
        self.last_scene = data.get("last_scene", "")
        self.recent_scenes = data.get("recent_scenes", [])
        self.settings = data.get("settings", {})
    
    def save(self, path=None):
        """Сохранить проект"""
        if path:
            self.path = path
            
        if not self.path:
            return False
            
        self.modified = datetime.now()
        project_data = self.to_dict()
        
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving project: {e}")
            return False
    
    def load(self, path):
        """Загрузить проект"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            self.from_dict(project_data)
            self.path = path
            return True
        except Exception as e:
            print(f"Error loading project: {e}")
            return False
    
    def add_scene(self, scene_path):
        """Добавить сцену в проект"""
        if scene_path not in self.scenes:
            self.scenes.append(scene_path)
            
        if scene_path in self.recent_scenes:
            self.recent_scenes.remove(scene_path)
            
        self.recent_scenes.insert(0, scene_path)
        self.recent_scenes = self.recent_scenes[:10]  # Keep only 10 recent
        
        self.last_scene = scene_path
        
    def get_project_folder(self):
        """Получить папку проекта"""
        if self.path:
            return os.path.dirname(self.path)
        return ""

class ProjectManager:
    def __init__(self):
        self.current_project = None
        self.recent_projects = []
        self.max_recent_projects = 10
        
    def create_project(self, name, directory):
        """Создать новый проект"""
        project_path = os.path.join(directory, f"{name}.project")
        
        if os.path.exists(project_path):
            return False, "Project already exists"
            
        # Создаем структуру папок
        folders = ["Assets", "Scenes", "Scripts", "Textures", "Models", "Materials", "Prefabs"]
        for folder in folders:
            folder_path = os.path.join(directory, folder)
            os.makedirs(folder_path, exist_ok=True)
        
        # Создаем проект
        project = Project(name)
        project.path = project_path
        
        if project.save():
            self.current_project = project
            self._add_to_recent(project_path)
            return True, "Project created successfully"
        
        return False, "Failed to create project"
    
    def load_project(self, path):
        """Загрузить проект"""
        if not os.path.exists(path):
            return False, "Project file not found"
            
        project = Project()
        if project.load(path):
            self.current_project = project
            self._add_to_recent(path)
            return True, "Project loaded successfully"
            
        return False, "Failed to load project"
    
    def save_current_project(self):
        """Сохранить текущий проект"""
        if self.current_project:
            return self.current_project.save()
        return False
    
    def close_project(self):
        """Закрыть текущий проект"""
        self.current_project = None
    
    def _add_to_recent(self, path):
        """Добавить проект в список недавних"""
        if path in self.recent_projects:
            self.recent_projects.remove(path)
            
        self.recent_projects.insert(0, path)
        self.recent_projects = self.recent_projects[:self.max_recent_projects]
        
        # Сохраняем список недавних проектов
        self._save_recent_list()
    
    def _save_recent_list(self):
        """Сохранить список недавних проектов"""
        recent_file = os.path.join(os.path.expanduser("~"), ".3d_engine_recent")
        try:
            with open(recent_file, 'w', encoding='utf-8') as f:
                json.dump(self.recent_projects, f, indent=2)
        except:
            pass
    
    def load_recent_list(self):
        """Загрузить список недавних проектов"""
        recent_file = os.path.join(os.path.expanduser("~"), ".3d_engine_recent")
        if os.path.exists(recent_file):
            try:
                with open(recent_file, 'r', encoding='utf-8') as f:
                    self.recent_projects = json.load(f)
            except:
                self.recent_projects = []
    
    def get_recent_projects(self):
        """Получить список недавних проектов"""
        # Фильтруем только существующие проекты
        return [p for p in self.recent_projects if os.path.exists(p)]