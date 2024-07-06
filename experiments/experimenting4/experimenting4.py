import pygame.mixer

from imports import *
import assets
from classes import *
from globals import *

# initialization

def debug():
    HoldNote(4)

pygame.init()
pygame.display.init()
pixel_display = pygame.Surface((64,64))
display = pygame.display.set_mode((512,512))
# pygame mixer initialized in assets.py
clock = pygame.time.Clock()
running = True

game_position = 24

# object instances

GameClasses = {Key,Button,PianoRoll,Note}

pkey0 = Key()
pkey1 = Key()
pkey2 = Key()
pkey3 = Key()

keyboard = pygame.sprite.Group()
keyboard.add(pkey0)
keyboard.add(pkey1)
keyboard.add(pkey2)
keyboard.add(pkey3)

pkey1.update_position((4, 0))
pkey2.update_position((8, 0))
pkey3.update_position((12, 0))

button0 = Button()
button1 = Button()
button2 = Button()
button3 = Button()

buttons = pygame.sprite.Group()
buttons.add(button0)
buttons.add(button1)
buttons.add(button2)
buttons.add(button3)

button0.update_position((0, 12))
button1.update_position((4, 12))
button2.update_position((8, 12))
button3.update_position((12, 12))

pianoroll0 = PianoRoll()
pianoroll0.update_position((game_position, 16))

note0 = Note()
note0.update_position((0, 60))

# variables depending on object instance

column0 = Column()
column0.update_position((game_position,0))
column1 = Column()
column1.update_position((game_position+4,0))
column2 = Column()
column2.update_position((game_position+8,0))
column3 = Column()
column3.update_position((game_position+12,0))

columns = [column0,column1,column2,column3]

column0.set_kkey(pygame.K_d)
column1.set_kkey(pygame.K_f)
column2.set_kkey(pygame.K_j)
column3.set_kkey(pygame.K_k)

column0.new_note(note0)
column1.new_note(Note())

# sounds = {'A4': None}
# keymap = {pygame.K_d: 0, pygame.K_f: 1, pygame.K_j: 2, pygame.K_k: 3}
# pkey_id_to_object = {0: pkey0, 1: pkey1, 2: pkey2, 3: pkey3}
# pkey_id_to_button = {0: button0, 1: button1, 2: button2, 3: button3}

sounds = {'A4': None}
keymap = {pygame.K_d: 0, pygame.K_f: 1, pygame.K_j: 2, pygame.K_k: 3}
pkey_id_to_object = {0: column0.pkey, 1: column1.pkey, 2: column2.pkey, 3: column3.pkey}
pkey_id_to_button = {0: column0.button, 1: column1.button, 2: column2.button, 3: column3.button}


# loop variables

escape_tally = 0
escape_counter = 0
timer = 0
game_state = 0
scoreboard = Scoreboard()

while running:

    # debug()

    # pixel_display.blit(piano_key_left, (0, 0))
    # pixel_display.blit(piano_key_left, (0, 0))

    pixel_display.fill(pygame.color.Color(0,0,0))
    pixel_display.blit(assets.bg,(0,0))

    cycle = 0
    cycle = (cycle + 1) % 64
    # rail_rect = assets.rail.get_rect()
    # railtop = pygame.transform.chop(assets.rail,(0,cycle,rail_rect[2],rail_rect[3]))
    # railbttm = pygame.transform.chop(assets.rail,(0,0,rail_rect[2],cycle))

    # pixel_display.blit(railtop,(22,0))
    # pixel_display.blit(railbttm,(44,railtop.get_rect()[3]))
    pixel_display.blit(assets.rail,(22,0))
    pixel_display.blit(assets.rail,(40,0))
    pixel_display.blit(scoreboard.render(),(2,0))
    if game_state == 0:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                kkey_unicode = event.dict.get('key')
                if kkey_unicode in keymap.keys():
                    pkey_object = pkey_id_to_object[keymap[kkey_unicode]]
                    pkey_object.hold()

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
                    pkey_object.release()

        for pkey_id in pkey_id_to_object.keys():
            pkey_object = pkey_id_to_object[pkey_id]
            pixel_display.blit(pkey_object.image, pkey_object.position)

            button_object = pkey_id_to_button[pkey_id]
            pixel_display.blit(button_object.image, button_object.position)

        pixel_display.blit(pianoroll0.image, pianoroll0.position)
        for column in columns:
            for note in column.notes:
                pixel_display.blit(note.image, note.position)

        pygame.transform.scale(pixel_display, (512, 512), display)
        pygame.display.flip()

        if timer == 0:
            pygame.mixer.find_channel(force=True).play(assets.click_sound)
            if random.random() < 1:
                chosen_button = random.random() * 6
                if chosen_button < 1:
                    # button0.turn_on()
                    column0.new_note(Note())
                if chosen_button < 2 and chosen_button >= 1:
                    # button1.turn_on()
                    column1.new_note(Note())
                if chosen_button < 3 and chosen_button >= 2:
                    # button2.turn_on()
                    column2.new_note(Note())
                if chosen_button < 4 and chosen_button >= 3:
                    # button3.turn_on()
                    column3.new_note(Note())

        if timer % 4 == 0:

            for i,column in enumerate(columns):
                deleted_notes = []

                if column.button.ontimer <= 0:
                    column.button.turn_off()
                else:
                    column.button.ontimer -= 1

                for note in column.notes:
                    if note.position[1] < column.button.position[1] - 2:
                        deleted_notes.append(note)
                        if scoreboard.score > 0:
                            scoreboard.score -= 1
                    else:
                        if note.position[1] < column.button.position[1] + 4 and pygame.key.get_pressed()[column.kkey]:
                            note.hit()
                            scoreboard.score += 5
                            column.button.turn_on()
                            deleted_notes.append(note)
                        xy = list(note.position)
                        xy[1] -= 1
                        note.position = tuple(xy)
                for note in deleted_notes:
                    column.remove_note(note)
            '''...'''

        clock.tick(240)
        timer = (timer + 1) % 60
        if escape_counter > 0:
            escape_counter -= 1
