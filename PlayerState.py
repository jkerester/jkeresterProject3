from dataclasses import dataclass
import json
from typing import Dict
import arcade
import datetime
from dataclasses_json import dataclass_json

WINDOW_WIDTH = 480
WINDOW_HEIGHT = 480


@dataclass_json
@dataclass
class PlayerState:
    x_loc: int
    y_loc: int
    points: int  # health?
    last_update: datetime.datetime


@dataclass_json
@dataclass
class TargetState:
    xLoc: int
    yloc: int


@dataclass
class PlayerMovement:
    keys = {
        arcade.key.UP: False,
        arcade.key.DOWN: False,
        arcade.key.LEFT: False,
        arcade.key.RIGHT: False,
        arcade.key.A: False}

    # to string is purely for debugging
    def __str__(self):
        return f"UP: {self.keys[arcade.key.UP]}, Down: {self.keys[arcade.key.DOWN]}, Left: {self.keys[arcade.key.LEFT]}, Right: {self.keys[arcade.key.RIGHT]}, "


@dataclass_json
@dataclass
class GameState:
    player_states: Dict[str, PlayerState]
    target: TargetState
