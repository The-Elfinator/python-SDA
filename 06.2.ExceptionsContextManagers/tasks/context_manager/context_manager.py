import sys
import traceback
from contextlib import contextmanager
from typing import Iterator, TextIO, Type


@contextmanager
def supresser(*types_: Type[BaseException]) -> Iterator[None]:
    try:
        yield None
    except Exception as e:
        if type(e) in types_:
            return
        else:
            raise e


@contextmanager
def retyper(type_from: Type[BaseException], type_to: Type[BaseException]) -> Iterator[None]:
    try:
        yield
    except type_from:
        _, value, traceback_ = sys.exc_info()
        if isinstance(value, type_from):
            raise type_to(*value.args).with_traceback(traceback_)
        raise


@contextmanager
def dumper(stream: TextIO | None = None) -> Iterator[None]:
    if stream is None:
        stream = sys.stderr
    try:
        yield
    except Exception:
        etype, value, traceback_ = sys.exc_info()
        message = ''.join(
            traceback.format_exception_only(etype, value)
        )
        stream.write(message)
        raise
