"""
Simplified VM code which works for some cases.
You need extend/rewrite code to pass all cases.
"""

import builtins
import dis
import types
import typing as tp

# def eprint(*args, **kwargs):
#     print(*args, file=sys.stderr, **kwargs)

fl = open("debug_n", "w")

CO_VARARGS = 4
CO_VARKEYWORDS = 8

ERR_TOO_MANY_POS_ARGS = 'Too many positional arguments'
ERR_TOO_MANY_KW_ARGS = 'Too many keyword arguments'
ERR_MULT_VALUES_FOR_ARG = 'Multiple values for arguments'
ERR_MISSING_POS_ARGS = 'Missing positional arguments'
ERR_MISSING_KWONLY_ARGS = 'Missing keyword-only arguments'
ERR_POSONLY_PASSED_AS_KW = 'Positional-only argument passed as keyword argument'


def bind_args(pos_defaults: tuple[tp.Any], code: tp.Any, *args: tp.Any, **kwargs: tp.Any) -> dict[str, tp.Any]:
    """Bind values from `args` and `kwargs` to corresponding arguments of `func`

    :param func: function to be inspected
    :param args: positional arguments to be bound
    :param kwargs: keyword arguments to be bound
    :return: `dict[argument_name] = argument_value` if binding was successful,
             raise TypeError with one of `ERR_*` error descriptions otherwise
    """
    result: dict[str, tp.Any] = {}
    flags = code.co_flags
    has_args = flags & CO_VARARGS != 0
    has_kwargs = flags & CO_VARKEYWORDS != 0

    # for arg in args:
    positional_defaults = pos_defaults
    map_defaults = None
    if map_defaults is None:
        map_defaults = {}  # type: ignore

    variables = list(code.co_varnames)
    lc = code.co_nlocals - code.co_argcount - code.co_kwonlyargcount
    if has_args:
        lc -= 1

    if has_kwargs:
        lc -= 1
    for i in range(lc):
        variables.pop(len(variables) - 1)

    args_name = "args"
    kwargs_name = "kwargs"
    if has_kwargs:
        kwargs_name = variables.pop(len(variables) - 1)
    if has_args:
        args_name = variables.pop(len(variables) - 1)
    positional_only = code.co_posonlyargcount
    kw_only = code.co_kwonlyargcount

    pos_only_vars = variables[0:positional_only]
    kw_only_vars = variables[-kw_only:]
    middle = variables[positional_only:-kw_only]
    if kw_only == 0:
        kw_only_vars = []
        middle = variables[positional_only:]

    not_used_args = []

    for i in range(len(args)):
        if i < len(pos_only_vars):
            result[pos_only_vars[i]] = args[i]
            if pos_only_vars[i] in kwargs and not has_kwargs:
                raise TypeError(ERR_POSONLY_PASSED_AS_KW)
        elif i < len(pos_only_vars) + len(middle):
            result[middle[i - len(pos_only_vars)]] = args[i]
            if middle[i - len(pos_only_vars)] in kwargs:
                raise TypeError(ERR_MULT_VALUES_FOR_ARG)
        else:
            if has_args:
                not_used_args.append(args[i])
            else:
                raise TypeError(ERR_TOO_MANY_POS_ARGS)

    if len(result) < len(pos_only_vars):
        i = len(result)
        if i >= len(pos_only_vars) + len(middle) - len(positional_defaults):
            for i in range(i, len(pos_only_vars)):
                if pos_only_vars[i] in kwargs and not has_kwargs:
                    raise TypeError(ERR_POSONLY_PASSED_AS_KW)
                result[pos_only_vars[i]] = positional_defaults[-(len(pos_only_vars) + len(middle) - i)]
        elif pos_only_vars[len(result) - 1] in kwargs and not has_kwargs:
            raise TypeError(ERR_POSONLY_PASSED_AS_KW)
        else:
            raise TypeError(ERR_MISSING_POS_ARGS)

    used_kwargs = set([])

    for i in range(len(result), len(variables)):
        if i < len(pos_only_vars) + len(middle):
            if middle[i - len(pos_only_vars)] in kwargs:
                result[middle[i - len(pos_only_vars)]] = kwargs[middle[i - len(pos_only_vars)]]
                used_kwargs.add(middle[i - len(pos_only_vars)])
            elif i >= len(pos_only_vars) + len(middle) - len(positional_defaults):
                result[middle[i - len(pos_only_vars)]] = positional_defaults[-(len(pos_only_vars) + len(middle) - i)]
            else:
                raise TypeError(ERR_MISSING_POS_ARGS)
        else:
            var = kw_only_vars[i - len(pos_only_vars) - len(middle)]
            if var in kwargs:
                result[var] = kwargs[var]
                used_kwargs.add(var)
            elif var in map_defaults:
                result[var] = map_defaults[var]
            else:
                raise TypeError(ERR_MISSING_KWONLY_ARGS)

    not_used_kwargs = {}
    for k, v in kwargs.items():
        if k not in used_kwargs:
            not_used_kwargs[k] = v

    if not has_kwargs:
        if len(not_used_kwargs) > 0:
            raise TypeError(ERR_TOO_MANY_KW_ARGS)
    else:
        result[kwargs_name] = not_used_kwargs

    if has_args:
        result[args_name] = tuple(not_used_args)
    return result



class Frame:
    """
    Frame header in cpython with description
        https://github.com/python/cpython/blob/3.11/Include/frameobject.h

    Text description of frame parameters
        https://docs.python.org/3/library/inspect.html?highlight=frame#types-and-members
    """

    def __init__(self,
                 frame_code: types.CodeType,
                 frame_builtins: dict[str, tp.Any],
                 frame_globals: dict[str, tp.Any],
                 frame_locals: dict[str, tp.Any],
                 frame_nested: list[dict[str, tp.Any]] | None = None) -> None:
        self.code = frame_code
        self.ptr = -1
        self.builtins = frame_builtins
        self.globals = frame_globals
        self.locals = frame_locals
        self.data_stack: tp.Any = []
        self.return_value = None
        self.returned = False
        if frame_nested is None:
            frame_nested = []
        self.frame_nested = frame_nested

    def top(self) -> tp.Any:
        return self.data_stack[-1]

    def pop(self) -> tp.Any:
        return self.data_stack.pop()

    def push(self, *values: tp.Any) -> None:
        self.data_stack.extend(values)

    def popn(self, n: int) -> tp.Any:
        """
        Pop a number of values from the value stack.
        A list of n values is returned, the deepest value first.
        """
        if n > 0:
            returned = self.data_stack[-n:]
            self.data_stack[-n:] = []
            return returned
        else:
            return []

    def run(self) -> tp.Any:
        # TODO-JUMP
        instructions = list(dis.get_instructions(self.code))
        while self.ptr < len(instructions) - 1:
            self.ptr += 1
            instruction = instructions[self.ptr]
            fl.write(instruction.__str__() + "\n")
            getattr(self, instruction.opname.lower() + "_op")(argval=instruction.argval, arg=instruction.arg)
            fl.write(f"stack: {self.data_stack}, globals: {self.globals}, locals: {self.locals}\n\n")
            if self.returned:
                return self.return_value

    def import_name_op(self, argval: str, **kwargs: tp.Any) -> None:
        level, from_list = self.popn(2)
        self.push(builtins.__import__(argval, globals(), locals(), from_list, level))

    def import_from_op(self, argval: str, **kwargs: tp.Any) -> None:
        mod = self.top()
        self.push(getattr(mod, argval))

    def load_build_class_op(self, **kwargs: tp.Any) -> None:
        self.push(builtins.__build_class__)

    def import_star_op(self, **kwargs: tp.Any) -> None:
        mod_val = self.pop()
        for item in dir(mod_val):
            if item[0] != "_":
                self.globals[item] = getattr(mod_val, item)

    def extended_arg_op(self, **kwargs: tp.Any) -> None:
        pass

    def load_assertion_error_op(self, **kwargs: tp.Any) -> None:
        self.push(Exception)

    def kw_names_op(self, arg: str, **kwargs: tp.Any) -> None:
        raise NameError(arg)

    def delete_global_op(self, argval: str, **kwargs: tp.Any) -> None:
        if argval in self.globals:
            del self.globals[argval]
        else:
            raise NameError

    def get_iter_op(self, **kwargs: tp.Any) -> None:
        self.push(iter(self.pop()))

    def jump_forward_op(self, argval: int, **kwargs: tp.Any) -> None:
        self.ptr = self.__find_instruction(argval)

    def store_fast_op(self, argval: str, **kwargs: tp.Any) -> None:
        if argval in self.locals:
            self.push(self.locals[argval])
        else:
            for i in self.frame_nested:
                if argval in i:
                    self.push(i[argval])
                    break
        raise UnboundLocalError

    def for_iter_op(self, argval: int, **kwargs: tp.Any) -> None:
        try:
            it = next(self.top())
            if it is not None:
                self.push(it)
            else:
                self.pop()
                self.ptr = self.__find_instruction(argval)
        except StopIteration:
            self.pop()
            self.ptr = self.__find_instruction(argval)

    def contains_op_op(self, argval: bool, **kwargs: tp.Any) -> None:
        # argval == invert[bool]
        target = self.pop()
        el = self.pop()
        val = el in target
        val = not val if argval else val
        self.push(val)

    def build_slice_op(self, argval: int, **kwargs: tp.Any) -> None:
        # argval == argc[int]
        argc = argval
        if argc != 2 and argc != 3:
            raise NameError("error argument in build_slice_op")
        if argc == 2:
            end = self.pop()
            start = self.pop()
            self.push(slice(start, end))
        else:
            step = self.pop()
            end = self.pop()
            start = self.pop()
            self.push(slice(start, end, step))

    def unary_positive_op(self, **kwargs: tp.Any) -> None:
        self.push(+self.pop())

    def raise_varargs_op(self, arg: int, **kwargs: tp.Any) -> None:
        if arg == 0:
            raise
        elif arg == 1:
            e = self.pop()
            raise e
        elif arg == 2:
            cause = self.pop()
            e = self.pop()
            raise e(cause)
        raise NameError

    def binary_subscr_op(self, **kwargs: tp.Any) -> None:
        tos = self.pop()
        tos1 = self.pop()
        self.push(tos1[tos])

    def store_attr_op(self, argval: str, **kwargs: tp.Any) -> None:
        tos = self.pop()
        tos1 = self.pop()
        setattr(tos, argval, tos1)
        self.push(tos)

    def load_attr_op(self, argval: str, **kwargs: tp.Any) -> None:
        tos = self.pop()
        self.push(getattr(tos, argval))

    def delete_attr_op(self, argval: str, **kwargs: tp.Any) -> None:
        delattr(self.top(), argval)

    def delete_name_op(self, argval: str, **kwargs: tp.Any) -> None:
        if argval in self.locals:
            self.locals.pop(argval)
        elif argval in self.globals:
            self.globals.pop(argval)
        elif argval in self.builtins:
            self.builtins.pop(argval)
        else:
            raise NameError

    def build_set_op(self, argval: int, **kwargs: tp.Any) -> None:
        cnt = argval
        if cnt < 0:
            raise Exception(f"unexpected count {cnt} in build_set_op")
        values = []
        for i in range(cnt):
            values.append(self.pop())
        self.push(set(values))

    def build_tuple_op(self, argval: int, **kwargs: tp.Any) -> None:
        cnt = argval
        if cnt < 0:
            raise Exception(f"unexpected count {cnt} in build_tuple_op")
        values = []
        for i in range(cnt):
            values.append(self.pop())
        self.push(tuple(values))

    def unpack_sequence_op(self, argval: int, **kwargs: tp.Any) -> None:
        tos = self.pop()
        for i in tos[::-1]:
            self.push(i)

    def build_list_op(self, argval: int, **kwargs: tp.Any) -> None:
        cnt = argval
        if cnt < 0:
            raise Exception(f"unexpected count {cnt} in build_list_op")
        values = []
        for i in range(cnt):
            values.append(self.pop())
        self.push(list(values))

    def build_const_key_map_op(self, argval: int, **kwargs: tp.Any) -> None:
        cnt = argval
        assert cnt > 0
        keys = self.pop()
        values = self.popn(cnt)

        result = {}
        for i in range(cnt):
            result[keys[i]] = values[i]
        self.push(result)

    def build_map_op(self, argval: int, **kwargs: tp.Any) -> None:
        size = argval
        res = {}
        values = self.popn(size * 2)
        for i in range(0, size * 2, 2):
            res[values[i]] = values[i + 1]
        self.push(res)

    def list_extend_op(self, argval: int, **kwargs: tp.Any) -> None:
        indx = argval
        assert indx > 0
        seq = self.pop()
        list.extend(self.data_stack[-indx], seq)

    def set_update_op(self, argval: int, **kwargs: tp.Any) -> None:
        i = argval
        seq = self.pop()
        set.update(self.data_stack[-i], seq)

    def resume_op(self, **kwargs: tp.Any) -> None:
        pass

    def push_null_op(self, **kwargs: tp.Any) -> None:
        self.push(None)

    def precall_op(self, **kwargs: tp.Any) -> None:
        pass

    def call_op(self, argval: int, **kwargs: tp.Any) -> None:
        arg = argval
        """
        Operation description:
            https://docs.python.org/release/3.11.5/library/dis.html#opcode-CALL
        """

        arguments = self.popn(arg)

        f = self.pop()
        if callable(f):
            if len(self.data_stack) > 0 and self.top() is None:
                self.pop()
            self.push(f(*arguments))
        else:
            obj = f
            method = self.pop()
            self.push(getattr(obj, method)(*arguments))

    def load_name_op(self, argval: str, **kwargs: tp.Any) -> None:
        """
        Partial realization

        Operation description:
            https://docs.python.org/release/3.11.5/library/dis.html#opcode-LOAD_NAME
        """
        # TODO: parse all scopes
        arg = argval
        if arg in self.locals:
            self.push(self.locals[arg])
        elif arg in self.globals:
            self.push(self.globals[arg])
        elif arg in self.builtins:
            self.push(self.builtins[arg])
        else:
            raise NameError

    def load_global_op(self, argval: str, **kwargs: tp.Any) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.11.5/library/dis.html#opcode-LOAD_GLOBAL
        """
        # TODO: parse all scopes
        arg = argval
        if arg in self.globals:
            self.push(self.globals[arg])
        elif arg in self.builtins:
            self.push(self.builtins[arg])
        else:
            raise NameError

    def load_fast_op(self, argval: tp.Any, **kwargs: tp.Any) -> None:
        assert argval in self.locals
        self.push(self.locals[argval])

    def load_const_op(self, argval: tp.Any, **kwargs: tp.Any) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.11.5/library/dis.html#opcode-LOAD_CONST
        """
        self.push(argval)

    def return_value_op(self, **kwargs: tp.Any) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.11.5/library/dis.html#opcode-RETURN_VALUE
        """
        self.return_value = self.pop()
        self.returned = True

    def pop_top_op(self, **kwargs: tp.Any) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.11.5/library/dis.html#opcode-POP_TOP
        """
        self.pop()

    def make_function_op(self, arg: int, **kwargs: tp.Any) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.11.5/library/dis.html#opcode-MAKE_FUNCTION
        """
        code = self.pop()  # the code associated with the function (at TOS1)

        flags = arg
        pos_defaults = ()
        if flags & 1 != 0:
            pos_defaults = self.pop()

        # TODO: use arg to parse function defaults

        def f(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
            # TODO: parse input arguments using code attributes such as co_argcount

            parsed_args: dict[str, tp.Any] = bind_args(pos_defaults, code, *args, **kwargs)  # type: ignore

            f_locals = dict(self.locals)
            f_locals.update(parsed_args)
            res_frame = []
            res_frame.extend(self.frame_nested)
            res_frame.extend(f_locals)  # type: ignore
            frame = Frame(code, self.builtins, self.globals, f_locals, res_frame)  # Run code in prepared environment
            return frame.run()

        self.push(f)

    def store_name_op(self, argval: str, **kwargs: tp.Any) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.11.5/library/dis.html#opcode-STORE_NAME
        """
        arg = argval
        const = self.pop()

        self.locals[arg] = const

    def store_global_op(self, argval: str, **kwargs: tp.Any) -> None:
        arg = argval
        const = self.pop()
        self.globals[arg] = const

    def binary_op_op(self, argval: str, **kwargs: tp.Any) -> None:
        op = argval

        rhs = self.pop()
        lhs = self.pop()
        result = None

        if op == 0:
            result = lhs + rhs
        elif op == 1:
            result = lhs & rhs
        elif op == 2:
            result = lhs // rhs
        elif op == 3:
            result = lhs << rhs
        elif op == 4:
            # TODO:MATRIX
            result = lhs @ rhs
        elif op == 5:
            result = lhs * rhs
        elif op == 6:
            result = lhs % rhs
        elif op == 7:
            result = lhs | rhs
        elif op == 8:
            result = lhs ** rhs
        elif op == 9:
            result = lhs >> rhs
        elif op == 10:
            result = lhs - rhs
        elif op == 11:
            result = lhs / rhs
        elif op == 12:
            result = lhs ^ rhs
        elif op == 13:
            lhs += rhs
            result = lhs
        elif op == 14:
            lhs &= rhs
            result = lhs
        elif op == 15:
            lhs //= rhs
            result = lhs
        elif op == 16:
            lhs <<= rhs
            result = lhs
        elif op == 17:
            # TODO:MATRIX
            lhs @= rhs
            result = lhs
        elif op == 18:
            lhs *= rhs
            result = lhs
        elif op == 19:
            lhs %= rhs
            result = lhs
        elif op == 20:
            lhs |= rhs
            result = lhs
        elif op == 21:
            lhs **= rhs
            result = lhs
        elif op == 22:
            lhs >>= rhs
            result = lhs
        elif op == 23:
            lhs -= rhs
            result = lhs
        elif op == 24:
            lhs /= rhs
            result = lhs
        elif op == 25:
            lhs ^= rhs
            result = lhs
        else:
            raise NameError(op)
        self.push(result)

    def compare_op_op(self, argval: str, **kwargs: tp.Any) -> None:
        op = argval
        rhs = self.pop()
        lhs = self.pop()
        result = None
        if op == "<":
            result = lhs < rhs
        elif op == "<=":
            result = lhs <= rhs
        elif op == "==":
            result = lhs == rhs
        elif op == "!=":
            result = lhs != rhs
        elif op == ">":
            result = lhs > rhs
        elif op == ">=":
            result = lhs >= rhs
        else:
            raise NameError(op)
        self.push(result)

    def unary_negative_op(self, **kwargs: tp.Any) -> None:
        self.push(-self.pop())

    def unary_invert_op(self, **kwargs: tp.Any) -> None:
        self.push(~self.pop())

    def unary_not_op(self, **kwargs: tp.Any) -> None:
        self.push(not self.pop())

    def store_subscr_op(self, **kwargs: tp.Any) -> None:
        key = self.pop()
        container = self.pop()
        value = self.pop()
        container[key] = value
        self.push(container)

    def delete_subscr_op(self, **kwargs: tp.Any) -> None:
        key = self.pop()
        container = self.pop()
        del container[key]
        self.push(container)

    def setup_annotations_op(self, **kwargs: tp.Any) -> None:
        if "__annotations__" not in self.locals:
            self.locals["__annotations__"] = {}

    def jump_if_true_or_pop_op(self, argval: int, **kwargs: tp.Any) -> None:
        tos = self.top()
        if tos:
            self.ptr = self.__find_instruction(argval)
        else:
            self.pop()

    def jump_if_false_or_pop_op(self, argval: int, **kwargs: tp.Any) -> None:
        tos = self.top()
        if not tos:
            self.ptr = self.__find_instruction(argval)
        else:
            self.pop()

    def __find_instruction(self, offset: int) -> int:
        for indx, instruction in enumerate(dis.get_instructions(self.code)):
            if instruction.offset == offset:
                return indx - 1
        raise IndexError()

    def pop_jump_forward_if_true_op(self, argval: int, **kwargs: tp.Any) -> None:
        tos = self.pop()
        if tos:
            self.ptr = self.__find_instruction(argval)

    def pop_jump_forward_if_false_op(self, argval: int, **kwargs: tp.Any) -> None:
        tos = self.pop()
        if not tos:
            self.ptr = self.__find_instruction(argval)

    def pop_jump_forward_if_none_op(self, argval: int, **kwargs: tp.Any) -> None:
        tos = self.pop()
        if tos is None:
            self.ptr = self.__find_instruction(argval)

    def jump_backward_op(self, argval: int, **kwargs: tp.Any) -> None:
        # TODO: check
        self.ptr = self.__find_instruction(argval)

    def load_method_op(self, argval: str, **kwargs: tp.Any) -> None:
        tos = self.pop()
        if argval in dir(tos):
            self.push(getattr(tos, argval))
        else:
            self.push(None)

    def copy_op(self, argval: int, **kwargs: tp.Any) -> None:
        self.push(self.data_stack[-argval])

    def swap_op(self, argval: int, **kwargs: tp.Any) -> None:
        (self.data_stack[-1], self.data_stack[-argval]) = (self.data_stack[-argval], self.data_stack[-1])

    def nop_op(self, **kwargs: tp.Any) -> None:
        pass

    def is_op_op(self, arg: int, **kwargs: tp.Any) -> None:
        rhs = self.pop()
        lhs = self.pop()

        if arg == 1:
            self.push(lhs is not rhs)
        else:
            self.push(lhs is rhs)

    def format_value_op(self, arg: int, **kwargs: tp.Any) -> None:
        value = self.pop()
        flags = arg
        if (flags & 0x03) == 0x00:
            pass
        elif (flags & 0x03) == 0x01:
            value = str(value)
        elif (flags & 0x03) == 0x02:
            value = repr(value)
        elif (flags & 0x03) == 0x03:
            value = ascii(value)
        elif (flags & 0x04) == 0x04:
            raise NameError("not implemented")
            # fmt_spec = self.pop()
            # if type(fmt_spec
        self.push(value)

    def build_string_op(self, arg: int, **kwargs: tp.Any) -> None:
        self.push("".join(map(str, self.popn(arg))))


class VirtualMachine:
    def run(self, code_obj: types.CodeType) -> None:
        """
        :param code_obj: code for interpreting
        """
        globals_context: dict[str, tp.Any] = {}
        frame = Frame(code_obj, builtins.globals()['__builtins__'], globals_context, globals_context)
        return frame.run()
