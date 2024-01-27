import typing as tp
import heapq


def merge(input_streams: tp.Sequence[tp.IO[bytes]], output_stream: tp.IO[bytes]) -> None:
    """
    Merge input_streams in output_stream
    :param input_streams: list of input streams. Contains byte-strings separated by "\n". Nonempty stream ends with "\n"
    :param output_stream: output stream. Contains byte-strings separated by "\n". Nonempty stream ends with "\n"
    :return: None
    """
    heap: list[tuple[int, int, bytes]] = []
    k = len(input_streams)
    for i in range(k):
        line = input_streams[i].readline()
        if len(line) != 0:
            heapq.heappush(heap, (int(line), i, line))
    while len(heap) != 0:
        item, ind, elem = heapq.heappop(heap)
        output_stream.write(elem)
        line = input_streams[ind].readline()
        if len(line) != 0:
            heapq.heappush(heap, (int(line), ind, line))
