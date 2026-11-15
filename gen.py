from main import count_iter


def get_perturbed_points(a, b, c):
    points = [
        ((a - 1) % b, b, c),
        ((a + 1) % b, b, c),
        (a, b, (c - 1) % b),
        (a, b, (c + 1) % b),
    ]

    for new_b in (b - 1, b + 1):
        if new_b >= 2:
            points.append((a % new_b, new_b, c % new_b))

    return points


def sensitivity(p, p_perturbed):
    n_p = count_iter(*p)
    n_p_perturbed = count_iter(*p_perturbed)

    numerator = abs(n_p_perturbed - n_p) / max(n_p, 1)

    denominator = max(
        abs(new - old) / max(abs(old), 1)
        for old, new in zip(p, p_perturbed)
    )

    return numerator / denominator


def condition_number(a, b, c):
    point = (a, b, c)
    points = get_perturbed_points(a, b, c)

    sensitivitys = [
        sensitivity(point, point_perturbed)
        for point_perturbed in points
    ]

    return max(sensitivitys, default=0)


def make_c_table():
    rows = []

    for b in (7, 11, 13, 17):
        for a in (2, 3, 5):
            for c in range(b):
                n_before = count_iter(a, b, c)
                n_after = count_iter(a, b, (c + 1) % b)
                rows.append((a, b, c, n_before, n_after))

    return rows


def make_a_table():
    rows = []

    for b in (7, 11, 13, 17):
        for a in (2, 3, 5):
            for c in range(b):
                n_before = count_iter(a, b, c)
                n_after_plus = count_iter((a + 1) % b, b, c)
                n_after_minus = count_iter((a - 1) % b, b, c)
                rows.append((a, b, c, n_before, n_after_plus, n_after_minus))

    return rows



def make_b_table():
    rows = []

    for b in (7, 11, 13, 17):
        for a in (2, 3, 5):
            for c in range(b):
                n_before = count_iter(a, b, c)
                b1 = b + 1
                b2 = b - 1
                n_after_plus = count_iter(a % b1, b1, c % b1)
                n_after_minus = count_iter(a % b2, b2, c % b2)
                rows.append((a, b, c, n_before, n_after_plus, n_after_minus))

    return rows


def make_condition_table(points):
    rows = []

    for a, b, c in points:
        n = count_iter(a, b, c)
        kappa = condition_number(a, b, c)
        rows.append((a, b, c, n, kappa))

    return rows


def find_zero_to_positive():
    rows = []

    for b in range(2, 51):
        for a in range(b):
            for c in range(b):
                p = (a, b, c)
                n_before = count_iter(a, b, c)

                if n_before != 0:
                    continue

                for p_perturbed in dict.fromkeys(get_perturbed_points(a, b, c)):
                    n_after = count_iter(*p_perturbed)

                    if n_after > 0:
                        s = sensitivity(p, p_perturbed)
                        rows.append((p, p_perturbed, n_before, n_after, s))
                        break

                if len(rows) == 3:
                    return rows

    return rows


def mini_research():
    zero_count = 0
    multi_count = 0
    total_count = 0
    max_kappa = -1
    max_point = None
    stable_point = None
    histogram = {}
    change_fraction = []

    for b in range(2, 51):
        changed_at_b = 0
        points_at_b = 0

        for a in range(b):
            for c in range(b):
                p = (a, b, c)
                n = count_iter(a, b, c)
                points = get_perturbed_points(a, b, c)
                changed = False

                total_count += 1
                zero_count += n == 0
                multi_count += n >= 2
                histogram[n] = histogram.get(n, 0) + 1

                for p_perturbed in points:
                    if count_iter(*p_perturbed) != n:
                        changed = True
                        break

                changed_at_b += changed
                points_at_b += 1

                kappa = condition_number(a, b, c)
                if kappa > max_kappa:
                    max_kappa = kappa
                    max_point = p

                if stable_point is None and not changed and len(points) == 6:
                    stable_point = p

        change_fraction.append((b, changed_at_b / points_at_b))

    return {
        'zero_count': zero_count,
        'multi_count': multi_count,
        'total_count': total_count,
        'max_kappa': max_kappa,
        'max_point': max_point,
        'stable_point': stable_point,
        'histogram': histogram,
        'change_fraction': change_fraction,
    }