def problem01() -> dict[int, str]:
    return {
        5: "К типу который может быть None применяется неподдерживаемая операция +",
        7: "В переменную типа int присваивается тип int | None"
    }


def problem02() -> dict[int, str]:
    return {
        5: "Оператор + нельзя применять к объекту, тип которого неизвестен (или тип object)"
    }


def problem03() -> dict[int, str]:
    return {
        9: "Ожидался тип set[int] аргумента, но получили set[float]",
        13: "Ожидался тип set[int] аргумента, но получили set[bool]"
    }


def problem04() -> dict[int, str]:
    return {
        9: "Ожидался тип set[int] аргумента, но получили set[float]"
    }


def problem05() -> dict[int, str]:
    return {
        11: "У результата ожидался тип 'B', получили тип 'A'"
    }


def problem06() -> dict[int, str]:
    return {
        15: "У класса предка тип переменной VAR объявлен 'S', получили тип 'T'"
    }


def problem07() -> dict[int, str]:
    return {
        25: "Ожидали тип A -> B, а получили A -> A",
        27: "Ожидали тип A -> B, а получили B -> A",
        28: "Ожидали тип А -> B, а получили B -> B"
    }


def problem08() -> dict[int, str]:
    return {
        6: "Функция len не может применяться к аргументу типа Iterable[str]",
        18: "Ожидался тип Iterable[str], получили тип 'A'",
        24: "Ожидался тип Iterable[str], получили тип 'B' (Iterable[int])"
    }


def problem09() -> dict[int, str]:
    return {
        32: "Неподдерживаемый оператор для типа 'Fooable'",
        34: "Ожидался тип Fooable, получили list",
        37: "Ожидался тип Fooable, получили 'C'",
        38: "Ожидался тип Fooable, получили функцию int -> None"
    }


def problem10() -> dict[int, str]:
    return {
        18: "Ожидался тип 'T' SupportsFloat, получили str",
        29: "Ожидался int, получили float"
    }
