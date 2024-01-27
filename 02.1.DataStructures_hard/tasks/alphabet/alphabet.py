import enum
from queue import LifoQueue


class Status(enum.Enum):
    NEW = 0
    EXTRACTED = 1
    FINISHED = 2


def extract_alphabet(
        graph: dict[str, set[str]]
        ) -> list[str]:
    """
    Extract alphabet from graph
    :param graph: graph with partial order
    :return: alphabet
    """
    status: dict[str, Status] = {v: Status.NEW for v in graph}
    alphabet: list[str] = []
    in_alpha: dict[str, bool] = {v: False for v in graph}
    stack: LifoQueue[str] = LifoQueue()
    for v in graph:
        if status[v] == Status.NEW:
            stack.put(v)
            while not stack.empty():
                v_from = stack.get()
                stack.put(v_from)
                if status[v_from] == Status.FINISHED:
                    stack.get()
                    if not in_alpha[v_from]:
                        alphabet.append(v_from)
                        in_alpha[v_from] = True
                    continue
                if status[v_from] == Status.EXTRACTED:
                    status[v_from] = Status.FINISHED
                    stack.get()
                    if not in_alpha[v_from]:
                        alphabet.append(v_from)
                        in_alpha[v_from] = True
                    continue
                status[v_from] = Status.EXTRACTED
                for v_to in graph[v_from]:
                    if status[v_to] == Status.NEW:
                        stack.put(v_to)
    return alphabet[::-1]


def build_graph(
        words: list[str]
        ) -> dict[str, set[str]]:
    """
    Build graph from ordered words. Graph should contain all letters from words
    :param words: ordered words
    :return: graph
    """
    graph: dict[str, set[str]] = {letter: set() for word in words for letter in word}
    for i in range(len(words) - 1):
        for j in range(min(len(words[i]), len(words[i+1]))):
            ch_1, ch_2 = words[i][j], words[i+1][j]
            if ch_1 == ch_2:
                continue
            graph[ch_1].add(ch_2)
            break
    return graph


#########################
# Don't change this code
#########################

def get_alphabet(
        words: list[str]
        ) -> list[str]:
    """
    Extract alphabet from sorted words
    :param words: sorted words
    :return: alphabet
    """
    graph = build_graph(words)
    return extract_alphabet(graph)

#########################
