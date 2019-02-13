from socket import socket
from itertools import count
from time import sleep

from core_client.models.messages import Message
from core_client.layers import socket_send_data
from core_client.modules.default_modules import (SendAsJSONModule,
                                                 Base64EncodeModule,
                                                 Base64SendModule,
                                                 AES256SendModule)
from core_client.models.base import Jsonable
from core_client.models.packets import Packet
from core_client.models.actions import NewMessageAction

modules = {
    "transformer": SendAsJSONModule(),
    "model": [Base64EncodeModule()],
    "binary": [Base64SendModule(),
               AES256SendModule("yoursecretkey123", enabled=False)]
}

for i in count():
    sock = socket()
    sock.connect(('127.0.0.1', 8000))
    for j in range(3):
        m = Message(text=f'{i}, {j}')
        a = NewMessageAction()
        p = Packet(action=a, message=m)
        socket_send_data(sock, p, modules)
        sleep(0.6)
    sleep(0.3)
