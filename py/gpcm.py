# gpcm + gpsp. framing = \key\value\key\value\

import socket
import threading
import hashlib
import sys
import time

CHALLENGE_LEN = 10
PASSWORD = b'pokemondpds'

conns = {}
lock = threading.Lock()


def parse(blob):
    p = blob.split(b'\\')
    return dict(zip(p[1::2], p[2::2]))


def build(d):
    o = b''
    for k in d:
        v = d[k]
        if not isinstance(v, bytes):
            v = v.encode()
        o += b'\\' + k.encode() + b'\\' + v
    return o + b'\\'


def read_frame(c):
    # on accumule jusqu'a un frame complet
    b = b''
    while True:
        try:
            x = c.recv(1024)
        except:
            return b
        if not x:
            return b
        b += x
        if len(b) > 4 and b[:1] == b'\\' and b[-1:] == b'\\':
            return b


def response(challenge, pw):
    return hashlib.md5(challenge + pw).hexdigest().encode()


def ping(c):
    while True:
        time.sleep(45)
        try:
            c.sendall(build({b'ka': b''}))
        except:
            return


def handle(c, a):
    print('gpcm: %s:%d' % a)
    threading.Thread(target=ping, args=(c,)).start()
    while True:
        f = read_frame(c)
        if not f:
            break
        d = parse(f)
        if b'login' in d:
            got = response(d.get(b'challenge', b''), PASSWORD)
            if got == d.get(b'response'):
                c.sendall(build({b'lc': b'2', b'id': b'1', b'final': b''}))
            else:
                c.sendall(build({b'lc': b'0', b'msg': b'bad pass'}))
        elif b'lt' in d:
            pass
        else:
            print('gpcm: connais pas', d)
    c.close()


def main():
    port = 29900
    if len(sys.argv) > 2 and sys.argv[1] == '--port':
        port = int(sys.argv[2])
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', port))
    s.listen(8)
    print('gpcm sur', port)
    while True:
        c, a = s.accept()
        threading.Thread(target=handle, args=(c, a)).start()


if __name__ == '__main__':
    main()
