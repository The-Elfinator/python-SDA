import typing as tp

T = tp.TypeVar("T", bound=tp.SupportsFloat, covariant=True)

class A(tp.Generic[T]):
    def __init__(self, a: T) -> None:
        self._a: tp.SupportsFloat = a

    def increment(self) -> float:
        self._a = float(self._a) + 1
        return self._a


A(1)
A(1.2)
A(True)
A("1.3")

class B:
    def __float__(self) -> float:
        return 1.1

A(B())

def g(a: A[int]) -> None:
    pass

g(A(1.4))
g(A(True))
