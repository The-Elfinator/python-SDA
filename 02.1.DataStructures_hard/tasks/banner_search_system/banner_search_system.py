import heapq
from collections import defaultdict
import typing as tp


def normalize(
        text: str
        ) -> str:
    """
    Removes punctuation and digits and convert to lower case
    :param text: text to normalize
    :return: normalized query
    """
    return ''.join([c.lower() for c in text if c.isalpha() or c.isspace()])


def get_words(
        query: str
        ) -> list[str]:
    """
    Split by words and leave only words with letters greater than 3
    :param query: query to split
    :return: filtered and split query by words
    """
    return [word for word in query.split() if len(word) > 3]


def build_index(
        banners: list[str]
        ) -> dict[str, list[int]]:
    """
    Create index from words to banners ids with preserving order and without repetitions
    :param banners: list of banners for indexation
    :return: mapping from word to banners ids
    """
    d: dict[str, set[int]] = defaultdict(set)
    for i in range(len(banners)):
        for word in get_words(normalize(banners[i])):
            d[word].add(i)
    return {k: list(v) for k, v in d.items()}


def __merge__(seq: tp.Sequence[tp.Sequence[int]]) -> list[int]:
    heap: list[tuple[int, int]] = []
    k = len(seq)
    indexes = [0 for _ in range(k)]  # which indexes are now in heap
    for i in range(k):
        if len(seq[i]) != 0:
            heapq.heappush(heap, (seq[i][0], i))
    ret: list[int] = []
    while len(heap) != 0:
        elem, ind = heapq.heappop(heap)
        ret.append(elem)
        indexes[ind] += 1
        if indexes[ind] < len(seq[ind]):
            heapq.heappush(heap, (seq[ind][indexes[ind]], ind))
    return ret


def get_banner_indices_by_query(
        query: str,
        index: dict[str, list[int]]
        ) -> list[int]:
    """
    Extract banners indices from index, if all words from query contains in indexed banner
    :param query: query to find banners
    :param index: index to search banners
    :return: list of indices of suitable banners
    """
    query_words: list[str] = get_words(normalize(query))
    n: int = len(query_words)
    seq: list[list[int]] = []
    for word in query_words:
        seq.append(index[word]) if word in index.keys() else seq.append([])
    for i in range(len(seq)):
        seq[i].sort()
    merged_seq = __merge__(seq)
    ret: list[int] = []
    left = 0
    right = n - 1 if n <= len(merged_seq) and n != 0 else 0
    while right < len(merged_seq):
        if merged_seq[left] == merged_seq[right]:
            ret.append(merged_seq[left])
        left += 1
        right += 1
    return ret


#########################
# Don't change this code
#########################

def get_banners(
        query: str,
        index: dict[str, list[int]],
        banners: list[str]
        ) -> list[str]:
    """
    Extract banners matched to queries
    :param query: query to match
    :param index: word-banner_ids index
    :param banners: list of banners
    :return: list of matched banners
    """
    indices = get_banner_indices_by_query(query, index)
    return [banners[i] for i in indices]

#########################
