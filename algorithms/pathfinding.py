import heapq

from typing import Set
from typing import Dict
from typing import List
from typing import Tuple
from typing import Sequence

from algorithms import Position
from algorithms import Direction


class PathFinding:
    def __init__(self, ground: Set[Position], directions: Sequence[Direction]):
        self.ground = ground
        self.directions = directions

    def searchPath(self, source: Position, dest: Position) -> List[Position]:
        queue: List[Position] = [source]
        dist: Dict[Position, int] = {source: 0}
        previous: Dict[Position, Position] = dict()
        visited = set()

        while len(queue) > 0:
            list.sort(queue, key=lambda x: dist[x] if x in dist else 10000000)
            current = queue.pop(0)
            visited.add(current)
            if current == dest:
                return self._postProcess(dest, previous)
            for dir in self.directions:
                neighbor = dir + current
                if neighbor in self.ground and neighbor not in visited:
                    distance = neighbor.distanceDiamond(dest)
                    distance += dist[current]
                    distance += 1
                    if neighbor not in dist or distance < dist[neighbor]:
                        previous[neighbor] = current
                        dist[neighbor] = distance
                        queue.append(neighbor)
        return []

    def _postProcess(
        self, dest: Position, previous: Dict[Position, Position]
    ) -> List[Position]:
        path: List[Position] = []
        path.insert(0, dest)
        while dest in previous:
            next = previous[dest]
            dest = next
            path.insert(0, dest)
        return path