import pygame


class Music:
    def __init__(self, path: str, format: str):
        self.path = path
        self.format = format
        self.fadeIn = 0

    def play(self, fadeInMillis=0):
        self.fadeIn = fadeInMillis
        pygame.mixer.music.unload()
        pygame.mixer.music.load(self.path, self.format)
        pygame.mixer.music.play(1, fade_ms=self.fadeIn)

    def loop(self):
        pygame.mixer.music.play(-1, fade_ms=self.fadeIn)

    def pause(self):
        pygame.mixer.music.pause()

    def resume(self):
        pygame.mixer.music.unpause()

    def fade(self, millis=1000):
        pygame.mixer.music.fadeout(millis)

    def stop(self):
        pygame.mixer.music.unload()
        pygame.mixer.music.stop()

    @property
    def isPlaying(self):
        return pygame.mixer.music.get_busy()

    @property
    def volume(self) -> float:
        return pygame.mixer.music.get_volume()

    @volume.setter
    def volume(self, value) -> None:
        pygame.mixer.music.set_volume(value)
