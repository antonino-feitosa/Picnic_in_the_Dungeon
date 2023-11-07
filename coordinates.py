


class Position:
    __slots__ = ["x", "y"]

    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        return f"({self.x},{self.y})"

    def __add__(self, other: "Position | Direction") -> "Position":
        return Position(self.x + other.x, self.y + other.y)

    def __radd__(self, other: "Position | Direction") -> "Position":
        return self.__add__(other)

    def __hash__(self) -> int:
        # NOTE it supports grids of 8192 x 8192
        return 4096 * (4096 + self.y) + (4096 + self.x)

    def __eq__(self, other: "Position"):
        return other is not None and self.x == other.x and self.y == other.y

    def __ne__(self, other: "Position"):
        return self.x != other.x or self.y != other.y

    def __iter__(self):
        yield self.x
        yield self.y

    def relativeDirection(self, dest: "Position") -> "Direction":
        sign = lambda x: 0 if x == 0 else (1 if x > 0 else -1)
        dx = sign(dest.x - self.x)
        dy = sign(dest.y - self.y)
        return Direction(dx, dy)

    def distanceSquare(self, other: "Position") -> int:
        return max(abs(self.x - other.x), abs(self.y - other.y))

    def distanceDiamond(self, other: "Position") -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def distanceCircle(self, other: "Position") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** (1 / 2)





class Dimension:
    __slof__ = ["width", "height"]

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def __contains__(self, element: Position):
        return (
            element.x < self.width
            and element.y < self.height
            and element.x >= 0
            and element.y >= 0
        )

    def __iter__(self):
        yield self.width
        yield self.height

    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        return f"({self.width},{self.height})"





class Direction:
    Up: "Direction"
    Down: "Direction"
    Left: "Direction"
    Right: "Direction"
    UpLeft: "Direction"
    UpRight: "Direction"
    DownLeft: "Direction"
    DownRight: "Direction"

    All: tuple[
        "Direction",
        "Direction",
        "Direction",
        "Direction",
        "Direction",
        "Direction",
        "Direction",
        "Direction",
    ]
    Cardinals: tuple["Direction", "Direction", "Direction", "Direction"]
    Diagonals: tuple["Direction", "Direction", "Direction", "Direction"]

    _names: dict["Direction", str]

    __slots__ = ["x", "y"]

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __neg__(self):
        return Direction(-self.x, -self.y)

    def __iter__(self):
        yield self.x
        yield self.y
    
    def __eq__(self, other: "Direction"):
        return other is not None and self.x == other.x and self.y == other.y

    def __ne__(self, other: "Direction"):
        return self.x != other.x or self.y != other.y

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
    Direction.Up: "up",
    Direction.Down: "down",
    Direction.Left: "left",
    Direction.Right: "right",
    Direction.UpLeft: "up.left",
    Direction.UpRight: "up.right",
    Direction.DownLeft: "down.left",
    Direction.DownRight: "down.right",
}
