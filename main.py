def binpow(a, n, mod):
    res = 1
    a %= mod
    while n > 0:
        if n & 1:
            res = (res * a) % mod
        a = (a * a) % mod
        n >>= 1
    return res


def count_fastpow(a, b, c):
    mod = b
    res = 0
    for y in range(b):
        if binpow(a, y, mod) == c % mod:
            res += 1
    return res


def count_naive(a, b, c):
    mod = b
    res = 0
    for y in range(b):
        q = 1
        for _ in range(y):
            q = (q * a) % mod

        if q == c % mod:
            res += 1

    return res


def count_iter(a, b, c):
    mod = b
    res = 0
    q = 1
    for y in range(b):
        if q == c % mod:
            res += 1
        q = (q * a) % mod

    return res
