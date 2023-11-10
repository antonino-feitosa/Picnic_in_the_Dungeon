
from typing import Sequence, Callable

from algorithms import Point
from algorithms import Direction


class PathFinding:
    def __init__(self, isExit: Callable[[Point],bool], directions: Sequence[Direction]):
        self.isExit = isExit
        self.directions = directions

    def searchPath(self, source: Point, dest: Point) -> list[Point]:
        queue: list[Point] = [source]
        dist: dict[Point, int] = {source: 0}
        previous: dict[Point, Point] = dict()
        visited = set()

        while len(queue) > 0:
            list.sort(queue, key=lambda x: dist[x] if x in dist else 10000000)
            current = queue.pop(0)
            visited.add(current)
            if current == dest:
                return self._postProcess(dest, previous)
            for dir in self.directions:
                neighbor = dir + current
                if self.isExit(neighbor) and neighbor not in visited:
                    distance = neighbor.distanceDiamond(dest)
                    distance += dist[current]
                    distance += 1
                    if neighbor not in dist or distance < dist[neighbor]:
                        previous[neighbor] = current
                        dist[neighbor] = distance
                        queue.append(neighbor)
        return []

    def _postProcess(
        self, dest: Point, previous: dict[Point, Point]
    ) -> list[Point]:
        path: list[Point] = []
        path.insert(0, dest)
        while dest in previous:
            next = previous[dest]
            dest = next
            path.insert(0, dest)
        return path
