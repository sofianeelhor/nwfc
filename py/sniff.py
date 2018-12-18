# lit un pcap et sort les ops gts. usage: sniff.py dump.pcap

import struct
import sys

GTS_PORT = 27900


def pkts(path):
    f = open(path, 'rb')
    h = f.read(24)
    if len(h) < 24:
        return
    big = struct.unpack_from('<I', h, 0)[0] == 0xd4c3b2a1
    while True:
        rh = f.read(16)
        if len(rh) < 16:
            break
        if big:
            ts, tu, cap, ln = struct.unpack('>IIII', rh)
        else:
            ts, tu, cap, ln = struct.unpack('<IIII', rh)
        yield ts, f.read(cap)
    f.close()


def payload(p):
    # ethernet -> ip -> tcp/udp, offsets hardcodes
    if len(p) < 54:
        return None
    if p[12:14] != b'\x08\x00':
        return None
    ip = p[14:]
    ihl = (ip[0] & 0x0f) * 4
    proto = ip[9]
    off = 14 + ihl
    if proto == 6:
        thl = (p[off + 12] >> 4) * 4
        return p[off + thl:]
    if proto == 17:
        return p[off + 8:]
    return None


if __name__ == '__main__':
    n = 0
    for ts, p in pkts(sys.argv[1]):
        d = payload(p)
        if d and len(d) > 16:
            print(ts, d[:32].hex())
            n += 1
    print('total', n, 'paquets')
