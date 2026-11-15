import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / 'results'


def load_json(name):
    with (RESULTS / name).open(encoding='utf-8') as file:
        return json.load(file)


def load_csv(name):
    with (RESULTS / name).open(encoding='utf-8') as file:
        return list(csv.DictReader(file))


def slope(rows, key):
    x = [math.log(row['b']) for row in rows]
    y = [math.log(row[key]) for row in rows]
    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)
    return sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y)) / sum(
        (xi - x_mean) ** 2 for xi in x
    )


def make_full_plot(rows):
    fig, ax = plt.subplots(figsize=(8, 5))
    b = [row['b'] for row in rows]

    for key, label, marker in (
        ('naive', 'count_naive', 'o'),
        ('fastpow', 'count_fastpow', 's'),
        ('iter', 'count_iter', '^'),
    ):
        ax.loglog(b, [row[key] for row in rows], marker=marker, linewidth=2, label=label)

    ax.set_xlabel('b')
    ax.set_ylabel('Время, с')
    ax.set_title('Полная модель: время вычисления')
    ax.grid(True, which='both', alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / 'full_time.png', dpi=180)
    plt.close(fig)


def make_histogram(rows):
    values = [int(row['N']) for row in rows]
    counts = [int(row['count']) for row in rows]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(values, counts, width=0.85, color='#3478bf')
    ax.set_xlabel('N')
    ax.set_ylabel('Количество точек')
    ax.set_title('Распределение N при b ≤ 50')
    ax.set_xticks(range(0, 51, 5))
    ax.grid(axis='y', alpha=0.25)
    fig.tight_layout()
    fig.savefig(RESULTS / 'n_histogram.png', dpi=180)
    plt.close(fig)


def make_fraction_plot(rows):
    b = [int(row['b']) for row in rows]
    fractions = [float(row['fraction']) for row in rows]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(b, fractions, color='#c44e52', linewidth=2)
    ax.scatter(b, fractions, s=14, color='#c44e52')
    ax.set_xlabel('b')
    ax.set_ylabel('Доля точек с ΔN ≠ 0')
    ax.set_title('Чувствительность к возмущениям при b ≤ 50')
    ax.set_ylim(0, 1.02)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(RESULTS / 'change_fraction.png', dpi=180)
    plt.close(fig)


def make_sparse_plot(data):
    measured = data['measured']
    fig, ax = plt.subplots(figsize=(8, 5))

    for key, label, marker in (
        ('naive', 'count_sp_naive', 'o'),
        ('fastpow', 'count_sp_fastpow', 's'),
        ('iter', 'count_sp_iter', '^'),
    ):
        points = sorted((int(b), value) for b, value in measured[key].items())
        ax.loglog(
            [point[0] for point in points],
            [point[1] for point in points],
            marker=marker,
            linewidth=2,
            label=label,
        )

    ax.set_xlabel('b')
    ax.set_ylabel('Время, с')
    ax.set_title('Разреженная модель: измеренное время')
    ax.grid(True, which='both', alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / 'sparse_time.png', dpi=180)
    plt.close(fig)


if __name__ == '__main__':
    full = load_json('full_timings.json')
    make_full_plot(full)
    make_histogram(load_csv('n_histogram.csv'))
    make_fraction_plot(load_csv('change_fraction.csv'))
    make_sparse_plot(load_json('sparse_timings.json'))

    slopes = {key: slope(full, key) for key in ('naive', 'fastpow', 'iter')}
    ratio = full[-1]['naive'] / full[-1]['iter']
    estimate = load_json('full_naive_estimate.json')
    save_data = {
        'slopes': slopes,
        'naive_iter_ratio_b_10000': ratio,
        'naive_estimate_b_100000_seconds': estimate['seconds'],
    }

    with (RESULTS / 'derived_metrics.json').open('w', encoding='utf-8') as file:
        json.dump(save_data, file, ensure_ascii=False, indent=2)

    print(json.dumps(save_data, ensure_ascii=False, indent=2))
