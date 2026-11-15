import csv
import json
import statistics
import time
from pathlib import Path

from gen import (
    condition_number,
    find_zero_to_positive,
    make_a_table,
    make_b_table,
    make_c_table,
    make_condition_table,
    mini_research,
)
from main import count_fastpow, count_iter, count_naive
from sparse import (
    count_sp_fastpow,
    count_sp_iter,
    count_sp_naive,
    sparse_condition_number,
)


RESULTS = Path(__file__).resolve().parent / 'results'
RESULTS.mkdir(exist_ok=True)


def save_csv(name, header, rows):
    with (RESULTS / name).open('w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


def save_json(name, data):
    with (RESULTS / name).open('w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def measure(func, args, repeats=1):
    values = []
    result = None

    for _ in range(repeats):
        start = time.perf_counter()
        result = func(*args)
        values.append(time.perf_counter() - start)

    return result, statistics.median(values)


def run_full_model():
    correctness_points = [
        (2, 7, 4, 2),
        (2, 7, 3, 0),
        (3, 11, 1, 3),
        (0, 7, 0, 6),
        (0, 7, 1, 1),
    ]
    correctness_rows = []

    for a, b, c, expected in correctness_points:
        values = [
            count_naive(a, b, c),
            count_fastpow(a, b, c),
            count_iter(a, b, c),
        ]
        assert values == [expected, expected, expected]
        correctness_rows.append((a, b, c, expected, *values))

    save_csv(
        'correctness.csv',
        ('a', 'b', 'c', 'expected', 'naive', 'fastpow', 'iter'),
        correctness_rows,
    )

    save_csv('c_perturbations.csv', ('a', 'b', 'c', 'N', 'N_c_plus'), make_c_table())
    save_csv(
        'a_perturbations.csv',
        ('a', 'b', 'c', 'N', 'N_a_plus', 'N_a_minus'),
        make_a_table(),
    )
    save_csv(
        'b_perturbations.csv',
        ('a', 'b', 'c', 'N', 'N_b_plus', 'N_b_minus'),
        make_b_table(),
    )

    condition_points = [
        (2, 7, 4),
        (2, 7, 3),
        (3, 11, 1),
        (0, 7, 0),
        (0, 7, 1),
        (2, 11, 0),
        (3, 13, 2),
        (5, 17, 3),
        (4, 10, 0),
        (6, 15, 5),
    ]
    condition_rows = make_condition_table(condition_points)
    save_csv('condition_numbers.csv', ('a', 'b', 'c', 'N', 'kappa'), condition_rows)

    zero_rows = find_zero_to_positive()
    assert len(zero_rows) == 3
    assert len({row[0] for row in zero_rows}) == 3
    save_csv(
        'zero_to_positive.csv',
        ('a', 'b', 'c', 'a_new', 'b_new', 'c_new', 'N', 'N_new', 'S'),
        [(*row[0], *row[1], row[2], row[3], row[4]) for row in zero_rows],
    )

    research = mini_research()
    assert research['stable_point'] is not None
    assert condition_number(*research['max_point']) == research['max_kappa']
    save_json('mini_research.json', research)
    save_csv(
        'n_histogram.csv',
        ('N', 'count'),
        sorted(research['histogram'].items()),
    )
    save_csv('change_fraction.csv', ('b', 'fraction'), research['change_fraction'])

    b_values = (100, 300, 1000, 3000, 10_000)
    full_timings = []

    for b in b_values:
        row = {'b': b}
        for name, func in (
            ('naive', count_naive),
            ('fastpow', count_fastpow),
            ('iter', count_iter),
        ):
            result, elapsed = measure(func, (2, b, 1), repeats=3)
            assert result == 1
            row[name] = elapsed
        full_timings.append(row)

    save_json('full_timings.json', full_timings)
    save_csv(
        'full_timings.csv',
        ('b', 'naive', 'fastpow', 'iter'),
        [(row['b'], row['naive'], row['fastpow'], row['iter']) for row in full_timings],
    )

    naive_estimate = full_timings[-1]['naive'] * 100
    save_json('full_naive_estimate.json', {'b': 100_000, 'seconds': naive_estimate})

    return full_timings, research


def run_sparse_model():
    correctness_cases = [
        (0, 2, 0),
        (0, 2, 1),
        (1, 7, 1),
        (2, 7, 4),
        (3, 11, 1),
        (0, 50, 0),
        (5, 50, 7),
        (2, 1000, 1),
        (3, 1000, 5),
        (2, 100_000, 1),
    ]
    correctness_rows = []

    for a, b, c in correctness_cases:
        values = [
            count_sp_naive(a, b, c),
            count_sp_fastpow(a, b, c),
            count_sp_iter(a, b, c),
        ]
        assert values[0] == values[1] == values[2]
        correctness_rows.append((a, b, c, *values))

    save_csv(
        'sparse_correctness.csv',
        ('a', 'b', 'c', 'naive', 'fastpow', 'iter'),
        correctness_rows,
    )

    b_values = (1_000, 100_000, 10_000_000, 1_000_000_000, 10**12, 10**15)
    measured = {'naive': {}, 'fastpow': {}, 'iter': {}}

    for b in b_values:
        if b <= 100_000:
            _, elapsed = measure(count_sp_naive, (2, b, 1))
            measured['naive'][b] = elapsed

        _, elapsed = measure(count_sp_fastpow, (2, b, 1), repeats=3)
        measured['fastpow'][b] = elapsed

        if b <= 1_000_000_000:
            _, elapsed = measure(count_sp_iter, (2, b, 1))
            measured['iter'][b] = elapsed

    estimates = {'naive': {}, 'fastpow': {}, 'iter': {}}

    for b in b_values:
        if b not in measured['naive']:
            estimates['naive'][b] = measured['naive'][100_000] * b / 100_000
        if b not in measured['iter']:
            estimates['iter'][b] = measured['iter'][1_000_000_000] * b / 1_000_000_000

    save_json('sparse_timings.json', {'measured': measured, 'estimates': estimates})

    timing_rows = []
    for b in b_values:
        row = [b]
        for name in ('naive', 'fastpow', 'iter'):
            if b in measured[name]:
                row.append(measured[name][b])
            else:
                row.append('не выполнять')
        timing_rows.append(row)

    save_csv(
        'sparse_timings.csv',
        ('b', 'count_sp_naive', 'count_sp_fastpow', 'count_sp_iter'),
        timing_rows,
    )

    condition_rows = []
    for b in (10**6, 10**9, 10**12):
        n = count_sp_fastpow(2, b, 1)
        kappa = sparse_condition_number(2, b, 1)
        condition_rows.append((2, b, 1, n, kappa))

    save_csv(
        'sparse_condition_numbers.csv',
        ('a', 'b', 'c', 'N_sp', 'kappa'),
        condition_rows,
    )

    special_rows = []
    for a in (0, 1, 2, 3, 10**12 - 1):
        special_rows.append((a, 10**12, 1, count_sp_fastpow(a, 10**12, 1)))
    save_csv('sparse_special_case.csv', ('a', 'b', 'c', 'N_sp'), special_rows)

    return measured, estimates, condition_rows, special_rows


if __name__ == '__main__':
    full_timings, research = run_full_model()
    sparse_timings, sparse_estimates, sparse_conditions, special = run_sparse_model()

    print('Полная модель:')
    for row in full_timings:
        print(row)
    print('Мини-исследование:', {key: value for key, value in research.items() if key not in ('histogram', 'change_fraction')})
    print('Разреженная модель, замеры:', sparse_timings)
    print('Разреженная модель, оценки:', sparse_estimates)
    print('Разреженная модель, обусловленность:', sparse_conditions)
    print('Частный случай:', special)
