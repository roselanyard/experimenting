# assets
from imports import *

pygame.mixer.init()
pygame.font.init()

piano_key_left_off = pygame.image.load("../assets/piano/pianokeyleftoff.png")
piano_key_left_on = pygame.image.load("../assets/piano/pianokeylefton_retexture.png")
button_off = pygame.image.load("../assets/piano/buttonoff.png")
button_on = pygame.image.load("../assets/piano/buttonon.png")
piano_roll = pygame.image.load("../assets/piano/pianoroll.png")
note = pygame.image.load("../assets/piano/note.png")
note_hit = pygame.image.load("../assets/piano/note_hit.png")
black_pixel = pygame.image.load("../assets/piano/blackpixel.png")
bg = pygame.image.load("../assets/piano/bg.png")
rail = pygame.image.load("../assets/piano/rail.png")

piano_sound = pygame.mixer.Sound("../assets/UI Soundpack/UI Soundpack/MP3/Modern2.mp3")
hit_sound = pygame.mixer.Sound("../assets/UI Soundpack/UI Soundpack/MP3/Minimalist1.mp3")
click_sound = pygame.mixer.Sound("../assets/UI Soundpack/UI Soundpack/MP3/Minimalist8.mp3")

game_font = pygame.font.Font("../assets/piano/m5x7.ttf",16)