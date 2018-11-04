#!/usr/bin/env python2
import struct
from binascii import hexlify

# index -> slot, les 24 permutations
BLOCK_ORDER = [
    (0,1,2,3),(0,1,3,2),(0,2,1,3),(0,3,1,2),(0,2,3,1),(0,3,2,1),
    (1,0,2,3),(1,0,3,2),(2,0,1,3),(3,0,1,2),(2,0,3,1),(3,0,2,1),
    (1,2,0,3),(1,3,0,2),(2,1,0,3),(3,1,0,2),(2,3,0,1),(3,2,0,1),
    (1,2,3,0),(1,3,2,0),(2,1,3,0),(3,1,2,0),(2,3,1,0),(3,2,1,0),
]

CRC_POLY = 0x1021
LCG_MUL  = 0x41C64E6D
LCG_ADD  = 0x6073

cache = {}

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

# ancienne, la garde au cas ou
#def checksum(buf):
#    return zlib.crc32(buf[8:0x88]) & 0xffff

def unshuffle(buf, pid):
    o = BLOCK_ORDER[sv(pid)]
    t = bytearray(128)
    for i in range(4):
        t[i*32:(i+1)*32] = buf[8+o[i]*32:8+o[i]*32+32]
    buf[8:0x88] = t

def shuffle(buf, pid):
    o = BLOCK_ORDER[sv(pid)]
    t = bytearray(128)
    for i in range(4):
        t[o[i]*32:o[i]*32+32] = buf[8+i*32:8+i*32+32]
    buf[8:0x88] = t

def crypt(buf, pid):
    # self inverse
    csum = struct.unpack_from('<H', buf, 6)[0]
    seed = (csum | (pid << 16)) & 0xffffffff
    for i in range(64):
        seed = (LCG_MUL * seed + LCG_ADD) & 0xffffffff
        off = 8 + i*2
        v = struct.unpack_from('<H', buf, off)[0] ^ ((seed >> 16) & 0xffff)
        struct.pack_into('<H', buf, off, v)

def decode(raw, enc=1):
    buf = bytearray(raw)
    pid = struct.unpack_from('<I', buf, 0)[0]
    if enc:
        crypt(buf, pid)
    unshuffle(buf, pid)
    return pid, buf

def encode(raw, pid, enc=1):
    buf = bytearray(raw)
    # crc sur le canonique, avant le shuffle
    struct.pack_into('<H', buf, 6, checksum(buf))
    shuffle(buf, pid)
    if enc:
        crypt(buf, pid)
    return bytes(buf)

def verify(raw, enc=1):
    pid, buf = decode(raw, enc)
    return struct.unpack_from('<H', raw, 6)[0] == checksum(buf)

def report(raw, enc=1):
    pid, buf = decode(raw, enc)
    d = {}
    d['pid'] = '0x%08X' % pid
    d['sv'] = sv(pid)
    d['ok'] = (struct.unpack_from('<H', raw, 6)[0] == checksum(buf))
    d['species'] = struct.unpack_from('<H', buf, 0x08)[0]
    d['tid'] = struct.unpack_from('<H', buf, 0x0C)[0]
    d['sid'] = struct.unpack_from('<H', buf, 0x0E)[0]
    d['exp'] = struct.unpack_from('<I', buf, 0x10)[0]
    return d

if __name__ == '__main__':
    import sys
    f = open(sys.argv[1], 'rb')
    d = report(f.read())
    f.close()
    for k in d:
        print k, d[k]
