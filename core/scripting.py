import inspect
import types
import os

class ScriptComponent:
    def __init__(self, script_path=None):
        self.script_path = script_path
        self.script_instance = None
        self.enabled = True
        
    def load_script(self, script_path):
        try:
            if not os.path.exists(script_path):
                print(f"Script file not found: {script_path}")
                return False
                
            with open(script_path, 'r', encoding='utf-8') as f:
                script_code = f.read()
            
            # Create module from script code
            module = types.ModuleType("script_module")
            exec(script_code, module.__dict__)
            
            # Find script class (should be named 'Script')
            if hasattr(module, 'Script'):
                self.script_instance = module.Script()
                self.script_path = script_path
                
                # Inject parent object reference
                if hasattr(self.script_instance, 'set_parent'):
                    self.script_instance.set_parent(self)
                    
                return True
            else:
                print(f"Script class not found in {script_path}")
                
        except Exception as e:
            print(f"Error loading script {script_path}: {e}")
            import traceback
            traceback.print_exc()
        return False
    
    def call_method(self, method_name, *args):
        if self.script_instance and hasattr(self.script_instance, method_name):
            method = getattr(self.script_instance, method_name)
            if callable(method):
                try:
                    return method(*args)
                except Exception as e:
                    print(f"Error calling {method_name}: {e}")
        return None

class ScriptManager:
    def __init__(self):
        self.scripts = {}
        self.globals = {}
        
    def register_script(self, name, script_class):
        self.scripts[name] = script_class
        
    def create_script_instance(self, name):
        if name in self.scripts:
            return self.scripts[name]()
        return None
        
    def add_global_variable(self, name, value):
        self.globals[name] = value
        
    def get_global_variable(self, name):
        return self.globals.get(name)

# Base script template
class ScriptTemplate:
    def __init__(self):
        self.parent = None
        self.enabled = True
        
    def set_parent(self, parent):
        self.parent = parent
        
    def start(self):
        """Called when the script is first initialized"""
        pass
        
    def update(self, delta_time):
        """Called every frame"""
        pass
        
    def on_collision_enter(self, other_object):
        """Called when collision starts"""
        pass
        
    def on_collision_exit(self, other_object):
        """Called when collision ends"""
        pass