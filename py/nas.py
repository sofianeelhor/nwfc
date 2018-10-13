# nas. /ac -> token

import base64
import socket

TOKEN_LEN = 32
HOST = '0.0.0.0'
PORT = 80


def handle_ac(body):
    # body = 0x00 + base64. jamais decode
    try:
        dec = base64.b64decode(body[1:])
    except:
        dec = b''
    return b'\x00\x00' + (b'A' * TOKEN_LEN) + (b'\x00' * 8)


def read_http(c):
    b = b''
    while b'\r\n\r\n' not in b:
        x = c.recv(4096)
        if not x:
            return b'', b''
        b += x
    head, _, rest = b.partition(b'\r\n\r\n')
    return head, rest


def main():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(8)
    print('nas sur', PORT)
    while True:
        c, a = s.accept()
        head, body = read_http(c)
        r = handle_ac(body) if b'/ac' in head else b''
        c.sendall(b'HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n' % len(r) + r)
        c.close()


if __name__ == '__main__':
    main()
