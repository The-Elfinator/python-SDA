from types import FunctionType, CodeType
from typing import Any

CO_VARARGS = 4
CO_VARKEYWORDS = 8

ERR_TOO_MANY_POS_ARGS = 'Too many positional arguments'
ERR_TOO_MANY_KW_ARGS = 'Too many keyword arguments'
ERR_MULT_VALUES_FOR_ARG = 'Multiple values for arguments'
ERR_MISSING_POS_ARGS = 'Missing positional arguments'
ERR_MISSING_KWONLY_ARGS = 'Missing keyword-only arguments'
ERR_POSONLY_PASSED_AS_KW = 'Positional-only argument passed as keyword argument'


def parse_args(func_code: CodeType, posonly_slice: slice, pos_or_kw_slice: slice, kwonly_slice: slice,
               args: tuple[Any, ...], kwargs: dict[str, Any]) \
        -> tuple[
            dict[Any, Any],
            dict[Any, Any],
            frozenset[Any],
            tuple[Any, ...],
            frozenset[Any],
            dict[str, Any],
            dict[str, Any],
            frozenset[Any],
            dict[str, Any]
        ]:
    # parse args
    parsed_posonlyargs = dict(zip(
        func_code.co_varnames[posonly_slice],
        args[posonly_slice]
    ))
    parsed_posargs = dict(zip(
        func_code.co_varnames[pos_or_kw_slice],
        args[pos_or_kw_slice]
    ))
    varargs = args[func_code.co_argcount:]

    # parse kwargs
    posonly_names = frozenset(func_code.co_varnames[posonly_slice])
    pos_or_kw_names = frozenset(func_code.co_varnames[pos_or_kw_slice])
    kwonly_names = frozenset(func_code.co_varnames[kwonly_slice])

    parsed_kwargs = {}
    parsed_kwonlyargs = {}
    varkwargs = {}
    for k, v in kwargs.items():
        if k in pos_or_kw_names:
            parsed_kwargs[k] = v
        elif k in kwonly_names:
            parsed_kwonlyargs[k] = v
        else:
            varkwargs[k] = v
    return (parsed_posonlyargs, parsed_posargs, posonly_names, varargs,
            pos_or_kw_names, parsed_kwargs, parsed_kwonlyargs, kwonly_names, varkwargs)


def check_results(defaults: dict[Any, Any], has_varargs: bool, has_varkwargs: bool, kwonly_names: frozenset[Any],
                  kwonlydefaults: dict[str, Any], parsed_kwargs: dict[str, Any], parsed_kwonlyargs: dict[str, Any],
                  parsed_posargs: dict[str, Any], parsed_posonlyargs: dict[str, Any],
                  pos_or_kw_names: frozenset[str], posonly_names: frozenset[str],
                  varargs: tuple[Any, ...], varkwargs: dict[str, Any]) -> None:
    if parsed_posargs.keys() & parsed_kwargs.keys():
        raise TypeError(ERR_MULT_VALUES_FOR_ARG)
    if varkwargs.keys() & posonly_names and not has_varkwargs:
        raise TypeError(ERR_POSONLY_PASSED_AS_KW)
    if varkwargs and not has_varkwargs:
        raise TypeError(ERR_TOO_MANY_KW_ARGS)
    if varargs and not has_varargs:
        raise TypeError(ERR_TOO_MANY_POS_ARGS)
    if (
            (posonly_names | pos_or_kw_names)
            - parsed_posonlyargs.keys()
            - parsed_posargs.keys()
            - parsed_kwargs.keys()
            - defaults.keys()
    ):
        raise TypeError(ERR_MISSING_POS_ARGS)
    if kwonly_names - parsed_kwonlyargs.keys() - kwonlydefaults.keys():
        raise TypeError(ERR_MISSING_KWONLY_ARGS)


def make_result(defaults: dict[str, Any], func_code: CodeType, has_varargs: bool, has_varkwargs: bool,
                kwonlydefaults: Any, parsed_kwargs: Any, parsed_kwonlyargs: Any,
                parsed_posargs: Any, parsed_posonlyargs: Any, varargs: Any, varkwargs: Any) -> dict[str, Any]:
    bound_args = {}
    bound_args.update(defaults)
    bound_args.update(kwonlydefaults)
    bound_args.update(parsed_posonlyargs)
    bound_args.update(parsed_posargs)
    bound_args.update(parsed_kwargs)
    bound_args.update(parsed_kwonlyargs)
    if has_varargs:
        varargs_name = func_code.co_varnames[func_code.co_argcount + func_code.co_kwonlyargcount]
        bound_args[varargs_name] = varargs
    if has_varkwargs:
        varkwargs_name = func_code.co_varnames[func_code.co_argcount + func_code.co_kwonlyargcount + has_varargs]
        bound_args[varkwargs_name] = varkwargs
    return bound_args


def bind_args(func: FunctionType, *args: Any, **kwargs: Any) -> dict[str, Any]:
    """Bind values from `args` and `kwargs` to corresponding arguments of `func`

    :param func: function to be inspected
    :param args: positional arguments to be bound
    :param kwargs: keyword arguments to be bound
    :return: `dict[argument_name] = argument_value` if binding was successful,
             raise TypeError with one of `ERR_*` error descriptions otherwise
    """
    func_code = func.__code__
    default_values = func.__defaults__ or ()
    kwonlydefaults = func.__kwdefaults__ or {}

    has_varargs = bool(func_code.co_flags & CO_VARARGS)
    has_varkwargs = bool(func_code.co_flags & CO_VARKEYWORDS)

    posonly_slice = slice(None, func_code.co_posonlyargcount)
    pos_or_kw_slice = slice(func_code.co_posonlyargcount, func_code.co_argcount)
    kwonly_slice = slice(func_code.co_argcount, func_code.co_argcount + func_code.co_kwonlyargcount)
    defaults_slice = slice(func_code.co_argcount - len(default_values), func_code.co_argcount)

    default_names = func_code.co_varnames[defaults_slice]
    defaults = dict(zip(default_names, default_values))

    (parsed_posonlyargs, parsed_posargs, posonly_names, varargs,
     pos_or_kw_names, parsed_kwargs, parsed_kwonlyargs, kwonly_names, varkwargs) \
        = parse_args(func_code, posonly_slice, pos_or_kw_slice, kwonly_slice, args, kwargs)

    check_results(defaults, has_varargs, has_varkwargs, kwonly_names, kwonlydefaults, parsed_kwargs, parsed_kwonlyargs,
                  parsed_posargs, parsed_posonlyargs, pos_or_kw_names, posonly_names, varargs, varkwargs)

    return make_result(defaults, func_code, has_varargs, has_varkwargs, kwonlydefaults, parsed_kwargs,
                       parsed_kwonlyargs, parsed_posargs, parsed_posonlyargs, varargs, varkwargs)
