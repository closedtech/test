import pytest
from quadratic import solve_quadratic

def test_two_solutions():
    assert "x1" in solve_quadratic(1, -3, 2)

def test_one_solution():
    result = solve_quadratic(1, -2, 1)
    assert "x = 1.0000" in result

def test_no_solutions():
    assert "Нет действительных решений" in solve_quadratic(1, 0, 1)

def test_linear():
    assert "Линейное уравнение" in solve_quadratic(0, 2, -4)

def test_zero_abc():
    assert "Нет решений" in solve_quadratic(0, 0, 1)
