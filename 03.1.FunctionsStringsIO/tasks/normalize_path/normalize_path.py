def normalize_path(path: str) -> str:
    """
    :param path: unix path to normalize
    :return: normalized path
    """
    stack: list[str] = []
    is_absolute_path = len(path) > 0 and path.startswith('/')
    for word in path.split('/'):
        if len(word) == 0:
            continue
        if word == ".":
            continue
        if word == "..":
            if len(stack) != 0:
                if stack[-1] == "..":
                    stack.append("..")
                else:
                    stack.pop()
            else:
                if is_absolute_path:
                    continue
                else:
                    stack.append("..")
            continue
        stack.append(word)
    if is_absolute_path:
        return '/' + '/'.join(stack)
    if len(stack) == 0:
        return "."
    return '/'.join(stack)
