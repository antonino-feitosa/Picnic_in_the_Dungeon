
import math
import random

from typing import Any, TypeVar, Sequence


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

    def nextDouble(self) -> float:
        return self.rand.random()

    def nextBool(self) -> bool:
        return self.nextDouble() < 0.5

    T = TypeVar("T")

    def choice(self, elements: Sequence[T]) -> T:
        index = self.choiceIndex(elements)
        return elements[index]

    def choiceIndex(self, elements: Sequence[Any]) -> int:
        size = len(elements)
        if size <= 0:
            raise ValueError("The list can not be empty!")
        return self.rand.randint(0, size - 1)

    def shuffle(self, elements: list) -> None:
        for i in range(len(elements)-1, 1, -1):
            j = self.nextRange(0, i+1)
            aux = elements[i]
            elements[i] = elements[j]
            elements[j] = aux

    def poissonSample(self, mean) -> int:
        uniform = self.nextDouble()
        prob = math.exp(-mean)
        cumulative = prob
        x = 0
        while uniform > cumulative:
            x += 1
            prob *= mean/x
            cumulative += prob
        return x
