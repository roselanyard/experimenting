import assets
from imports import *

# classes
'''@abc.ABC
class GameObject(pygame.sprite.Sprite):
    @abc.abstractmethod
    def __init__(self):
        super().__init__()
        self.image = assets.black_pixel
        self.position = (0, 0)
        self.rect = pygame.Rect(0, 0, 0, 0)

    @abc.abstractmethod
    def update_position(self):
        pass
'''

class Key(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = assets.piano_key_left_off
        self.rect = assets.piano_key_left_off.get_rect()
        self.position = (0, 0)
        self.channel: pygame.mixer.Channel | None = None

    def update_position(self, position: tuple[int, int]):
        self.position = position

    def play_sound(self):
        self.channel = pygame.mixer.find_channel(force=True)
        if type(self.channel) is types.NoneType:
            pass
        else:
            self.channel.play(assets.piano_sound)

    def stop_playing_sound(self):
        if type(self.channel) is not types.NoneType:
            self.channel.stop()

    def hold(self):
        self.image = assets.piano_key_left_on
        self.play_sound()

    def release(self):
        self.image = assets.piano_key_left_off
        self.stop_playing_sound()


class Button(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.is_on = False
        self.image = assets.button_off
        self.rect = assets.piano_key_left_off.get_rect()
        self.position = (0, 0)
        self.ontimer = 0

    def turn_on(self):
        self.is_on = True
        self.image = assets.button_on
        self.ontimer = 20

    def turn_off(self):
        self.is_on = False
        self.image = assets.button_off
        self.ontimer = 0

    def update_position(self, position: tuple[int, int]):
        self.position = position


class PianoRoll(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.is_on = False
        self.image = assets.piano_roll
        self.rect = assets.piano_key_left_off.get_rect()
        self.position = (0, 0)

    def update_position(self, position: tuple[int, int]):
        self.position = position


class Note(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = assets.note
        self.rect = assets.piano_key_left_off.get_rect()
        self.position = (0, 0)
        self.hit_status = False

    def update_position(self, position: tuple[int, int]):
        self.position = position

    def hit(self):
        if not self.hit_status:
            self.image = assets.note_hit
            self.play_hit_sound()
        self.hit_status = True

    @staticmethod
    def play_hit_sound():
        pygame.mixer.find_channel(force=True).play(assets.hit_sound)

class HoldNote(Note):
    def __init__(self,length: int):
        super().__init__()
        note_top_cap = pygame.transform.chop(assets.note,(0,0,0,3))
        note_interior = pygame.transform.chop(assets.note,(0,1,3,2))
        note_end_cap = pygame.transform.chop(assets.note,(0,3,3,3))
        note_size = assets.note.get_size()
        surface = pygame.surface.Surface(note_size[0],note_size[1]+(4*length))
        surface.blit(note_top_cap,(0,0))
        for i in range(length):
            surface.blit(note_interior,(0,2+i))
        surface.blit(note_end_cap,(0,2+i*length))
        self.image = surface
        self.rect = self.image.get_rect()


class Column(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.pkey = Key()
        self.button = Button()
        self.position = (0, 0)
        self.notes: set[Note] = set()
        self.kkey = pygame.K_l

    def update_position(self, position: tuple[int, int]):
        self.position = position
        self.pkey.update_position(position)
        self.button.update_position((position[0], position[1] + 12))
        for note in self.notes:
            note.update_position((position[0], note.position[1]))

    def new_note(self, note: Note):
        self.notes.add(note)
        note.update_position((self.position[0], self.position[1] + 60))

    def remove_note(self, note):
        if note in self.notes:
            self.notes.remove(note)
        del note

    def set_kkey(self, kkey: int):
        self.kkey = kkey

class Rail(pygame.sprite.Sprite):
    def __init__(self):
        pass

class Scoreboard:
    def __init__(self):
        self.score = 0
        self.places = 3
    def get_score_string(self):
        printed_score = min(self.score, math.pow(10,self.places))
        printed_score_string = str(printed_score)
        printed_score_string = printed_score_string.rjust(self.places," ")
        return printed_score_string
    def render(self):
        return assets.game_font.render(self.get_score_string(), False, (255, 255, 255))
    def get_score(self):
        return self.score
    def set_score(self,score):
        self.score = score