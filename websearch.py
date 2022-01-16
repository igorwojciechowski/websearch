#!/usr/bin/env python3
import argparse
import asyncio
from typing import Coroutine
import warnings
import sys
from aiohttp import ClientSession, ClientConnectorError

warnings.filterwarnings("ignore", category=DeprecationWarning)


def read_wordlist(wordlist: str) -> list:
    """
    Returns a list of words read from wordlist file
    :param wordlist: path to wordlist file
    """
    with open(wordlist, 'r', encoding='utf-8') as _file:
        return [_.replace('\n', '') for _ in _file.readlines()]


class ErrorsLimitExceededException(Exception):
    pass


class Websearch:

    def __init__(self, target: str, wordlist: str, threads: int, max_errors: int):
        self.target = target
        self.wordlist = read_wordlist(wordlist)
        self.semaphore = asyncio.Semaphore(threads)
        self.max_errors = max_errors
        self.errors = 0

    async def fetch(self, session: ClientSession, path: str) -> None:
        """
        Sends a request to a given URL and returns formatted result
        :param session: http client session
        :param target: target URL
        :param path: path concatenated to the target URL
        """
        url = f"{self.target}/{path}"
        try:
            response = await session.request(method='GET', url=url, allow_redirects=False, ssl=False)
            content_length = len(str(await response.content.read()))
            print(f"{url:30}\t{response.status:5}\t{content_length:8}")
            self.errors = 0
        except ClientConnectorError:
            self.errors += 1

    async def threaded(self, session: ClientSession, path: str) -> Coroutine:
        """
        
        """
        async with self.semaphore:
            if self.errors >= self.max_errors:
                raise ErrorsLimitExceededException
            return await self.fetch(session=session, path=path)

    async def run(self) -> None:
        async with ClientSession() as session:
            tasks = []
            for word in self.wordlist:
                tasks.append(self.threaded(session=session, path=word))
            await asyncio.gather(*tasks)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-u', '--url', type=str,
                           help='URL to be enumerated', required=True)
    argparser.add_argument('-w', '--wordlist', type=str,
                           help='path to a wordlist', required=True)
    argparser.add_argument('-t', '--threads', type=int,
                           help='number of threads', default=30)
    argparser.add_argument('--max_errors', type=int,
                           help='Max errors', default=30)
    args = argparser.parse_args()

    config = args.url, args.wordlist, args.threads, args.max_errors
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(Websearch(*config).run())
    except ErrorsLimitExceededException:
        for task in asyncio.Task.all_tasks():
            task.cancel()
        loop.stop()
        sys.stderr.write('Errors limit exceeded')
        sys.exit(1)
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
