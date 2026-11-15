from main import count_fastpow, count_iter, count_naive
import time


A = 2
C = 1
b_val = [100, 300, 1000, 3000, 10_000]


def time_func():
    funcs = [count_naive, count_iter, count_fastpow]

    for func in funcs:
        for b in b_val:
            start = time.perf_counter()
            result = func(A, b, C)
            elapsed = time.perf_counter() - start
            print(f'{func.__name__}: b={b}, N={result}, time={elapsed:.6f} s')


if __name__ == '__main__':
    time_func()
