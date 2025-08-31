import random
from OpenGL.GL import *

class WeatherSystem:
    def __init__(self):
        self.weather_type = "CLEAR"  # CLEAR, RAIN, SNOW, FOG, STORM
        self.intensity = 0.0  # 0.0 to 1.0
        self.wind_direction = [1, 0, 0]
        self.wind_speed = 0.0
        self.time_of_day = 12.0  # 0-24 hours
        self.day_night_cycle = True
        
        # Weather particles
        self.rain_particles = []
        self.snow_particles = []
        
    def set_weather(self, weather_type, intensity=0.5, duration=0.0):
        self.weather_type = weather_type
        self.intensity = intensity
        print(f"Weather changed to {weather_type} with intensity {intensity}")
        
    def update(self, delta_time):
        if self.day_night_cycle:
            self.time_of_day = (self.time_of_day + delta_time / 3600) % 24
            
        # Update weather particles
        if self.weather_type == "RAIN":
            self._update_rain(delta_time)
        elif self.weather_type == "SNOW":
            self._update_snow(delta_time)
            
    def _update_rain(self, delta_time):
        # Rain particle logic
        pass
        
    def _update_snow(self, delta_time):
        # Snow particle logic
        pass
        
    def get_sky_color(self):
        # Calculate sky color based on time of day
        hour = self.time_of_day
        if 6 <= hour < 18:  # Day
            return [0.53, 0.81, 0.98, 1.0]
        else:  # Night
            return [0.05, 0.05, 0.15, 1.0]