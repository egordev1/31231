from OpenGL.GL import *
import numpy as np

class Octree:
    def __init__(self, bounds, max_depth=8, max_objects=10):
        self.bounds = bounds  # [min_x, min_y, min_z, max_x, max_y, max_z]
        self.max_depth = max_depth
        self.max_objects = max_objects
        self.objects = []
        self.children = []
        self.depth = 0
        
    def insert(self, obj, bounds):
        if not self._intersects(bounds):
            return False
            
        if len(self.objects) < self.max_objects or self.depth >= self.max_depth:
            self.objects.append((obj, bounds))
            return True
            
        if not self.children:
            self._subdivide()
            
        for child in self.children:
            if child.insert(obj, bounds):
                return True
                
        self.objects.append((obj, bounds))
        return True
        
    def query(self, query_bounds):
        results = []
        if not self._intersects(query_bounds):
            return results
            
        results.extend([obj for obj, _ in self.objects])
        
        for child in self.children:
            results.extend(child.query(query_bounds))
            
        return results
        
    def _subdivide(self):
        cx = (self.bounds[0] + self.bounds[3]) / 2
        cy = (self.bounds[1] + self.bounds[4]) / 2
        cz = (self.bounds[2] + self.bounds[5]) / 2
        
        # Create 8 children
        for i in range(8):
            child_bounds = [
                self.bounds[0] if i % 2 == 0 else cx,
                self.bounds[1] if (i // 2) % 2 == 0 else cy,
                self.bounds[2] if (i // 4) % 2 == 0 else cz,
                cx if i % 2 == 0 else self.bounds[3],
                cy if (i // 2) % 2 == 0 else self.bounds[4],
                cz if (i // 4) % 2 == 0 else self.bounds[5]
            ]
            
            child = Octree(child_bounds, self.max_depth, self.max_objects)
            child.depth = self.depth + 1
            self.children.append(child)
            
    def _intersects(self, bounds):
        return not (bounds[3] < self.bounds[0] or bounds[0] > self.bounds[3] or
                   bounds[4] < self.bounds[1] or bounds[1] > self.bounds[4] or
                   bounds[5] < self.bounds[2] or bounds[2] > self.bounds[5])

class SpatialPartitioning:
    def __init__(self):
        self.octree = None
        self.object_bounds = {}
        
    def initialize(self, scene_bounds):
        self.octree = Octree(scene_bounds)
        
    def add_object(self, obj, bounds):
        self.object_bounds[obj] = bounds
        if self.octree:
            self.octree.insert(obj, bounds)
            
    def get_visible_objects(self, frustum):
        if not self.octree:
            return []
        return self.octree.query(frustum.get_bounds())