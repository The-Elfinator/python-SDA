def get_fizz_buzz(n: int) -> list[int | str]:
    """
    If value divided by 3 - "Fizz",
       value divided by 5 - "Buzz",
       value divided by 15 - "FizzBuzz",
    else - value.
    :param n: size of sequence
    :return: list of values.
    """
    return ["Fizz"*(x % 3 == 0) + "Buzz"*(x % 5 == 0) or x for x in range(1, n+1)]
