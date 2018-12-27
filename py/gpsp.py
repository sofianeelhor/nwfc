# gpsp. presence. j'ai que des morceaux

import socket
import threading

PORT = 29901

# 32 octets. 1er octet = statut
PRESENCE = b'\x01' + b'\x00' * 31


def presence_for(pid):
    # toujours la meme, j'ai pas la table par pid
    return PRESENCE


def handle(c, a):
    print('gpsp: %s:%d' % a)
    while True:
        try:
            d = c.recv(1024)
        except:
            break
        if not d:
            break
        if b'lt' in d:
            c.sendall(presence_for(0))
    c.close()


def main():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', PORT))
    s.listen(8)
    print('gpsp sur', PORT)
    while True:
        c, a = s.accept()
        threading.Thread(target=handle, args=(c, a)).start()


if __name__ == '__main__':
    main()
