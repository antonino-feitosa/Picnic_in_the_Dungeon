import pygame


class Sound:
    def __init__(self, sound: pygame.mixer.Sound):
        self.sound = sound

    def play(self):
        self.sound.play()
    
    def stop(self):
        self.sound.stop()

    @property
    def volume(self) -> float:
        return self.sound.get_volume()

    @volume.setter
    def volume(self, value) -> None:
        self.sound.set_volume(value)
