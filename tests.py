from gen import condition_number, get_perturbed_points, make_a_table, make_b_table, make_c_table, sensitivity
from main import count_iter, count_fastpow, count_naive
from sparse import count_sp_fastpow, count_sp_iter, count_sp_naive, sparse_y

SIZE = 5
a = [2, 2, 3, 0, 0]
b = [7, 7, 11, 7, 7]
c = [4, 3, 1, 0, 1]
ans = [2, 0, 3, 6, 1]


class TestFunc:
    def test_iter(self):
        for i in range(SIZE):
            assert count_iter(a[i], b[i], c[i]) == ans[i]

    def test_naive(self):
        for i in range(SIZE):
            assert count_naive(a[i], b[i], c[i]) == ans[i]

    def test_fastpow(self):
        for i in range(SIZE):
            assert count_fastpow(a[i], b[i], c[i]) == ans[i]


class TestSensitivity:
    def test_perturbed_points(self):
        assert get_perturbed_points(2, 7, 4) == [
            (1, 7, 4),
            (3, 7, 4),
            (2, 7, 3),
            (2, 7, 5),
            (2, 6, 4),
            (2, 8, 4),
        ]

    def test_sensitivity(self):
        assert sensitivity((2, 7, 4), (3, 7, 4)) == 1.0

    def test_condition_number(self):
        assert condition_number(2, 7, 4) == 4.0

    def test_perturbation_tables(self):
        assert len(make_c_table()) == 144
        assert len(make_a_table()) == 144
        assert len(make_b_table()) == 144


class TestSparse:
    def test_sparse_functions(self):
        cases = [(0, 2, 0), (1, 7, 1), (2, 7, 4), (3, 11, 1), (2, 1000, 1)]

        for a_value, b_value, c_value in cases:
            values = [
                count_sp_naive(a_value, b_value, c_value),
                count_sp_fastpow(a_value, b_value, c_value),
                count_sp_iter(a_value, b_value, c_value),
            ]
            assert values[0] == values[1] == values[2]

    def test_sparse_y_is_a_set(self):
        assert sparse_y(2) == [0, 1]

    def test_special_case(self):
        assert count_sp_fastpow(2, 10**12, 1) == 1
        assert count_sp_fastpow(1, 10**12, 1) == 500
