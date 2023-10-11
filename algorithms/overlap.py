

from algorithms.direction import Direction


class Overlap:
    Empty: "Overlap"
    Up: "Overlap"
    Down: "Overlap"
    Left: "Overlap"
    Right: "Overlap"
    UpLeft: "Overlap"
    UpRight: "Overlap"
    DownLeft: "Overlap"
    DownRight: "Overlap"
    UpDown: "Overlap"
    LeftRight: "Overlap"
    UpDownLeft: "Overlap"
    UpDownRight: "Overlap"
    UpLeftRight: "Overlap"
    DownLeftRight: "Overlap"
    UpDownLeftRight: "Overlap"

    All: tuple[
        "Overlap",
        "Overlap",
        "Overlap",
        "Overlap",
        "Overlap",
        "Overlap",
        "Overlap",
        "Overlap",
    ]
    Cardinals: tuple["Overlap", "Overlap", "Overlap", "Overlap"]
    Diagonals: tuple["Overlap", "Overlap", "Overlap", "Overlap"]
    DirectionToOvelap: dict[Direction, "Overlap"] = dict()

    __slots__ = ["mask"]

    def __init__(self, mask: int = 0):
        self.mask = mask

    def inter(self, other: "Overlap") -> "Overlap":
        return Overlap(self.mask & other.mask)

    def union(self, other: "Overlap") -> "Overlap":
        return Overlap(self.mask | other.mask)

    def __contains__(self, other: "Overlap") -> "Overlap":
        return Overlap((self.mask & other.mask) == self.mask)

    def __len__(self) -> int:
        sum = 0
        for other in [Overlap.Up, Overlap.Down, Overlap.Left, Overlap.Right]:
            sum += (self.mask & other.mask) > 0
        return sum

    def __add__(self, other: "Overlap") -> "Overlap":
        return Overlap(self.mask | other.mask)

    def __sub__(self, other: "Overlap") -> "Overlap":
        return Overlap(self.mask & ~other.mask)

    @classmethod
    def fromDirection(cls, direction: Direction) -> "Overlap":
        if direction in Overlap.DirectionToOvelap:
            return Overlap.DirectionToOvelap[direction]
        return Overlap.Empty

    def __str__(self):
        str = ""
        str += "U" if Overlap.Up in self else "_"
        str += "D" if Overlap.Up in self else "_"
        str += "L" if Overlap.Up in self else "_"
        str += "R" if Overlap.Up in self else "_"
        return str

    def __repr__(self) -> str:
        return self.__str__()


Overlap.Empty = Overlap(0b0000)
Overlap.Up = Overlap(0b0001)
Overlap.Down = Overlap(0b0010)
Overlap.Left = Overlap(0b0100)
Overlap.Right = Overlap(0b1000)
Overlap.UpDown = Overlap(0b0001 | 0b0010)
Overlap.UpLeft = Overlap(0b0001 | 0b0100)
Overlap.UpRight = Overlap(0b0001 | 0b1000)
Overlap.DownLeft = Overlap(0b0010 | 0b0100)
Overlap.DownRight = Overlap(0b0010 | 0b1000)
Overlap.LeftRight = Overlap(0b0100 | 0b1000)
Overlap.UpDownLeft = Overlap(0b0001 | 0b0010 | 0b0100)
Overlap.UpDownRight = Overlap(0b0001 | 0b0010 | 0b1000)
Overlap.UpLeftRight = Overlap(0b0001 | 0b0100 | 0b1000)
Overlap.DownLeftRight = Overlap(0b0010 | 0b0100 | 0b1000)
Overlap.UpDownLeftRight = Overlap(0b0001 | 0b0010 | 0b0100 | 0b1000)

Overlap.DirectionToOvelap[Direction.Up] = Overlap.Up
Overlap.DirectionToOvelap[Direction.Down] = Overlap.Down
Overlap.DirectionToOvelap[Direction.Left] = Overlap.Left
Overlap.DirectionToOvelap[Direction.Right] = Overlap.Right
Overlap.DirectionToOvelap[Direction.UpLeft] = Overlap.UpLeft
Overlap.DirectionToOvelap[Direction.UpRight] = Overlap.UpRight
Overlap.DirectionToOvelap[Direction.DownLeft] = Overlap.DownLeft
Overlap.DirectionToOvelap[Direction.DownRight] = Overlap.DownRight
