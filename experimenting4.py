import queue
import types
import random
import pygame

pygame.init()
pygame.display.init()
pixel_display = pygame.Surface((64,64))
display = pygame.display.set_mode((512,512))

piano_key_left_off = pygame.image.load("assets/piano/pianokeyleftoff.png")
piano_key_left_on = pygame.image.load("assets/piano/pianokeylefton.png")
button_off = pygame.image.load("./assets/piano/buttonoff.png")
button_on = pygame.image.load("./assets/piano/buttonon.png")
piano_roll = pygame.image.load("./assets/piano/pianoroll.png")
note = pygame.image.load("./assets/piano/note.png")
note_hit = pygame.image.load("./assets/piano/note_hit.png")

running = True

pygame.mixer.init()
clock = pygame.time.Clock()

piano_sound = pygame.mixer.Sound("./assets/UI Soundpack/UI Soundpack/MP3/Abstract1.mp3")
hit_sound = pygame.mixer.Sound("./assets/UI Soundpack/UI Soundpack/MP3/Modern4.mp3")

death_queue = []
class Key:
    def __init__(self):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = piano_key_left_off
        self.sprite.rect = piano_key_left_off.get_rect()
        self.sprite.position = (0,0)
        self.channel: pygame.mixer.Channel | None = None

    def update_position(self,position:tuple[2]):
        self.sprite.position = position
    def playsound(self):
        self.channel = pygame.mixer.find_channel(force=True)
        if type(self.channel) is types.NoneType:
            pass
        else:
            self.channel.play(piano_sound)
    def stop_playsound(self):
        if type(self.channel) is not types.NoneType:
            self.channel.stop()

class Button():
    def __init__(self):
        self.is_on = False
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = button_off
        self.sprite.rect = piano_key_left_off.get_rect()
        self.sprite.position = (0,0)

    def turn_on(self):
        self.is_on = True
        self.sprite.image = button_on

    def turn_off(self):
        self.is_off = False
        self.sprite.image = button_off

    def update_position(self, position: tuple[2]):
        self.sprite.position = position

class PianoRoll():
    def __init__(self):
        self.is_on = False
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = piano_roll
        self.sprite.rect = piano_key_left_off.get_rect()
        self.sprite.position = (0, 0)

    def update_position(self, position: tuple[2]):
        self.sprite.position = position

class Note():
    def __init__(self):
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = note
        self.sprite.rect = piano_key_left_off.get_rect()
        self.sprite.position = (0, 0)
        self.hit_status = False

    def update_position(self, position: tuple[2]):
        self.sprite.position = position

    def hit(self):
        if not self.hit_status:
            self.sprite.image = note_hit
            self.play_hit_sound()
            death_queue.append(self)
        self.hit_status = True

    def play_hit_sound(self):
        pygame.mixer.find_channel(force=True).play(hit_sound)


pkey0 = Key()
pkey1 = Key()
pkey2 = Key()
pkey3 = Key()

pkey1.update_position((4,0))
pkey2.update_position((8,0))
pkey3.update_position((12,0))

button0 = Button()
button1 = Button()
button2 = Button()
button3 = Button()

button0.update_position((0,12))
button1.update_position((4,12))
button2.update_position((8,12))
button3.update_position((12,12))

pianoroll0 = PianoRoll()
pianoroll0.update_position((0,16))

note0 = Note()
note0.update_position((0,60))

sounds = {'A4':None}
keymap = {pygame.K_d:0,pygame.K_f:1,pygame.K_j:2,pygame.K_k:3}
pkey_id_to_object = {0:pkey0, 1:pkey1, 2:pkey2, 3:pkey3}
pkey_id_to_button = {0:button0, 1:button1, 2:button2, 3:button3}

escape_tally = 0
escape_counter = 0

key_0_notes = {}

timer = 0
while running:

    # pixel_display.blit(piano_key_left, (0, 0))
    # pixel_display.blit(piano_key_left, (0, 0))

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            kkey_unicode = event.dict.get('key')
            if kkey_unicode in keymap.keys():
                pkey_object = pkey_id_to_object[keymap[kkey_unicode]]
                pkey_object.playsound()
                pkey_object.sprite.image = piano_key_left_on

                button_object = pkey_id_to_button[keymap[kkey_unicode]]
                button_object.turn_off()


            if kkey_unicode == pygame.K_ESCAPE:
                if escape_counter > 0:
                    running = False
                else:
                    escape_counter = 60

        if event.type == pygame.KEYUP:
            kkey_unicode = event.dict.get('key')
            if kkey_unicode in keymap.keys():
                pkey_object = pkey_id_to_object[keymap[kkey_unicode]]
                pkey_object.stop_playsound()
                pkey_object.sprite.image = piano_key_left_off



    for pkey_id in pkey_id_to_object.keys():
        pkey_object = pkey_id_to_object[pkey_id]
        pixel_display.blit(pkey_object.sprite.image,pkey_object.sprite.position)

        button_object = pkey_id_to_button[pkey_id]
        pixel_display.blit(button_object.sprite.image,button_object.sprite.position)

    pixel_display.blit(pianoroll0.sprite.image, pianoroll0.sprite.position)
    pixel_display.blit(note0.sprite.image, note0.sprite.position)

    pygame.transform.scale(pixel_display, (512, 512), display)
    pygame.display.flip()

    if timer == 0 and random.random() < 1:
        chosen_button = random.random()*4
        if chosen_button < 1:
            button0.turn_on()
        if chosen_button < 2 and chosen_button >= 1:
            button1.turn_on()
        if chosen_button < 3 and chosen_button >= 2:
            button2.turn_on()
        if chosen_button < 4 and chosen_button >= 3:
            button3.turn_on()

    if timer % 5 == 0:
        if note0.sprite.position[1] < button0.sprite.position[1] - 2:
            note0.update_position((0,32))
        else:
            if note0.sprite.position[1] < button0.sprite.position[1] + 4 and pygame.key.get_pressed()[pygame.K_d]:
                note0.hit()
            xy = list(note0.sprite.position)
            xy[1] -= 1
            note0.sprite.position = tuple(xy)
        for obj in death_queue:
            death_queue.remove(obj)
            del obj



    clock.tick(60)
    timer = (timer + 1) % 30
    if escape_counter > 0:
        escape_counter -= 1