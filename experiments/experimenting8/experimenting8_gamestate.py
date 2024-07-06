import uuid

import pydantic
import pygame
import numpy
from typing import Dict, Any


class Player(pydantic.BaseModel):
    position: tuple[int, int]
    color: tuple[int, int, int]
    name: str
    id: uuid.UUID

    __hash__ = object.__hash__

class GameState(pydantic.BaseModel):
    color: tuple[int, int, int]
    angle: int
    players: Dict[uuid.UUID, Player]

    __hash__ = object.__hash__

class GameEvent(pydantic.BaseModel):
    #class Config:
    #    arbitrary_types_allowed = True
    type: int
    pygame_dict: dict
def getNextGameState(game_state: GameState):
    new_game_state = GameState()
    new_game_state.angle = game_state.angle + 1


if __name__ == "__main__":
    state_data = dict()
    state_data['color'] = (255, 255, 255)
    state_data['angle'] = 1
    state_data['players'] = dict()
    state = GameState(**state_data)

    print(state)
    print(state.json())
