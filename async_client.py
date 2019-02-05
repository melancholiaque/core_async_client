import asyncio
import curses

import aioconsole


class Client:

    RETURN = 13

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.screen = curses.initscr()
        self.screen.refresh()
        self.stream, _ = self.loop.run_until_complete(
            aioconsole.get_standard_streams()
        )

    async def readchar(self):
        return (await self.stream.read(1)).decode()

    async def readline(self):
        string = ''
        inp = await self.readchar()

        while ord(inp) != self.RETURN:
            string += inp
            inp = (await self.stream.read(1)).decode()

        return string

    async def handle_key(self):
        while True:
            data = await self.readline()
            self.screen.addstr(1, 0, data)
            self.screen.refresh()

    async def handle_conn(self, reader, writer):
        while True:
            data = await reader.readuntil()
            self.screen.addstr(0, 1, data.decode())
            self.screen.refresh()

    def start_server(self):
        coro = asyncio.start_server(self.handle_conn,
                                    '127.0.0.1',
                                    8000,
                                    loop=self.loop)
        return self.loop.run_until_complete(coro)

    def start_kb_listener(self):
        coro = self.handle_key()
        return self.loop.run_until_complete(coro)

    def start(self):
        server = self.start_server()
        kb_listener = self.start_kb_listener()
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.close()
            self.loop.run_until_complete(server.wait_closed())
            self.loop.close()

Client().start()
