

from algorithms import Random


class RandomEntry:
    def __init__(self, name: str, weight: float) -> None:
        self.name = name
        self.weigth = weight


class RandomTable:
    def __init__(self) -> None:
        self.totalWeight = 0
        self.entries: list[RandomEntry] = []

    def add(self, name: str, weight: float) -> 'RandomTable':
        self.totalWeight += weight
        self.entries.append(RandomEntry(name, weight))
        return self

    def roll(self, rand: Random) -> str:
        if self.totalWeight == 0:
            return ""

        u = rand.nextDouble() * self.totalWeight
        for entry in self.entries:
            if u < entry.weigth:
                return entry.name
            u -= entry.weigth
        return ""
