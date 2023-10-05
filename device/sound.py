import pygame


class Sound:
    def __init__(self, sound: pygame.mixer.Sound):
        self.sound = sound

    def play(self):
        #pygame.mixer.Sound.play(self.sound)
        self.sound.play()
    
    def stop(self):
        #pygame.mixer.Sound.play(self.sound)
        self.sound.stop()

    @property
    def volume(self) -> float:
        return self.sound.get_volume()

    @volume.setter
    def volume(self, value) -> None:
        self.sound.set_volume(value)
