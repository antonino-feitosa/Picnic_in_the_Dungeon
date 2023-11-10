"""Bresenham Line Algorithm"""

from algorithms import Point


def plotLine(start: Point, end: Point) -> list[Point]:
    return _plotLine(start.x, start.y, end.x, end.y)


def _plotLine(x0: int, y0: int, x1: int, y1: int) -> list[Point]:
    if abs(y1 - y0) < abs(x1 - x0):
        if x0 > x1:
            result = _plotLineLow(x1, y1, x0, y0)
            result.reverse()
            return result
        else:
            return _plotLineLow(x0, y0, x1, y1)
    else:
        if y0 > y1:
            result = _plotLineHigh(x1, y1, x0, y0)
            result.reverse()
            return result
        else:
            return _plotLineHigh(x0, y0, x1, y1)


def _plotLineHigh(x0: int, y0: int, x1: int, y1: int) -> list[Point]:
    dx = x1 - x0
    dy = y1 - y0
    xi = 1
    if dx < 0:
        xi = -1
        dx = -dx
    D = (2 * dx) - dy
    x = x0
    points: list[Point] = []
    for y in range(y0, y1 + 1):
        points.append(Point(x, y))
        if D > 0:
            x = x + xi
            D = D + (2 * (dx - dy))
        else:
            D = D + 2 * dx
    return points


def _plotLineLow(x0: int, y0: int, x1: int, y1: int) -> list[Point]:
    dx = x1 - x0
    dy = y1 - y0
    yi = 1
    if dy < 0:
        yi = -1
        dy = -dy
    D = (2 * dy) - dx
    y = y0

    points: list[Point] = []
    for x in range(x0, x1 + 1):
        points.append(Point(x, y))
        if D > 0:
            y = y + yi
            D = D + (2 * (dy - dx))
        else:
            D = D + 2 * dy
    return points
