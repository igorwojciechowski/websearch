#!/usr/bin/env python3
import argparse
import asyncio
from typing import Coroutine
import warnings
import sys
from aiohttp import ClientSession, ClientConnectorError


def read_wordlist(wordlist: str) -> list:
    """
    Returns a list of words read from wordlist file.

    :param wordlist: path to wordlist file
    :return: list of words read from wordlist
    """
    with open(wordlist, 'r', encoding='utf-8') as _file:
        return [_.replace('\n', '') for _ in _file.readlines()]


class ErrorsLimitExceededException(Exception):
    """
    Exception raised when max errors limit is reached.
    """


class Websearch:
    """
    HTTP content discovery class utilizing `asyncio` package.
    """

    def __init__(self, target: str, wordlist: str, threads: int, max_errors: int, filter_include: str, filter_exclude: str):
        self.target = target
        self.wordlist = read_wordlist(wordlist)
        self.semaphore = asyncio.Semaphore(threads)
        self.max_errors = max_errors
        self.filter_included = filter_include
        self.filter_excluded = filter_exclude
        self.errors = 0
    
    def is_filtered(self, status_code: int) -> bool:
        """
        Checks whether status code should be filtered.
        :param status_code: response status code
        :return: True if status code should be filtered
        """
        included = self.filter_included.split(",")
        excluded = self.filter_excluded.split(",")
        if str(status_code) in included:
            return False
        return str(status_code) in excluded

    async def fetch(self, session: ClientSession, path: str) -> None:
        """
        Sends a request to a given URL and prints formatted result.
        Increments errors whenever a connection error occurs or set them down to 0
        on successful request.

        :param session: http client session
        :param target: target URL
        :param path: path concatenated to the target URL
        """
        url = f"{self.target}/{path}"
        try:
            response = await session.request(method='GET', url=url, allow_redirects=False, ssl=False)
            content_length = len(str(await response.content.read()))
            if not self.is_filtered(response.status):
                print(f"{url:30}\t{response.status:5}\t{content_length:8}")
            self.errors = 0
        except ClientConnectorError:
            self.errors += 1

    async def fetch_threaded(self, session: ClientSession, path: str) -> Coroutine:
        """
        Creates a coroutine of a `fetch` function.

        :param session: http client session
        :param path: path to be concatenated with target URL
        :raise: `ErrorsLimitExceededException` when requests fail `max_errors` times in a row
        :return: coroutine
        """
        async with self.semaphore:
            if self.errors >= self.max_errors:
                raise ErrorsLimitExceededException
            return await self.fetch(session=session, path=path)

    async def run(self) -> None:
        """
        Creates tasks and run them concurrently.
        """
        async with ClientSession() as session:
            tasks = []
            for word in self.wordlist:
                tasks.append(self.fetch_threaded(session=session, path=word))
            await asyncio.gather(*tasks)


def stop_loop():
    """
    Cancels pending tasks and stops event loop.
    """
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    for task in asyncio.Task.all_tasks():
        task.cancel()
    loop.stop()


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
    argparser.add_argument('-fi', '--filter_include', type=str, default="",
                           help='Include only status codes; comma-separated',)
    argparser.add_argument('-fe', '--filter_exclude', type=str, default="404",
                           help='Exclude status codes; comma-separated')
    args = argparser.parse_args()

    config = args.url, args.wordlist, args.threads, args.max_errors, args.filter_include, args.filter_exclude
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(Websearch(*config).run())
    except ErrorsLimitExceededException:
        stop_loop()
        sys.stderr.write('Errors limit exceeded')
        sys.exit(1)
    except KeyboardInterrupt:
        stop_loop()
        sys.exit(1)
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
