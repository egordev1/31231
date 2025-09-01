class Event:
    def __init__(self, event_type, data=None):
        self.type = event_type
        self.data = data or {}
        self.handled = False

class EventManager:
    def __init__(self):
        self.listeners = {}
        
    def add_listener(self, event_type, callback):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
        
    def remove_listener(self, event_type, callback):
        if event_type in self.listeners:
            self.listeners[event_type].remove(callback)
            
    def dispatch(self, event):
        if event.type in self.listeners:
            for callback in self.listeners[event.type]:
                callback(event)
                
    def clear(self):
        self.listeners.clear()

# Common event types
class EventTypes:
    OBJECT_CREATED = "object_created"
    OBJECT_DESTROYED = "object_destroyed"
    COLLISION_START = "collision_start"
    COLLISION_END = "collision_end"
    SCENE_LOADED = "scene_loaded"
    SCENE_UNLOADED = "scene_unloaded"
    KEY_PRESSED = "key_pressed"
    MOUSE_CLICKED = "mouse_clicked"