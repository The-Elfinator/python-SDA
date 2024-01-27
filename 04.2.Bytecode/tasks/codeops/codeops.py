import dis
import queue
import types


def count_operations(source_code: types.CodeType) -> dict[str, int]:
    """Count byte code operations in given source code.

    :param source_code: the bytecode operation names to be extracted from
    :return: operation counts
    """
    instructions: queue.Queue[dis.Instruction] = queue.Queue()
    for _ in dis.get_instructions(source_code):
        instructions.put(_)
    result: dict[str, int] = dict()
    while not instructions.empty():
        inst = instructions.get()
        name = inst.opname
        if isinstance(inst.argval, types.CodeType):
            for _ in dis.get_instructions(inst.argval):
                instructions.put(_)

        if name not in result.keys():
            result[name] = 1
        else:
            result[name] += 1
    return result
