import pygame
import numpy
import numba

GRIDX = 400
GRIDY = 400

play_field = numpy.zeros((400, 400), dtype=bool)
#print(play_field)


@numba.njit(parallel=True)
def update_play_field(play_field_param: numpy.ndarray):
    play_field_next = numpy.copy(play_field_param)
    for i in numba.prange(0, GRIDX):
    #for i in range(0, GRIDX):
        for j in numba.prange(0, GRIDY-1):
        #for j in range(0, GRIDY):
            if j == 201 and i == 200:
                pass
            neighbors = numpy.count_nonzero(play_field_param[i - 1:i + 2,j - 1:j + 2])
            cell_alive = play_field_param[i, j]
            if cell_alive:
                neighbors -= 1
            if neighbors < 2:
                play_field_next[i,j] = False
            else:
                if neighbors == 2 or neighbors == 3:
                    if cell_alive or neighbors == 3:
                        play_field_next[i, j] = True
                else:
                    if neighbors > 3:
                        play_field_next[i, j] = False
    return play_field_next



play_field[200,200] = True
play_field[201,201] = True
play_field[202,201] = True
play_field[201,202] = True
play_field[200,202] = True

print(play_field[198:204,198:204])
print(play_field[201,201])
print(update_play_field(play_field)[198:204,198:204])
print(update_play_field(play_field)[198:204,198:204])

play_field_local = play_field
print(play_field_local[198:204,198:204])
play_field_local = update_play_field(play_field_local)
print(play_field_local[198:204,198:204])
play_field_local = update_play_field(play_field_local)
print(play_field_local[198:204,198:204])
play_field_local = update_play_field(play_field_local)
print(play_field_local[198:204,198:204])
play_field_local = update_play_field(play_field_local)