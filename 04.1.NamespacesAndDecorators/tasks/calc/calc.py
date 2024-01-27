import sys
import math
from typing import Any

PROMPT = '>>> '


def run_calc(context: dict[str, Any] | None = None) -> None:
    """Run interactive calculator session in specified namespace"""
    if context is None:
        context = dict()
    context['__builtins__'] = {}
    while True:
        print(PROMPT, end='')
        s = sys.stdin.readline()
        if s == '':
            print()
            break
        print(eval(s.rstrip('\n'), context))


if __name__ == '__main__':
    context = {'math': math}
    run_calc(context)
