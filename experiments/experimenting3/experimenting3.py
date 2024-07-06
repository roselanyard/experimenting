import curses
import numpy
import abc
import pygame
import os

# local files
import constants


# game


class AbstractGame(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        raise NotImplementedError


class Game(AbstractGame):
    def __init__(self):
        raise NotImplementedError


class Window(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            instance = super(Window, cls).__new__(cls)
            assert ('curses.stdscr' not in globals())

            pygame.display.init()
            pygame.mixer.init()

            instance.display = Display()

            env = os.environ
            assert [env['']]
            cls._instance = instance
        return cls._instance


class Display:
    def __init__(self):
        self.surface = pygame.Surface


class PianoRoll(abc.ABC):
    pass


class Song():
    pass


# keyboard

class PianoKeyboardLayout():
    def __init__(self):
        self.computer_keymap = {}
        self.piano_keys = {}


class PianoKeyboard():
    def __init__(self, layout):
        self.layout = layout
        self.piano_keys = {}

    def display(self):
        for piano_key in self.piano_keys:
            piano_key.display()

    def computer_key_on(self, computer_key):
        played_piano_key = self.layout.computer_keymap[computer_key]
        assert (played_piano_key)
        played_piano_key.play_sound_on()

    def computer_key_off(self, computer_key):
        played_piano_key = self.layout.computer_keymap[computer_key]
        assert (played_piano_key)
        played_piano_key.play_sound_off()
        pass

    pass


### keys

class PianoKey(abc.ABC):
    def __init__(self):
        self.active_channel = None
        self.sprite = None
        pass

    def play_sound_on(self):
        assert (type(pygame.mixer.get_init()) is not type(None))
        self.active_channel = pygame.mixer.find_channel()
        self.active_channel.play(pygame.mixer.Sound(notes.PianoSound))
        pass

    def play_sound_off(self):
        # assert mixer is initialized?
        assert (self.active_channel.get_busy())
        self.active_channel.stop()
        self.active_channel = None
        pass

    def is_playing(self):
        pass

    def display(self):
        assert (Window().is_init())
        Window().surface.blit(self.sprite)


class WhiteKey(PianoKey):
    def __init__(self, orientation="center", position=0, note=notes.A4):
        self.sprite = AsciiSprite((0, 0))
        self.image = notes.WhiteKeyLeft

    def update_position(self, position: tuple[2]):
        self.sprite.position = position


class BlackKey(PianoKey):
    pass


class Note():
    pass


### sprite


class AsciiSprite():
    def __init__(self, position=(0, 0), image=None):
        self.position = position
        self.image = image
        pass


# def blit_ascii(AsciiSprite):
#    pass
# def blit_key()

def play_game():
    test: numpy.chararray = numpy.chararray((2, 2))
    test[:, :] = [['X', 'X'], ['X', 'X']]

    # write these in json later
    example_layout = PianoKeyboardLayout()
    example_layout.keymap = {'d': 0, 'f': 1}
    example_layout.keys = {0: WhiteKey(orientation="left", position=0, note=notes.A2), 1: WhiteKey(orientation="left", position=0, note=notes.A4)}

    keyboard = PianoKeyboard(example_layout)
    keyboard.display()

def main():
    Game()

if __name__ == "__main__":
    main()