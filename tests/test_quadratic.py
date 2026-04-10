import pytest
from quadratic import solve_quadratic
from bigint import BigInt
import re


def bi(s):
    return BigInt(s)


def parse_x(result):
    nums = re.findall(r'[-+]?\d+', result)
    return [BigInt(n) for n in nums]


class TestQuadraticBasic:
    def test_x2_1(self):
        r = solve_quadratic("1", "0", "-1")
        assert "Два решения" in r
    def test_x2_4(self):
        r = solve_quadratic("1", "0", "-4")
        assert "Два решения" in r
    def test_x2_9(self):
        r = solve_quadratic("1", "0", "-9")
        assert "Два решения" in r
    def test_x2_16(self):
        r = solve_quadratic("1", "0", "-16")
        assert "Два решения" in r
    def test_x2_25(self):
        r = solve_quadratic("1", "0", "-25")
        assert "Два решения" in r


class TestQuadraticOneRoot:
    def test_one_root_1(self):
        r = solve_quadratic("1", "-2", "1")
        assert "Одно решение" in r
    def test_one_root_2(self):
        r = solve_quadratic("1", "-4", "4")
        assert "Одно решение" in r
    def test_one_root_3(self):
        r = solve_quadratic("1", "-6", "9")
        assert "Одно решение" in r
    def test_one_root_4(self):
        r = solve_quadratic("1", "-8", "16")
        assert "Одно решение" in r
    def test_one_root_5(self):
        r = solve_quadratic("1", "-10", "25")
        assert "Одно решение" in r


class TestQuadraticComplex:
    def test_complex_1(self):
        r = solve_quadratic("1", "1", "1")
        assert "Комплексные" in r
    def test_complex_2(self):
        r = solve_quadratic("1", "2", "2")
        assert "Комплексные" in r
    def test_complex_3(self):
        r = solve_quadratic("1", "3", "3")
        assert "Комплексные" in r
    def test_complex_4(self):
        r = solve_quadratic("1", "4", "5")
        assert "Комплексные" in r
    def test_complex_5(self):
        r = solve_quadratic("1", "5", "10")
        assert "Комплексные" in r


class TestQuadraticLinear:
    def test_linear_1(self):
        r = solve_quadratic("0", "2", "-4")
        assert "x = 2" in r
    def test_linear_2(self):
        r = solve_quadratic("0", "3", "-9")
        assert "x = 3" in r
    def test_linear_3(self):
        r = solve_quadratic("0", "5", "-15")
        assert "x = 3" in r
    def test_linear_4(self):
        r = solve_quadratic("0", "-2", "10")
        assert "x = 5" in r
    def test_linear_5(self):
        r = solve_quadratic("0", "-4", "12")
        assert "x = 3" in r


class TestQuadraticNoSolution:
    def test_no_sol_1(self):
        r = solve_quadratic("0", "0", "5")
        assert "Нет решений" in r
    def test_no_sol_2(self):
        r = solve_quadratic("0", "0", "100")
        assert "Нет решений" in r


class TestQuadraticInfinite:
    def test_infinite(self):
        r = solve_quadratic("0", "0", "0")
        assert "Бесконечно" in r


class TestQuadraticMixed:
    def test_mixed_1(self):
        r = solve_quadratic("1", "-3", "2")
        assert "Два решения" in r
    def test_mixed_2(self):
        r = solve_quadratic("1", "-5", "6")
        assert "Два решения" in r
    def test_mixed_3(self):
        r = solve_quadratic("2", "5", "3")
        assert "Два решения" in r
    def test_mixed_4(self):
        r = solve_quadratic("3", "4", "1")
        assert "Два решения" in r
    def test_mixed_5(self):
        r = solve_quadratic("5", "8", "3")
        assert "Два решения" in r
