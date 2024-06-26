import math
import asyncio
import pygame
import threading
import experimenting6_udp_recv
import experimenting6_locks
import socket
import sys
import time
import logging
import decorator
import textwrap

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class Message:
    def __init__(self):
        self.content = ""
        self.incoming = False

    def __init__(self, str: str):
        self.content = str
        self.incoming = False

    def __init__(self, msg: list[str]):
        self.content = msg
        self.incoming = False


pygame.init()
pygame.display.init()
pygame.font.init()
clock = pygame.time.Clock()

font = pygame.font.Font("C:/Users/Alexandra/PycharmProjects/game_learning/assets/piano/m5x7.ttf", 16)
message_background = pygame.image.load("C:/Users/Alexandra/PycharmProjects/game_learning/assets/01_Flat_Theme/Sprites/UI_Flat_Frame_01_Standard.png")
message_background_size_over_three = message_background.get_size()[0]/3

message_corner = pygame.image.load("C:/Users/Alexandra/PycharmProjects/game_learning/assets/experimenting6/message_corner.png")
message_body = pygame.image.load("C:/Users/Alexandra/PycharmProjects/game_learning/assets/experimenting6/message_body.png")
message_edge = pygame.image.load("C:/Users/Alexandra/PycharmProjects/game_learning/assets/experimenting6/message_edge.png")

# message_background_grid = []
# for i in 0, 1, 2:
#    message_background_grid.append([])
#    for j in 0, 1, 2:
#        message_background_grid[i].append(pygame.transform.chop(message_background,
#                                                              (message_background_size_over_three * i,
#                                                               message_background_size_over_three * j,
#                                                               message_background_size_over_three * (i + 1),
#                                                               message_background_size_over_three * (j + 1))))

res_x = 1080
res_y = 480

display = pygame.display.set_mode((res_x, res_y))
# pygame.display.RESIZABLE = True
pygame.RESIZABLE = True
# pygame.NOFRAME = True


def render_message_text(text: str | list[str]) -> pygame.Surface:
    #offset = 5
    vertical_offset = 2
    if type(text) == type(""):
        text_ = font.render(text, False, (255,255,255))
        text_ = pygame.transform.scale(text_,((text_.get_size()[0]*2,text_.get_size()[1]*2)))
        return text_
    if type(text) == type([""]):
        space_height = font.render(" ", False, (255,255,255)).get_height()
        line_num = 0
        surf = pygame.Surface((1,space_height*len(text)),pygame.SRCALPHA,32)
        surf = surf.convert_alpha()
        for line in text:
            if len(line) == 0:
                continue
            line_cat = ''.join(line)
            curr_line_text = font.render(line_cat, False, (255,255,255))
            if curr_line_text.get_size()[0] > surf.get_size()[0]:
                # new_surf = pygame.Surface((curr_line_text.get_size()[0]+offset,space_height*len(text)),pygame.SRCALPHA,32)
                new_surf = pygame.Surface((curr_line_text.get_size()[0], (space_height + vertical_offset) * len(text)),
                                          pygame.SRCALPHA, 32)
                new_surf = new_surf.convert_alpha()
                new_surf.blit(surf,(0,0))
                surf = new_surf
            surf.blit(curr_line_text,(0, (line_num*space_height) + vertical_offset))
            #surf.blit(curr_line_text, (offset, (line_num * space_height) + 2))
            line_num += 1
        surf = pygame.transform.scale(surf, ((surf.get_size()[0]*2,surf.get_size()[1]*2)))
        #while True:
        #    display.fill((255, 255, 255))
        #    display.blit(surf, (0, 0))
        #    pygame.display.flip()
        return surf

# FUUUUUUUCK!
def render_message_text_(text:str ) -> pygame.Surface:
    surf = font.render(text,False,(255,255,255),bgcolor=None,wraplength=160)
    surf = pygame.transform.scale(surf, ((surf.get_size()[0]*2,surf.get_size()[1]*2)))
    return surf


def word_wrap(text: str):
    max_line_len = 160
    tokenized_lines = [line.split(' ') for line in text.splitlines()]
    new_lines = [[]]
    space_width = font.size(' ')[0]
    current_x = 0
    current_line = 0
    for j,token_list in enumerate(tokenized_lines):
        for i,tok in enumerate(token_list):
            tok_surface = font.render(tok,False,(255,255,255))
            tok_width = tok_surface.get_size()[0]
            if tok_width + current_x <= max_line_len:
                new_lines[current_line].append(tok)
                current_x += tok_width
                #if tok_width < max_line_len:

                #else:
            else:
                current_line += 1
                current_x = 0
                new_lines.append([])
                new_lines[current_line].append(tok)
            if space_width + current_x <= max_line_len:
                new_lines[current_line].append(' ')
                current_x += space_width
        current_line += 1
        current_x = 0
        if j == len(tokenized_lines)-1:
            break
        new_lines.append([])
    print(new_lines)
    return new_lines



def render_background() -> pygame.Surface:
    surf = pygame.Surface((display.get_size()))
    surf.fill((255, 255, 255))
    return surf


def render_message(message: Message) -> pygame.Surface:
    horizontal_offset = 5
    text = render_message_text_(message.content)
    text_pixel_size = text.get_size()
    message_block = render_block_of_min_size(text_pixel_size)
    message_block.blit(text,(horizontal_offset,0))
    return message_block


def render_block_of_min_size(size: tuple[int, int]):
    dimensions = math.ceil(size[0] / message_background_size_over_three), math.ceil(
        size[1] / message_background_size_over_three)
    surf = pygame.Surface((dimensions[0]*message_background_size_over_three, dimensions[1]*message_background_size_over_three))
    # corners
    surf.blit(message_corner, (0, 0))
    surf.blit(pygame.transform.rotate(message_corner, 90),
              (0, (dimensions[1] - 1) * message_background_size_over_three))
    surf.blit(pygame.transform.rotate(message_corner, 270),
              ((dimensions[0] - 1) * message_background_size_over_three, 0))
    surf.blit(pygame.transform.rotate(message_corner, 180),
              ((dimensions[0] - 1) * message_background_size_over_three,
               (dimensions[1] - 1) * message_background_size_over_three))
    # edges
    for i in range(dimensions[1]-2):
        surf.blit(pygame.transform.rotate(message_edge,180),
                  ((dimensions[0] - 1) * message_background_size_over_three, (i + 1) * message_background_size_over_three))
        surf.blit(message_edge,
                  (0 * message_background_size_over_three, (i + 1) * message_background_size_over_three))
    for i in range(dimensions[0] - 2):
        surf.blit(pygame.transform.rotate(message_edge, 90),
                  ((i + 1) * message_background_size_over_three, (dimensions[1] - 1) * message_background_size_over_three))
        surf.blit(pygame.transform.rotate(message_edge, 270),
                  ((i + 1) * message_background_size_over_three, 0 * message_background_size_over_three))
        for j in range(dimensions[1] - 2):
            surf.blit(message_body,
                      ((i + 1) * message_background_size_over_three, (j + 1) * message_background_size_over_three))
    return surf


# for i, x in enumerate(message_background_grid):
# for j, y in enumerate(x):
# display.blit(y, (j * message_background_size_over_three, j * message_background_size_over_three))

net_bytestring = b""
net_lock = threading.Lock()
messages = []
def recv():
    global net_bytestring
    global messages

    try:
        ns = sock.recv(1024)
        pass
    except socket.error as e:
        pass
    else:
        with net_lock:
            #messages.append(Message(word_wrap(str(ns,encoding="utf-8"))))
            messages.append(Message((str(ns,encoding="utf-8"))))


#net_thread = threading.Thread(target = recv)
def main():
    global messages
    global res_x
    global res_y
    global display

    scrollpos = 0

    sock.bind((UDP_IP, UDP_PORT))
    sock.setblocking(False)
    local_net_string = ""
    #sock.settimeout(0.1)
    running = True
    messages.append(Message("testicular manslaughter"))
    messages.append(Message("vehicular torsion"))
    messages.append(Message("extremely long string of text used to test how long this will be"))
    #messages.append(Message(word_wrap("extremely long string of text used to test how long this will be")))
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.VIDEORESIZE:
                res_x = e.dict.get('w')
                res_y = e.dict.get('h')
                display = pygame.display.set_mode((res_x, res_y))

        recv()
        display.blit(render_background(), (0, 0))

        with net_lock:
            if net_bytestring != b'':
                # messages.append(Message(str(net_bytestring, encoding="utf-8")))
                pass
        extra_lines = 0
        message_buf = pygame.Surface(display.get_size(),pygame.SRCALPHA,32)
        message_buf.convert_alpha()
        for i,message in enumerate(messages):
            surf = render_message(message)
            surf_dest = (2,((i+extra_lines)*message_background_size_over_three)+(2*(i)))
            if surf_dest[1] + surf.get_size()[1] > message_buf.get_size()[1]:
                new_mess_buf = pygame.Surface((res_x,surf_dest[1] + surf.get_size()[1]),pygame.SRCALPHA,32)
                new_mess_buf = new_mess_buf.convert_alpha()
                new_mess_buf.blit(message_buf,(0,0))
                message_buf = new_mess_buf
            message_buf.blit(surf,surf_dest)
            #if type(message.content) == type([]) and len(message.content) > 1:
            #    extra_lines += len(message.content) - 1
            if math.ceil(surf.get_height()/32) > 1:
                extra_lines += math.ceil(surf.get_height()/32) - 1
        extra_lines = 0

        message_buf_rect = message_buf.get_rect()
        # max_scrollpos = message_buf_rect[3]
        cropped_y = message_buf_rect[3] - display.get_rect()[3]
        message_buf_rect[1] = cropped_y
        message_buf_crop = message_buf.subsurface((message_buf_rect[0],message_buf_rect[1],res_x,res_y))
        display.blit(message_buf_crop,(0,0))

        #async with experimenting6_locks.net_lock:
        #    local_net_string = net_string
        #display.blit(render_block_of_min_size((96, 96)), (0, 0))

        pygame.display.flip()
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    #asyncio.run(main())
    #asyncio.run(recv())
    word_wrap("test")
    main()
    #t = threading.Thread(target = main)
    # th = threading.Thread(target = recv)
    # th.daemon = True
    # t.daemon = True
    #t.start()
    # th.start()
    #t.join()
    # th.join()