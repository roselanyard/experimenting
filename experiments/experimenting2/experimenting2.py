import numpy
import pygame
import sys
import cv2


class Particle(pygame.sprite.Sprite):
    def __init__(self, image: pygame.image):
        super().__init__(self)
        # time since creation
        self.t = 0
        self.position = pygame.Vector2(0,0)
        self.image = image
    def update(self):
        pass


class Heart(Particle):
    def __init__(self):
        super().__init__(pygame.image.load("./assets/redheart.png"))
    def update(self):
        pass

class Path:
    def __init__(self):
        pass
    def position(t):
        pass

class Glegle(pygame.sprite.Sprite):
    _instance = None

    def __new__(cls):
        if (cls._instance == None):
            cls._instance = super(pygame.sprite.Sprite,cls).__new__(cls)
            cls._instance.position = pygame.Vector2(0, 0)
            cls._instance.image = pygame.image.load("./assets/glegle.png")
            cls._instance.rect = cls._instance.image.get_rect()
        return cls._instance



def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()
    running = True

    black = pygame.Color(0,0,0)
    # pygame.mixer_music.load("./assets/overworld.mp3")
    pygame.mixer_music.load("./assets/pie.mp3")
    mouse_position = (0,0)
    # movie = cv2.VideoCapture("./assets/pie.mp4")
    # movie.set(2,0)
    # frame = 0

    while running:

        if pygame.mixer_music.get_busy() != True:
           pygame.mixer_music.play()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        mouse_position = pygame.mouse.get_pos()
        for x in 0,1:
            Glegle().position[x] = pygame.math.lerp(Glegle().position[x],mouse_position[x],0.2)

        screen.fill(black)
        # lambda just returns center of the image passed to it based on its size tuple
        screen.blit(Glegle().image, (lambda x,y: (x[0]-y[0]/2, x[1]-y[1]/2))(Glegle().position,Glegle().image.get_size()))

        pygame.display.flip()

        # frame += 1
        # movie.set(0,frame)
        # ret = movie.read()

        clock.tick(60)


if __name__ == "__main__":
    main()
