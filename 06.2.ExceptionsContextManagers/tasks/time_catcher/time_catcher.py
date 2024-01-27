import time
import typing as tp
import traceback


class TimeoutException(Exception):

    def __init__(self, type_exc: str, *args: tp.Any):
        self.type_exc = type_exc
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self) -> str:
        error_msg = f'TimeoutException: found {self.type_exc}'
        if self.message is not None:
            error_msg += f' with message={self.message}'
        return error_msg


class SoftTimeoutException(TimeoutException):

    def __init__(self, *args: tp.Any):
        super().__init__("SoftTimeoutException", args)

    def __str__(self) -> str:
        return super.__str__(self)


class HardTimeoutException(TimeoutException):

    def __init__(self, *args: tp.Any):
        super().__init__("HardTimeoutException", args)

    def __str__(self) -> str:
        return super.__str__(self)


class TimeCatcher(object):

    def __init__(self, soft_timeout: float | None = None, hard_timeout: float | None = None):
        assert soft_timeout is None or soft_timeout > 0
        assert hard_timeout is None or hard_timeout > 0
        if soft_timeout is not None and hard_timeout is not None:
            assert soft_timeout <= hard_timeout
        self.__soft_timeout = soft_timeout
        self.__hard_timeout = hard_timeout

    def __enter__(self) -> 'TimeCatcher':
        self.__start = time.time()
        self.__time_required = 0.0
        self.__has_finished = False
        return self

    def __exit__(self, type_exc: TimeoutException, value: object, traceback_exc: traceback.TracebackException) -> bool:
        self.__finish = time.time()
        self.__time_required = self.__finish - self.__start
        self.__has_finished = True
        if self.__soft_timeout is not None and self.__soft_timeout < self.__time_required:
            raise SoftTimeoutException
        if self.__hard_timeout is not None and self.__hard_timeout < self.__time_required:
            raise HardTimeoutException
        return True

    def __float__(self) -> float:
        if self.__has_finished:
            self.__time_required = self.__finish - self.__start
        else:
            self.__time_required = time.time() - self.__start
        return float(self.__time_required)

    def __str__(self) -> str:
        return f'Time consumed: {self.__float__()}'
