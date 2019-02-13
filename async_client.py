import asyncio
import curses
from collections import namedtuple
from itertools import count

import aioconsole

from core_client.config import METADATA_LEN
from core_client.modules.default_modules import (SendAsJSONModule,
                                                 Base64EncodeModule,
                                                 Base64SendModule,
                                                 AES256SendModule)
from core_client import layers


class Client:

    RETURN = 13

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.stream, _ = self.loop.run_until_complete(
            aioconsole.get_standard_streams()
        )
        self.modules = {
            "transformer": SendAsJSONModule(),
            "model": [Base64EncodeModule()],
            "binary": [Base64SendModule(),
                       AES256SendModule("yoursecretkey123", enabled=False)]
        }
        self.histories = list()
        self.screen = curses.initscr()
        self.screen.refresh()

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
        for i in count():
            data = await self.readchar()
            self.screen.addstr(2, i % 60, data)
            self.screen.refresh()

    async def handle_conn(self, reader, writer):
        sock = writer.get_extra_info('socket')
        while True:
            metadata = (await reader.read(METADATA_LEN)).decode()
            if metadata == '':
                return
            pkg_len = metadata[1:-1]
            if metadata[-1] == metadata[0] == chr(64) and pkg_len.isdigit():
                data = await reader.read(int(pkg_len))
                pkg, status_code = layers.socket_handle_received(
                    sock,
                    data,
                    self.modules
                )
                self.process_pkg(pkg)

    def process_pkg(self, pkg):
        action = pkg.action.action
        msg = pkg.message

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
        try:
            curses.curs_set(0)
            server = self.start_server()
            kb_listener = self.start_kb_listener()
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            curses.curs_set(1)
            server.close()
            self.loop.run_until_complete(server.wait_closed())
            self.loop.close()


Client().start()
