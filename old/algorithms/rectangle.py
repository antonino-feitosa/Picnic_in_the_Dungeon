
from algorithms import Position


class Rectangle:
    __slof__ = ["x1", "y1", "x2", "y2"]

    def __init__(self, x1:int, y1:int, x2:int, y2:int):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def __contains__(self, element: Position):
        return (
            element.x < self.x2
            and element.y < self.y2
            and element.x >= self.x1
            and element.y >= self.y1
        )

    def __iter__(self):
        yield self.x1
        yield self.y1
        yield self.x2
        yield self.y2

    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        return f"[({self.x1},{self.y1})x({self.x2},{self.y2})]"
