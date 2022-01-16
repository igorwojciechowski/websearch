#!/usr/bin/env python3
import argparse
import asyncio
from multiprocessing import Semaphore
from aiohttp import ClientSession, ClientConnectorError


def read_wordlist(wordlist: str) -> list:
    """
    Returns a list of words read from wordlist file
    :param wordlist: path to wordlist file
    """
    with open(wordlist, 'r', encoding='utf-8') as _file:
        return [_.replace('\n', '') for _ in _file.readlines()]


async def fetch(session: ClientSession, target: str, path: str) -> None:
    """
    Sends a request to a given URL and returns formatted result
    :param session: http client session
    :param target: target URL
    :param path: path concatenated to the target URL
    """
    url = f"{target}/{path}"
    try:
        response = await session.request(method='GET', url=url, allow_redirects=False)
        content_length = len(str(await response.content.read()))
        print(f"{url:30}\t{response.status:5}\t{content_length:8}")
    except ClientConnectorError:
        return


async def threaded(sem: Semaphore, session: ClientSession, url: str, path: str):
    async with sem:
        return await fetch(session=session, target=url, path=path)


async def work(sem, url: str, wordlist: list):
    async with ClientSession() as session:
        tasks = []
        for word in wordlist:
            tasks.append(threaded(sem, session=session, url=url, path=word))
        await asyncio.gather(*tasks)


ARGPARSER = argparse.ArgumentParser()
ARGPARSER.add_argument('-u', '--url', type=str,
                       help='URL to be enumerated', required=True)
ARGPARSER.add_argument('-w', '--wordlist', type=str,
                       help='path to a wordlist', required=True)
ARGPARSER.add_argument('-t', '--threads', type=int,
                       help='number of threads', default=30)
ARGS = ARGPARSER.parse_args()

URL = ARGS.url
WORDLIST = read_wordlist(ARGS.wordlist)
THREADS = ARGS.threads
SEMAPHORE = asyncio.Semaphore(THREADS)

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(work(SEMAPHORE, URL, WORDLIST))
finally:
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
