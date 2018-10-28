#!/usr/bin/env python2
import struct

# TODO verifier les 24 permutations, trouvees a droite a gauche
BLOCK_ORDER = [
    (0,1,2,3),(0,1,3,2),(0,2,1,3),(0,3,1,2),(0,2,3,1),(0,3,2,1),
    (1,0,2,3),(1,0,3,2),(2,0,1,3),(3,0,1,2),(2,0,3,1),(3,0,2,1),
    (1,2,0,3),(1,3,0,2),(2,1,0,3),(3,1,0,2),(2,3,0,1),(3,2,0,1),
    (1,2,3,0),(1,3,2,0),(2,1,3,0),(3,1,2,0),(2,3,1,0),(3,2,1,0),
]

CRC_POLY = 0x1021

def sv(pid):
    return ((pid >> 13) & 31) % 24

def checksum(buf):
    crc = 0
    for b in buf[8:0x88]:
        crc ^= b << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ CRC_POLY
            else:
                crc = crc << 1
            crc &= 0xffff
    return crc

def shuffle(buf, pid):
    o = BLOCK_ORDER[sv(pid)]
    t = bytearray(128)
    for i in range(4):
        t[o[i]*32:o[i]*32+32] = buf[8+i*32:8+i*32+32]
    buf[8:0x88] = t

def report(raw):
    buf = bytearray(raw)
    pid = struct.unpack_from('<I', buf, 0)[0]
    shuffle(buf, pid)
    d = {}
    d['pid'] = '0x%08X' % pid
    d['sv'] = sv(pid)
    d['ok'] = (struct.unpack_from('<H', raw, 6)[0] == checksum(buf))
    d['species'] = struct.unpack_from('<H', buf, 0x08)[0]
    return d

if __name__ == '__main__':
    import sys
    print report(open(sys.argv[1], 'rb').read())
