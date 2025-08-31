import os
import json
from datetime import datetime

class AssetManager:
    def __init__(self, assets_directory="assets"):
        self.assets_directory = assets_directory
        self.meshes = {}
        self.textures = {}
        self.materials = {}
        self.prefabs = {}
        self.scripts = {}
        
        self.asset_database = {}
        self.load_asset_database()
        
    def load_asset_database(self):
        db_path = os.path.join(self.assets_directory, "asset_database.json")
        if os.path.exists(db_path):
            try:
                with open(db_path, 'r') as f:
                    self.asset_database = json.load(f)
            except:
                self.asset_database = {}
                
    def save_asset_database(self):
        db_path = os.path.join(self.assets_directory, "asset_database.json")
        with open(db_path, 'w') as f:
            json.dump(self.asset_database, f, indent=2)
                
    def import_asset(self, asset_path, asset_type):
        """Import asset and add to database"""
        asset_id = self._generate_asset_id()
        asset_name = os.path.basename(asset_path)
        
        asset_info = {
            'id': asset_id,
            'name': asset_name,
            'path': asset_path,
            'type': asset_type,
            'import_date': datetime.now().isoformat(),
            'file_size': os.path.getsize(asset_path),
            'dependencies': []
        }
        
        self.asset_database[asset_id] = asset_info
        self.save_asset_database()
        
        return asset_id
        
    def get_asset(self, asset_id):
        return self.asset_database.get(asset_id)
        
    def find_assets_by_type(self, asset_type):
        return [asset for asset in self.asset_database.values() if asset['type'] == asset_type]
        
    def _generate_asset_id(self):
        return f"asset_{len(self.asset_database) + 1:08d}"