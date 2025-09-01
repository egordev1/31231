from PyQt5.QtCore import Qt, QTimer
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np

class CurveType(Enum):
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"

class Animation:
    def __init__(self, target_object, duration=1.0, loop=False):
        self.target = target_object
        self.duration = duration
        self.loop = loop
        self.time = 0.0
        self.playing = False
        self.keyframes = {
            'position': [],
            'rotation': [],
            'scale': [],
            'color': []
        }
    
    def add_keyframe(self, time, property_type, value):
        self.keyframes[property_type].append((time, value))
        self.keyframes[property_type].sort(key=lambda x: x[0])
    
    def update(self, dt):
        if not self.playing:
            return
            
        self.time += dt
        
        if self.time > self.duration:
            if self.loop:
                self.time = 0.0
            else:
                self.playing = False
                return
        
        self.apply_animation()
    
    def apply_animation(self):
        for prop in ['position', 'rotation', 'scale', 'color']:
            if self.keyframes[prop]:
                current_value = self.interpolate(prop, self.time)
                setattr(self.target, prop, current_value)
    
    def interpolate(self, prop, time):
        keyframes = self.keyframes[prop]
        if not keyframes:
            return getattr(self.target, prop)
            
        # Find current keyframes
        prev_kf = None
        next_kf = None
        
        for kf_time, kf_value in keyframes:
            if kf_time <= time:
                prev_kf = (kf_time, kf_value)
            else:
                next_kf = (kf_time, kf_value)
                break
        
        if not prev_kf:
            return next_kf[1]
        if not next_kf:
            return prev_kf[1]
        
        # Linear interpolation
        t = (time - prev_kf[0]) / (next_kf[0] - prev_kf[0])
        return [prev_kf[1][i] + t * (next_kf[1][i] - prev_kf[1][i]) for i in range(len(prev_kf[1]))]
    
    def play(self):
        self.playing = True
        self.time = 0.0
    
    def stop(self):
        self.playing = False
        self.time = 0.0

class AnimationController:
    def __init__(self):
        self.animations = []
    
    def add_animation(self, animation):
        self.animations.append(animation)
    
    def update(self, dt):
        for anim in self.animations:
            anim.update(dt)
    
    def play_all(self):
        for anim in self.animations:
            anim.play()
    
    def stop_all(self):
        for anim in self.animations:
            anim.stop()