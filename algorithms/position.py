from algorithms import Direction


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
        return self.x == other.x and self.y == other.y

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
