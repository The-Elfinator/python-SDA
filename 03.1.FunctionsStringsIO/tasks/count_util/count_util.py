def count_util(text: str, flags: str | None = None) -> dict[str, int]:
    """
    :param text: text to count entities
    :param flags: flags in command-like format - can be:
        * -m stands for counting characters
        * -l stands for counting lines
        * -L stands for getting length of the longest line
        * -w stands for counting words
    More than one flag can be passed at the same time, for example:
        * "-l -m"
        * "-lLw"
    Omitting flags or passing empty string is equivalent to "-mlLw"
    :return: mapping from string keys to corresponding counter, where
    keys are selected according to the received flags:
        * "chars" - amount of characters
        * "lines" - amount of lines
        * "longest_line" - the longest line length
        * "words" - amount of words
    """
    ret: dict[str, int] = {}
    characters_flag = "m"
    characters_key_word = "chars"
    lines_flag = "l"
    lines_key_word = "lines"
    longest_flag = "L"
    longest_key_word = "longest_line"
    words_flag = "w"
    words_key_word = "words"
    default_flags = "-m -l -L -w"
    for flag in flags.split() if flags is not None and len(flags) != 0 else default_flags.split():
        for k in flag[1:]:
            if k == characters_flag:
                ret[characters_key_word] = len(text)
            elif k == lines_flag:
                ret[lines_key_word] = text.count('\n')
            elif k == longest_flag:
                ret[longest_key_word] = 0 if len(text.splitlines()) == 0 \
                    else len(max(text.splitlines(), key=lambda string: len(string)))
            elif k == words_flag:
                ret[words_key_word] = len(text.split())
    return ret
