import asyncio
from concurrent.futures import ThreadPoolExecutor

import aiohttp
import requests


async def async_fetch(session: aiohttp.ClientSession, url: str) -> str:
    """
    Asyncronously fetch (get-request) single url using provided session
    :param session: aiohttp session object
    :param url: target http url
    :return: fetched text
    """
    async with session.get(url) as response:
        return await response.text()


async def async_requests(urls: list[str]) -> list[str]:
    """
    Concurrently fetch provided urls using aiohttp
    :param urls: list of http urls ot fetch
    :return: list of fetched texts
    """
    async with asyncio.TaskGroup() as task_group:
        tasks = [task_group.create_task(async_fetch(aiohttp.ClientSession(), url)) for url in urls]
    return [task.result() for task in tasks]


def sync_fetch(session: requests.Session, url: str) -> str:
    """
    Syncronously fetch (get-request) single url using provided session
    :param session: requests session object
    :param url: target http url
    :return: fetched text
    """
    return session.get(url).text


def threaded_requests(urls: list[str]) -> list[str]:
    """
    Concurrently fetch provided urls with requests in different threads
    :param urls: list of http urls ot fetch
    :return: list of fetched texts
    """
    with ThreadPoolExecutor(max_workers=len(urls)) as executor:
        responses = [executor.submit(sync_fetch, requests.session(), url) for url in urls]
        return [resp.result() for resp in responses]
