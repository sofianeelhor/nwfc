# repond a *.nintendowifi.net avec l'ip locale
# sudo python3 tools/dns_poison.py --ip 192.168.1.42

import socket
import struct
import sys

SUFFIX = b'nintendowifi.net'


def qname(d, off):
    parts = []
    while d[off]:
        n = d[off]
        off += 1
        parts.append(d[off:off + n])
        off += n
    return b'.'.join(parts), off + 1


def reply(d, ip):
    name, off = qname(d, 12)
    q = d[12:off] + d[off:off + 4]
    hdr = d[0:2] + b'\x81\x80' + b'\x00\x01\x00\x01' + b'\x00\x00\x00\x00'
    rr = b'\xc0\x0c' + b'\x00\x01\x00\x01' + struct.pack('>I', 60)
    rr += b'\x00\x04' + socket.inet_aton(ip)
    return hdr + q + rr


def main():
    ip = '127.0.0.1'
    if len(sys.argv) > 2 and sys.argv[1] == '--ip':
        ip = sys.argv[2]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('0.0.0.0', 53))
    print('dns sur 53 ->', ip)
    while True:
        d, a = s.recvfrom(512)
        if len(d) < 13:
            continue
        name, off = qname(d, 12)
        if name == SUFFIX or name.endswith(b'.' + SUFFIX):
            s.sendto(reply(d, ip), a)
            print('poison', name)


if __name__ == '__main__':
    main()
