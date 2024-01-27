import typing as tp


def reformat_git_log(inp: tp.IO[str], out: tp.IO[str]) -> None:
    """Reads git log from `inp` stream, reformats it and prints to `out` stream

    Expected input format: `<sha-1>\t<date>\t<author>\t<email>\t<message>`
    Output format: `<first 7 symbols of sha-1>.....<message>`
    """
    sha_length = 7
    line_max_length = 80
    rest = line_max_length - sha_length + 1
    for line in inp.readlines():
        content = line.split('\t')
        out.write(content[0][:sha_length] + content[-1].rjust(rest, '.'))
