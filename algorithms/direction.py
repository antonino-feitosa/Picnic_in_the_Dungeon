from typing import Dict
from typing import Tuple


class Direction:
    Up: "Direction"
    Down: "Direction"
    Left: "Direction"
    Right: "Direction"
    UpLeft: "Direction"
    UpRight: "Direction"
    DownLeft: "Direction"
    DownRight: "Direction"

    All: Tuple[
        "Direction",
        "Direction",
        "Direction",
        "Direction",
        "Direction",
        "Direction",
        "Direction",
        "Direction",
    ]
    Cardinals: Tuple["Direction", "Direction", "Direction", "Direction"]
    Diagonals: Tuple["Direction", "Direction", "Direction", "Direction"]

    _names: Dict["Direction", str]

    __slots__ = ["x", "y"]

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __neg__(self):
        return Direction(-self.x, -self.y)

    def __iter__(self):
        yield self.x
        yield self.y

    def __hash__(self) -> int:
        # NOTE it supports grids of 8192 x 8192
        return 4096 * (4096 + self.y) + (4096 + self.x)

    def __str__(self):
        if self in Direction._names:
            return Direction._names[self]
        return f"({self.x},{self.y})"

    def __repr__(self) -> str:
        return self.__str__()


Direction.Up = Direction(0, -1)
Direction.Down = Direction(0, 1)
Direction.Left = Direction(-1, 0)
Direction.Right = Direction(1, 0)
Direction.UpLeft = Direction(-1, -1)
Direction.UpRight = Direction(1, -1)
Direction.DownLeft = Direction(-1, 1)
Direction.DownRight = Direction(1, 1)

Direction.All = (
    Direction.Up,
    Direction.Down,
    Direction.Left,
    Direction.Right,
    Direction.UpLeft,
    Direction.UpRight,
    Direction.DownLeft,
    Direction.DownRight,
)
Direction.Cardinals = (Direction.Up, Direction.Down, Direction.Left, Direction.Right)
Direction.Diagonals = (
    Direction.UpLeft,
    Direction.UpRight,
    Direction.DownLeft,
    Direction.DownRight,
)

Direction._names = {
    Direction.Up: "Up",
    Direction.Down: "Down",
    Direction.Left: "Left",
    Direction.Right: "Right",
    Direction.UpLeft: "UpLeft",
    Direction.UpRight: "UpRight",
    Direction.DownLeft: "DownLeft",
    Direction.DownRight: "DownRight",
}