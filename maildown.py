import asyncio, aiodns
import anyio
import uvloop
import click
from python_socks.async_.anyio import Proxy
from typing import Iterable

def get_proxy(proxy_iterator: Iterable[str]) -> str:
    try:
        type_, ip, port = next(proxy_iterator)
        return f'{type_}://{ip}:{port}'
    except StopIteration:
        return None

async def dns_query(name, query_type):
    loop = asyncio.get_event_loop()
    resolver = aiodns.DNSResolver(loop=loop)
    return await resolver.query(name, query_type)

async def check_mx(host, mail_host, proxy_iterator, sleep_delay=1000):
    while True:
        try:
            proxy = Proxy.from_url(get_proxy(proxy_iterator))
            stream = await proxy.connect(dest_host=host, dest_port=25)

            await stream.anyio_stream.send(bytes(f'EHLO {mail_host}\r\n', encoding="utf8"))

            response = await stream.anyio_stream.receive()
            print(response)
            print("EHLO OK")
            await stream.anyio_stream.send(b'MAIL FROM:<johndoe@nowhere.com>\r\n')
            response = await stream.anyio_stream.receive()
            print(response)
            await anyio.sleep(sleep_delay)
        except:
            await anyio.sleep(1)
            pass


async def list_mx(mail_host, proxy_iterator, concurency=3):
    data = await dns_query(mail_host, 'MX')
    print('dns resolved\n')
    my_arr = []
    for k in range(0,concurency):
        for i in data:
            my_arr.append(check_mx(i.host, mail_host, proxy_iterator, sleep_delay=100))
    await asyncio.gather(*my_arr)


@click.command(help="Run MX checker")
@click.option('--host', help='target host')
@click.option('--sleep-delay', help='sleep time', type=int, default=100)
def main(host: str, sleep_delay: int):
    uvloop.install()
    proxy_iterator = [] # ?
    asyncio.run(list_mx(host, proxy_iterator, sleep_delay))


if __name__ == '__main__':
    main()
