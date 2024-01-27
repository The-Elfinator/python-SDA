import typing as tp

T = tp.TypeVar('T', int, float)


class Pair(tp.Generic[T]):
    def __init__(self, first: T, second: T) -> None:
        self._first: T = first
        self._second: T = second

    def sum(self) -> T:
        return self._first + self._second

    def first(self) -> T:
        return self._first

    def second(self) -> T:
        return self._second

    def __iadd__(self, pair: 'Pair[T]') -> 'Pair[T]':
        self._first += pair.first()
        self._second += pair.second()
        return self
