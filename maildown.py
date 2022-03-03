#!/usr/bin/env python
import asyncio, aiodns
import logging
import multiprocessing
from itertools import cycle

import anyio
import uvloop
import click
from python_socks.async_.anyio import Proxy
from commons import Proxy as ProxyDataClass, config_logger, load_proxies
from typing import Iterable


def get_proxy(proxy_iterator: Iterable[Proxy]) -> ProxyDataClass:
    try:
        return next(proxy_iterator)
    except StopIteration:
        return None


async def dns_query(name: str, query_type: str):
    loop = asyncio.get_event_loop()
    resolver = aiodns.DNSResolver(loop=loop)
    return await resolver.query(name, query_type)


async def check_mx(host: str, mail_host: str, proxy_iterator: Iterable[ProxyDataClass], sleep_delay: int = 1000):
    while True:
        try:
            proxy_url = get_proxy(proxy_iterator).get_formatted()
            proxy = Proxy.from_url(proxy_url)
            logging.info('[%s - %s] with proxy %s', mail_host, host, proxy_url)
            stream = await proxy.connect(dest_host=host, dest_port=25)
            response = await stream.anyio_stream.receive()
            logging.debug("[%s - %s] Welcome response: %s", mail_host, host, response)
            await stream.anyio_stream.send(bytes(f'EHLO {mail_host}\r\n', encoding="utf8"))

            response = await stream.anyio_stream.receive()
            #logging.debug("[%s - %s] EHLO response: %s", mail_host, host, response)
            #await stream.anyio_stream.send(b'MAIL FROM:<johndoe@nowhere.com>\r\n')
            #response = await stream.anyio_stream.receive()
            logging.debug('[%s - %s] MAIL FROM response: %s', mail_host, host, response)
            logging.debug('[%s - %s] Sleeping for %s seconds', mail_host, host, sleep_delay)
            await anyio.sleep(sleep_delay)
            logging.debug('[%s - %s] done', mail_host, host)
        except Exception as error:
            logging.error('[%s - %s] Got an error %s: %s', mail_host, host, type(error), error)
            await anyio.sleep(1)


async def list_mx(mail_host, proxy_iterator, sleep_delay, concurrency):
    data = await dns_query(mail_host, 'MX')
    logging.info('dns resolved started')
    my_arr = []
    for k in range(0, concurrency):
        for i in data:
            my_arr.append(check_mx(i.host, mail_host, proxy_iterator, sleep_delay=sleep_delay))
    await asyncio.gather(*my_arr)


def process(concurrency, host, log_to_stdout, proxy_file, proxy_url, shuffle_proxy, sleep_delay, verbose):
    config_logger(verbose, log_to_stdout)
    uvloop.install()
    proxy_iterator = cycle(load_proxies(proxy_file, proxy_url, shuffle=shuffle_proxy))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(list_mx(host, proxy_iterator, sleep_delay, concurrency))


@click.command(help="Run MX checker")
@click.option('--host', help='target host')
@click.option('--sleep-delay', help='sleep time', type=int, default=100)
@click.option('-v', '--verbose', help='Show verbose log', count=True)
@click.option('--log-to-stdout', help='log to console', is_flag=True)
@click.option('--proxy-url', help='url to proxy resourse')
@click.option('--proxy-file', help='path to file with proxy list')
@click.option('--shuffle-proxy', help='Shuffle proxy list on application start', is_flag=True, default=False)
@click.option('--concurrency', help='concurrency level', type=int, default=1)
@click.option('--restart-period', help='period in seconds to restart application (reload proxies ans targets)', type=int)
def main(
        host: str, sleep_delay: int, verbose: int, log_to_stdout: bool,
        proxy_url: str, proxy_file: str, shuffle_proxy: bool,
        concurrency: int, restart_period: int,
):
    if not proxy_url and not proxy_file:
        raise SystemExit('--proxy-url or --proxy-file is required')
    config_logger(verbose, log_to_stdout)

    while True:
        proc = multiprocessing.Process(
            target=process,
            args=(concurrency, host, log_to_stdout, proxy_file, proxy_url, shuffle_proxy, sleep_delay, verbose)
        )
        proc.start()
        proc.join(restart_period)
        if proc.exitcode is None:
            logging.info('Killing the process by restart period')
            proc.kill()
            proc.join()
        if restart_period is None:
            break


if __name__ == '__main__':
    main()
