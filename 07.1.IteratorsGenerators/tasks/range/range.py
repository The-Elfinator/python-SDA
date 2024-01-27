from collections.abc import Iterable, Iterator, Sized


class RangeIterator(Iterator[int]):
    """The iterator class for Range"""

    def __init__(self, range_: 'Range') -> None:
        self.__range = range_
        self.__item = 0

    def __iter__(self) -> 'RangeIterator':
        return self

    def __next__(self) -> int:
        val = self.__range.start + self.__item * self.__range.step
        if self.__range.step < 0:
            if val > self.__range.stop:
                self.__item += 1
                return val
        else:
            if val < self.__range.stop:
                self.__item += 1
                return val
        raise StopIteration


class Range(Sized, Iterable[int]):
    """The range-like type, which represents an immutable sequence of numbers"""

    def __init__(self, *args: int) -> None:
        """
        :param args: either it's a single `stop` argument
            or sequence of `start, stop[, step]` arguments.
        If the `step` argument is omitted, it defaults to 1.
        If the `start` argument is omitted, it defaults to 0.
        If `step` is zero, ValueError is raised.
        """
        if len(args) == 0:
            raise Exception("args size")
        if len(args) == 1:
            self.stop = args[0]
            self.start = 0
            self.step = 1
        elif len(args) >= 2:
            self.start = args[0]
            self.stop = args[1]
            if len(args) == 3:
                self.step = args[2]
            else:
                self.step = 1
        self.__args = args

    def __iter__(self) -> 'RangeIterator':
        return RangeIterator(self)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        if self.step == 1:
            return f'range({self.start}, {self.stop})'
        return f'range({self.start}, {self.stop}, {self.step})'

    def __contains__(self, key: int) -> bool:
        if self.step > 0:
            return self.stop > key >= self.start and (key - self.start) % self.step == 0
        elif self.step < 0:
            return self.stop < key <= self.start and (key - self.start) % self.step == 0
        else:
            return key == self.start

    def __getitem__(self, key: int) -> int:
        if key < len(self):
            return self.start + self.step * key
        raise IndexError

    def __len__(self) -> int:
        if self.step < 0 and self.start <= self.stop:
            return 0
        if self.step > 0 and self.start >= self.stop:
            return 0
        res = (self.stop - self.start) // self.step
        if (self.start - self.stop) % self.step != 0:
            res += 1
        return res
