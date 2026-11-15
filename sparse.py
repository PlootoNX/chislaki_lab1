from main import binpow
from gen import get_perturbed_points


K = 500


def sparse_y(b, k=K):
    return sorted({i * (b - 1) // (k - 1) for i in range(k)})


def count_sp_naive(a, b, c, k=K):
    res = 0

    for y in sparse_y(b, k):
        q = 1

        for _ in range(y):
            q = (q * a) % b

        if q == c % b:
            res += 1

    return res


def count_sp_fastpow(a, b, c, k=K):
    res = 0

    for y in sparse_y(b, k):
        if binpow(a, y, b) == c % b:
            res += 1

    return res


def count_sp_iter(a, b, c, k=K):
    res = 0
    q = 1
    y_values = set(sparse_y(b, k))

    for y in range(b):
        if y in y_values and q == c % b:
            res += 1
        q = (q * a) % b

    return res


def sparse_sensitivity(p, p_perturbed, k=K):
    n_p = count_sp_fastpow(*p, k=k)
    n_p_perturbed = count_sp_fastpow(*p_perturbed, k=k)
    numerator = abs(n_p_perturbed - n_p) / max(n_p, 1)
    denominator = max(
        abs(new - old) / max(abs(old), 1)
        for old, new in zip(p, p_perturbed)
    )

    return numerator / denominator


def sparse_condition_number(a, b, c, k=K):
    point = (a, b, c)
    values = [
        sparse_sensitivity(point, point_perturbed, k)
        for point_perturbed in get_perturbed_points(a, b, c)
    ]

    return max(values, default=0)
