import sys
import typing as tp
from pathlib import Path


def read_one_line(position: int, file: tp.BinaryIO) -> tuple[str, int]:
    if position < 1:
        return "", position
    position -= 1
    file.seek(position)
    char = file.read(1)
    result = ""
    if char != b'\n':
        result = char.decode('utf-8')
    while True:
        if position < 1:
            return result, position
        position -= 1
        file.seek(position)
        char = file.read(1)
        if char == b'\n':
            return result, position
        result = char.decode('utf-8') + result


def tail(filename: Path, lines_amount: int = 10, output: tp.IO[bytes] | None = None) -> None:
    """
    :param filename: file to read lines from (the file can be very large)
    :param lines_amount: number of lines to read
    :param output: stream to write requested amount of last lines from file
                   (if nothing specified stdout will be used)
    """
    out = output if output is not None else sys.stdout.buffer
    lines = []
    with open(filename, 'rb') as file:
        file.seek(0, 2)
        file_size = file.tell()
        start = file_size
        for _ in range(lines_amount):
            if start == 0:
                break
            (res, start) = read_one_line(start, file)
            lines.append(res)
    for line in reversed(lines):
        out.write(line.encode('utf-8') + b'\n')
