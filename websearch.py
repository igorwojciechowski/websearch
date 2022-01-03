#!/usr/bin/env python3
import asyncio
import json
from aiohttp import ClientSession, ClientConnectorError
import argparse


def read_wordlist(wordlist: str) -> list:
    with open(wordlist, 'r') as f:
        return [_.replace('\n', '') for _ in f.readlines()]


def output_json(path: str, data: dict):
    with open(path, 'w') as output:
        json.dump(data, output)


async def fetch(session: ClientSession, url: str, path: str):
    cli_output = "{url}/{path:15}\t\t{status}\t\t{content}"
    try:
        response = await session.request(method='GET', url=f"{url}/{path}", allow_redirects=False)
        print(cli_output.format(url=url, path=path, status=response.status, content=len(str(await response.content.read()))))
        return {
            'url': url,
            'path': path,
            'status': response.status,
            'content': len(str(await response.content.read()))
        }
    except ClientConnectorError:
        return


async def threaded(sem, session, url, path):
    async with sem:
        return await fetch(session=session, url=url, path=path)


async def work(sem, url: str, wordlist: list, output: str):
    async with ClientSession() as session:
        tasks = []
        for word in wordlist:
            tasks.append(threaded(sem, session=session, url=url, path=word))
        results = await asyncio.gather(*tasks)
        if output:
            output_json(output, results)


if __name__ == '__main__':
    ARGPARSER = argparse.ArgumentParser()
    ARGPARSER.add_argument('-u', '--url', type=str, help='', required=True)
    ARGPARSER.add_argument('-w', '--wordlist', type=str,
                           help='', required=True)
    ARGPARSER.add_argument('-t', '--threads', type=int, help='', default=30)
    ARGPARSER.add_argument('-o', '--output', type=str)
    ARGS = ARGPARSER.parse_args()

    URL = ARGS.url
    WORDLIST = read_wordlist(ARGS.wordlist)
    THREADS = ARGS.threads
    OUTPUT = ARGS.output
    SEMAPHORE = asyncio.Semaphore(THREADS)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(work(SEMAPHORE, URL, WORDLIST, OUTPUT))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
