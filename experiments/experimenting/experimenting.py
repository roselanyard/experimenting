from imports import *

# singleton class for game
class Game:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Game,cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pygame.init()
        # self.state = GameState()
        # self.properties = GameProperties()
        self.screen = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()
        self.running = True
        self.layers = None
        self.render_queue = None

''' @dataclasses.dataclass
class GameState:
    def __init__(self):
        self.running = None

@dataclasses.dataclass
class GameProperties:
'''

# field of squares with a value corresponding to a given object
class SquareField():
    def __init__(self,square_size,rows,cols):
        self.contents = {}
        self.content_sprites = {}

    def updateContents(self):
        pass
    def getContents(self):
        pass
    def getContentsAtCell(self):
        pass
    def updateContentsAtCell(self):
        pass
    def iForgot(self):
        pass

class Object():
    def __init__(self):
        self.position: tuple = (0,0)
        self.sprite: pygame.Surface = None
    def add_to_render_queue(self,layer:pygame.Surface):
        Game().render_queue()

class Square(Object):
    pass
class RedSquare(Square):
    pass
class WhiteSquare(Square):
    pass


def mainloop():
    # polling for events
    while Game().running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Game().running = False
        Game().screen.fill("black")
        pygame.display.flip()

        Game().clock.tick(60)

if __name__ == "__main__":
    mainloop()