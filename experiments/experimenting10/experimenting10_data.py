import abc

import pydantic
import typing
import uuid
import pygame
import abc


class PlayerSprite(pydantic.BaseModel):
    velocity: tuple[int, int]
    position: tuple[int, int]


class Player(pydantic.BaseModel):
    display_name: str
    score: int
    sprite: PlayerSprite


class GameState(pydantic.BaseModel):
    players: typing.Dict[uuid.UUID, Player]


class PygameEvent(pydantic.BaseModel):
    pygame_type: int
    pygame_dict: dict[str, typing.Any]

class Message(pydantic.BaseModel, abc.ABC):
    message_type: str = ""
    data: pydantic.BaseModel

    @classmethod
    def update_message_type(cls):
        cls.message_type = cls.__name__
        # cast the data type somehow?

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.update_message_type()

class GameStateMessage(Message):
    data: GameState


class EventMessage(Message):
    data: PygameEvent


def encode_pygame_event(event: pygame.event.Event) -> PygameEvent:
    event_dict = dict()
    event_dict["type"] = "pygame"
    event_dict["pygame_type"] = event.type
    event_dict["pygame_dict"] = event.dict
    try:
        event_obj = PygameEvent(**event_dict)
        return event_obj
    except pydantic.ValidationError as e:
        raise e

def get_example_game_state():
    game_state_dict = dict()
    player_obj = get_default_player()
    game_state_dict["players"] = dict()
    game_state_dict["players"][uuid.uuid4()] = player_obj
    game_state_obj = GameState(**game_state_dict)
    return game_state_obj
def get_init_game_state():
    game_state_dict = dict()
    game_state_dict["players"] = dict()
    game_state_obj = GameState(**game_state_dict)
    return game_state_obj

def get_default_player():
    player_dict = dict()
    player_sprite_dict = dict()
    player_sprite_dict["velocity"] = (0,0)
    player_sprite_dict["position"] = (0,0)
    player_sprite_obj = PlayerSprite(**player_sprite_dict)
    player_dict["sprite"] = player_sprite_obj
    player_dict["score"] = 0
    player_dict["display_name"] = "Anonymous Player"
    player_obj = Player(**player_dict)
    return player_obj