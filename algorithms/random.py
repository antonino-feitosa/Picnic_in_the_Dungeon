import random

from typing import Any
from typing import TypeVar
from typing import Sequence


class Random:
    def __init__(self, seed: int | None = None):
        self.seed = seed
        self.rand = random.Random(seed)

    def nextInt(self, max: int) -> int:
        return self.rand.randint(0, max - 1)

    def nextRange(self, min: int, max: int) -> int:
        return self.rand.randint(min, max - 1)

    def nextNormal(self, mean: float = 0, sigma: float = 1) -> float:
        return self.rand.normalvariate(mean, sigma)

    T = TypeVar("T")

    def choice(self, elements: Sequence[T]) -> T:
        index = self.choiceIndex(elements)
        return elements[index]

    def choiceIndex(self, elements: Sequence[Any]) -> int:
        size = len(elements)
        if size <= 0:
            raise ValueError("The list can not be empty!")
        return self.rand.randint(0, size - 1)
