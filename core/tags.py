class TagManager:
    def __init__(self):
        self.tags = ["Untagged", "Player", "Enemy", "Environment", "UI", "Light", "Camera", "Trigger", "Static", "Dynamic"]
        self.object_tags = {}  # object_id -> tag
        
    def add_tag(self, tag_name):
        """Добавить новый тег"""
        if tag_name not in self.tags and tag_name.strip():
            self.tags.append(tag_name)
            return True
        return False
        
    def remove_tag(self, tag_name):
        """Удалить тег"""
        if tag_name == "Untagged":
            return False
            
        if tag_name in self.tags:
            self.tags.remove(tag_name)
            # Обновляем объекты с этим тегом
            for obj_id, tag in list(self.object_tags.items()):
                if tag == tag_name:
                    self.object_tags[obj_id] = "Untagged"
            return True
        return False
        
    def set_object_tag(self, obj, tag_name):
        """Установить тег для объекта"""
        if tag_name in self.tags:
            self.object_tags[id(obj)] = tag_name
            return True
        return False
        
    def get_object_tag(self, obj):
        """Получить тег объекта"""
        return self.object_tags.get(id(obj), "Untagged")
        
    def find_objects_with_tag(self, tag_name):
        """Найти все объекты с указанным тегом"""
        if tag_name not in self.tags:
            return []
            
        return [obj for obj_id, tag in self.object_tags.items() if tag == tag_name]
        
    def rename_tag(self, old_name, new_name):
        """Переименовать тег"""
        if old_name not in self.tags or new_name in self.tags:
            return False
            
        index = self.tags.index(old_name)
        self.tags[index] = new_name
        
        # Обновляем все объекты с этим тегом
        for obj_id, tag in self.object_tags.items():
            if tag == old_name:
                self.object_tags[obj_id] = new_name
                
        return True
        
    def get_tag_count(self, tag_name):
        """Получить количество объектов с тегом"""
        return sum(1 for tag in self.object_tags.values() if tag == tag_name)