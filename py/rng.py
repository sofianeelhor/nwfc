#!/usr/bin/env python2

MUL = 0x41C64E6D
ADD = 0x6073

def step(seed):
    return (MUL * seed + ADD) & 0xffffffff

def unxor(seed, n):
    s = seed
    out = []
    for i in range(n):
        s = step(s)
        out.append((s >> 16) & 0xffff)
    return out

def md5_challenge(challenge, pw):
    import hashlib
    return hashlib.md5(challenge + pw).hexdigest()

# marche pas avec les str unicode
#def md5_challenge(c, p):
#    return md5.new(c + p).hexdigest()
