class Layer:
    def __init__(self, name, visible=True, lock=False):
        self.name = name
        self.visible = visible
        self.lock = lock
        self.objects = []

class LayerManager:
    def __init__(self):
        self.layers = []
        self.default_layer = Layer("Default")
        self.layers.append(self.default_layer)
        self.current_layer = self.default_layer
        
    def create_layer(self, name):
        """Создать новый слой"""
        if any(layer.name == name for layer in self.layers):
            return None
            
        layer = Layer(name)
        self.layers.append(layer)
        return layer
        
    def delete_layer(self, layer):
        """Удалить слой"""
        if layer == self.default_layer:
            return False
            
        if layer in self.layers:
            # Перемещаем объекты в default layer
            for obj in layer.objects:
                self.default_layer.objects.append(obj)
            self.layers.remove(layer)
            
            # Если удаляемый слой был текущим, переключаемся на default
            if self.current_layer == layer:
                self.current_layer = self.default_layer
                
            return True
        return False
        
    def move_object_to_layer(self, obj, layer):
        """Переместить объект в слой"""
        # Удаляем объект из всех слоев
        for l in self.layers:
            if obj in l.objects:
                l.objects.remove(obj)
        
        # Добавляем в целевой слой
        layer.objects.append(obj)
        
    def get_visible_objects(self):
        """Получить все видимые объекты"""
        visible_objects = []
        for layer in self.layers:
            if layer.visible:
                visible_objects.extend(layer.objects)
        return visible_objects
        
    def toggle_layer_visibility(self, layer):
        """Переключить видимость слоя"""
        if layer in self.layers:
            layer.visible = not layer.visible
            return True
        return False
        
    def toggle_layer_lock(self, layer):
        """Переключить блокировку слоя"""
        if layer in self.layers:
            layer.lock = not layer.lock
            return True
        return False
            
    def get_layer_by_name(self, name):
        """Найти слой по имени"""
        for layer in self.layers:
            if layer.name == name:
                return layer
        return None