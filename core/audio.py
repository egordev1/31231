import pygame
import os

class AudioSystem:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music = None
        self.volume = 1.0
        self.music_volume = 0.7
        
    def load_sound(self, name, path):
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
            return True
        except:
            print(f"Failed to load sound: {path}")
            return False
            
    def play_sound(self, name, loops=0, volume=1.0):
        if name in self.sounds:
            sound = self.sounds[name]
            sound.set_volume(volume * self.volume)
            sound.play(loops)
            
    def play_music(self, path, loops=-1):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(loops)
            pygame.mixer.music.set_volume(self.music_volume)
            self.music = path
        except:
            print(f"Failed to load music: {path}")
            
    def stop_music(self):
        pygame.mixer.music.stop()
        
    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        
    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)