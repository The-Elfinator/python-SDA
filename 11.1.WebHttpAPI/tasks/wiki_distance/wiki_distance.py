from pathlib import Path

import requests

from bs4 import BeautifulSoup

# Directory to save your .json files to
# NB: create this directory if it doesn't exist
SAVED_JSON_DIR = Path(__file__).parent / 'visited_paths'


def get_link(content: str, visited_urls: set[str]) -> tuple[str | None, set[str]]:
    soup = BeautifulSoup(content, "lxml", parser="html.parser")
    body = soup.find('body')
    all_paragraphs = body.select('p')
    wrong_paragraphs = body.select('table p')
    paragraph = None
    for p in all_paragraphs:
        if p not in wrong_paragraphs and len(p.select('a')) > 0:
            for a in p.select('a'):
                if a.get('href') is not None:
                    paragraph = p
                    break
            if paragraph is not None:
                break
    if paragraph is None:
        return None, visited_urls
    references = paragraph.select('a')
    for ref in references:
        # print(f"\t{ref=}")
        href = ref.get('href')
        if href.startswith('/wiki'):
            href = "https://ru.wikipedia.org" + href
        link: str = href
        title: str = ref.get('title')
        # print(f"\t{link=}, {title=}")
        if link is None or title is None:
            continue
        if link not in visited_urls:
            return link, visited_urls.union({link})
    return None, visited_urls
    # for word in str(p).split():
    #     if word.startswith("href="):
    #         references.append(word[6:-1])


def distance(source_url: str, target_url: str) -> int | None:
    """Amount of wiki articles which should be visited to reach the target one
    starting from the source url. Assuming that the next article is choosing
    always as the very first link from the first article paragraph (tag <p>).
    If the article does not have any paragraph tags or any links in the first
    paragraph then the target is considered unreachable and None is returned.
    If the next link is pointing to the already visited article, it should be
    discarded in favor of the second link from this paragraph. And so on
    until the first not visited link will be found or no links left in paragraph.
    NB. The distance between neighbour articles (one is pointing out to the other)
    assumed to be equal to 1.
    :param source_url: the url of source article from wiki
    :param target_url: the url of target article from wiki
    :return: the distance calculated as described above
    """
    current_url = source_url
    dist: int = 0
    visited_urls = {current_url}
    while current_url != target_url:
        # print(f"{current_url=}")
        response: requests.Response = requests.get(source_url)
        if response.ok:
            response.encoding = "utf-8"
            next_url, visited_urls = get_link(response.text, visited_urls)
            # print(f"{next_url=}")
            # print(f"{visited_urls=}")
            if next_url is None:
                return None
            current_url = next_url
            dist += 1
    return dist

# dst = distance(wiki_url('Git'), wiki_url('Система_управления_версиями'))
# assert dst == 1, f"Expected 1, found {dst}"
#
# dst = distance(wiki_url('Википедия'), wiki_url('Математика'))
# assert dst == 10, f"Expected 10, found {dst}"
