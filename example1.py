import asyncio

from subprocess import Popen, PIPE


async def connect_write_pipe(file):
    """Return a write-only transport wrapping a writable pipe"""
    loop = asyncio.get_event_loop()
    transport, _ = await loop.connect_write_pipe(asyncio.Protocol, file)
    return transport


async def connect_read_pipe(file):
    """Wrap a readable pipe in a stream"""
    loop = asyncio.get_event_loop()
    stream_reader = asyncio.StreamReader(loop=loop)

    def factory():
        return asyncio.StreamReaderProtocol(stream_reader)

    transport, _ = await loop.connect_read_pipe(factory, file)
    return stream_reader, transport


async def main(loop):
    # start subprocess and wrap stdin, stdout, stderr
    p = Popen(['/usr/bin/sort'], stdin=PIPE, stdout=PIPE, stderr=PIPE)

    stdin = await connect_write_pipe(p.stdin)
    stdout, stdout_transport = await connect_read_pipe(p.stdout)
    stderr, stderr_transport = await connect_read_pipe(p.stderr)

    # interact with subprocess
    name = {stdout: 'OUT', stderr: 'ERR'}
    registered = {
        asyncio.Task(stderr.read()): stderr,
        asyncio.Task(stdout.read()): stdout
    }

    to_sort = b"one\ntwo\nthree\n"
    stdin.write(to_sort)
    stdin.close()  # this way we tell we do not have anything else

    # get and print lines from stdout, stderr
    timeout = None
    while registered:
        done, pending = await asyncio.wait(
            registered, timeout=timeout,
            return_when=asyncio.FIRST_COMPLETED)
        if not done:
            break
        for f in done:
            stream = registered.pop(f)
            res = f.result()
            if res != b'':
                print(name[stream], res.decode('ascii').rstrip())
                registered[asyncio.Task(stream.read())] = stream
        timeout = 0.0

    stdout_transport.close()
    stderr_transport.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main(loop))
    finally:
        loop.close()
