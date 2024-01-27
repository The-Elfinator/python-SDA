import typing as tp

T = tp.TypeVar('T', covariant=True)


class Gettable(tp.Protocol[T]):
    def __getitem__(self, item: int) -> T:
        pass

    def __len__(self) -> int:
        pass


def get(container: Gettable[T], index: int) -> tp.Optional[T]:
    if container:
        return container[index]

    return None
