#!/usr/bin/env python2
# gts. le binaire derriere gpsp

import struct
import pk4

OPS = {1: 'search', 2: 'trade', 4: 'deposit'}
HDR = 16


def hdr(d):
    # 4 champs u32 ? le 3e ressemble a un opcode en u16
    return struct.unpack_from('<IIII', d, 0)


def opcode(d):
    return struct.unpack_from('<H', d, 8)[0]


def decode_search(d):
    # 0x0001
    sp = struct.unpack_from('<H', d, HDR + 4)[0]
    pid = struct.unpack_from('<I', d, HDR)[0]
    return {'species': sp, 'pid': '0x%08X' % pid}


def decode_deposit(d):
    # 0x0004. pk4 complet apres le header
    body = d[HDR:]
    if len(body) < 136:
        return {'op': 4, 'len': len(body)}
    return pk4.report(body, 1)


def dispatch(d):
    o = opcode(d)
    if o == 1:
        return decode_search(d)
    if o == 4:
        return decode_deposit(d)
    # 0x0002 j'y arrive pas
    return {'op': o, 'raw': d[:32].encode('hex')}
