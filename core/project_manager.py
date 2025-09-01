import json
import os
from datetime import datetime

class Project:
    def __init__(self, name="NewProject"):
        self.name = name
        self.version = "1.0.0"
        self.description = ""
        self.author = ""
        self.created_date = datetime.now().isoformat()
        self.last_modified = datetime.now().isoformat()
        self.scenes = []
        self.assets = []
        self.settings = {
            'render_quality': 'High',
            'physics_quality': 'Medium',
            'audio_quality': 'High'
        }
        
    def create_project(self, directory):
        project_path = os.path.join(directory, self.name)
        os.makedirs(project_path, exist_ok=True)
        
        # Create project structure
        folders = [
            'Assets',
            'Scenes', 
            'Scripts',
            'Textures',
            'Models',
            'Audio',
            'Prefabs'
        ]
        
        for folder in folders:
            os.makedirs(os.path.join(project_path, folder), exist_ok=True)
            
        # Save project file
        self.save(os.path.join(project_path, f"{self.name}.project"))
        
    def save(self, path):
        project_data = {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'created_date': self.created_date,
            'last_modified': datetime.now().isoformat(),
            'scenes': self.scenes,
            'assets': self.assets,
            'settings': self.settings
        }
        
        with open(path, 'w') as f:
            json.dump(project_data, f, indent=2)
            
    def load(self, path):
        try:
            with open(path, 'r') as f:
                project_data = json.load(f)
                
            self.name = project_data.get('name', 'NewProject')
            self.version = project_data.get('version', '1.0.0')
            self.description = project_data.get('description', '')
            self.author = project_data.get('author', '')
            self.created_date = project_data.get('created_date', '')
            self.last_modified = project_data.get('last_modified', '')
            self.scenes = project_data.get('scenes', [])
            self.assets = project_data.get('assets', [])
            self.settings = project_data.get('settings', {})
            
            return True
        except:
            return False

class ProjectManager:
    def __init__(self):
        self.current_project = None
        self.recent_projects = []
        
    def create_new_project(self, name, directory):
        project = Project(name)
        project.create_project(directory)
        self.current_project = project
        self.recent_projects.append(project)
        return project
        
    def load_project(self, path):
        project = Project()
        if project.load(path):
            self.current_project = project
            self.recent_projects.append(project)
            return project
        return None
        
    def save_current_project(self):
        if self.current_project:
            self.current_project.save()
            return True
        return False