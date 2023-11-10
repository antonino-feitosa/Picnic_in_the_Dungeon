from algorithms import Point


class Dimension:
    __slof__ = ["width", "height"]

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def __contains__(self, element: Point):
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