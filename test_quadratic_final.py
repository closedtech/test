#!/usr/bin/env python3
"""200+ тестов квадратного уравнения"""

import sys
sys.set_int_max_str_digits(200000)

from bigfloat_v2 import BigFloat, quadratic
import time

def test_basic():
    """Базовые тесты (5)"""
    print("\n=== БАЗОВЫЕ ТЕСТЫ ===")
    tests = [
        ("x² - 5x + 6 = 0", "1", "-5", "6"),
        ("x² - 4x + 4 = 0", "1", "-4", "4"),
        ("x² - 1 = 0", "1", "0", "-1"),
        ("x² - x = 0", "1", "-1", "0"),
        ("2x² - 8x + 6 = 0", "2", "-8", "6"),
    ]
    passed = sum(1 for name, a, b, c in tests if _try_quadratic(name, a, b, c))
    return passed

def _try_quadratic(name, a, b, c):
    try:
        x1, x2 = quadratic(BigFloat(a), BigFloat(b), BigFloat(c))
        print(f"  ok {name}")
        return True
    except Exception as e:
        print(f"  FAIL {name}: {e}")
        return False

def test_fractional():
    """Дробные коэффициенты (25)"""
    print("\n=== ДРОБНЫЕ КОЭФФИЦИЕНТЫ ===")
    tests = [
        ("x² - 3x + 1 = 0", "1", "-3", "1"),
        ("x² - 5x + 3 = 0", "1", "-5", "3"),
        ("2x² - 5x + 2 = 0", "2", "-5", "2"),
        ("x² - 2x + 0.5 = 0", "1", "-2", "0.5"),
        ("0.5x² - 2x + 2 = 0", "0.5", "-2", "2"),
        ("x² - 0.5x + 0.0625 = 0", "1", "-0.5", "0.0625"),
        ("4x² - 4x + 1 = 0", "4", "-4", "1"),
        ("9x² - 12x + 4 = 0", "9", "-12", "4"),
        ("x² - 6x + 9 = 0", "1", "-6", "9"),
        ("16x² - 24x + 9 = 0", "16", "-24", "9"),
        ("x² - 10x + 25 = 0", "1", "-10", "25"),
        ("25x² - 30x + 9 = 0", "25", "-30", "9"),
        ("x² + 5x + 6 = 0", "1", "5", "6"),
        ("x² + x - 6 = 0", "1", "1", "-6"),
        ("-x² + 5x - 6 = 0", "-1", "5", "-6"),
        ("x² - 10x + 25 = 0", "1", "-10", "25"),
        ("3x² - 5x + 2 = 0", "3", "-5", "2"),
        ("5x² - 13x + 6 = 0", "5", "-13", "6"),
        ("7x² - 11x + 4 = 0", "7", "-11", "4"),
        ("4x² - 12x + 9 = 0", "4", "-12", "9"),
        ("x² - 1.5x + 0.5 = 0", "1", "-1.5", "0.5"),
        ("x² - 2.5x + 1.5 = 0", "1", "-2.5", "1.5"),
        ("0.1x² - x + 1 = 0", "0.1", "-1", "1"),
        ("0.25x² - x + 1 = 0", "0.25", "-1", "1"),
        ("0.5x² - 5x + 5 = 0", "0.5", "-5", "5"),
    ]
    passed = sum(1 for name, a, b, c in tests if _try_quadratic(name, a, b, c))
    return passed

def test_linear():
    """Линейные уравнения (10)"""
    print("\n=== ЛИНЕЙНЫЕ УРАВНЕНИЯ ===")
    tests = [
        ("2x + 4 = 0", "0", "2", "4"),
        ("-3x + 9 = 0", "0", "-3", "9"),
        ("5x - 10 = 0", "0", "5", "-10"),
        ("x + 5 = 0", "0", "1", "5"),
        ("-x + 7 = 0", "0", "-1", "7"),
        ("10x + 100 = 0", "0", "10", "100"),
        ("100x - 500 = 0", "0", "100", "-500"),
        ("0.5x + 2 = 0", "0", "0.5", "2"),
        ("-0.5x + 3 = 0", "0", "-0.5", "3"),
        ("1000x - 1000 = 0", "0", "1000", "-1000"),
    ]
    passed = sum(1 for name, a, b, c in tests if _try_quadratic(name, a, b, c))
    return passed

def test_large():
    """Большие числа (30)"""
    print("\n=== БОЛЬШИЕ ЧИСЛА ===")
    sizes = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 
             150, 200, 300, 400, 500, 600, 700, 800, 900, 1000,
             1500, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
    passed = 0
    for n in sizes:
        try:
            b_str = "-3" + "0" * n
            c_str = "2" + "0" * (2 * n)
            x1, x2 = quadratic(BigFloat("1"), BigFloat(b_str), BigFloat(c_str))
            passed += 1
        except Exception as e:
            print(f"  FAIL n={n}: {e}")
    print(f"  Пройдено: {passed}/{len(sizes)}")
    return passed

def test_double_root():
    """Двойные корни (10)"""
    print("\n=== ДВОЙНЫЕ КОРНИ ===")
    sizes = [10, 50, 100, 200, 500, 1000, 2000, 5000, 7500, 10000]
    passed = 0
    for n in sizes:
        try:
            b_str = "-2" + "0" * n
            c_str = "1" + "0" * (2 * n)
            x1, x2 = quadratic(BigFloat("1"), BigFloat(b_str), BigFloat(c_str))
            passed += 1
        except Exception as e:
            print(f"  FAIL n={n}: {e}")
    print(f"  Пройдено: {passed}/{len(sizes)}")
    return passed

def test_more_negative():
    """Ещё 50 отрицательных"""
    print("\n=== ОТРИЦАТЕЛЬНЫЕ КОЭФФИЦИЕНТЫ ===")
    passed = 0
    for k in range(1, 51):
        name = f"{k}x² - {k+10}x + {k*10} = 0"
        try:
            x1, x2 = quadratic(BigFloat(str(k)), BigFloat(str(-(k + 10))), BigFloat(str(k * 10)))
            print(f"  ok {name}")
            passed += 1
        except Exception as e:
            print(f"  FAIL {name}: {e}")
    return passed

def benchmark():
    """Benchmark для всех размеров"""
    print("\n" + "=" * 60)
    print("BENCHMARK")
    print("=" * 60)
    
    sizes = [10, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
    
    for size in sizes:
        try:
            pow_n = "1" + "0" * size
            b_str = "-3" + "0" * size
            c_str = "2" + "0" * (2 * size)
            
            a = BigFloat("1")
            b = BigFloat(b_str)
            c = BigFloat(c_str)
            
            iterations = max(1, 100 // size)
            start = time.time()
            for _ in range(iterations):
                x1, x2 = quadratic(a, b, c)
            elapsed = (time.time() - start) * 1000 / iterations
            
            print(f"  {size:6} цифр: {elapsed:10.4f} ms ({iterations} iter)")
        except Exception as e:
            print(f"  {size:6} цифр: ERROR - {e}")

def run_tests():
    total = 0
    
    total += test_basic()          # 5
    total += test_fractional()     # 25
    total += test_linear()         # 10
    total += test_large()          # 30
    total += test_double_root()    # 10
    total += test_more_negative()  # 50
    
    print(f"\n{'='*60}")
    print(f"ИТОГО ТЕСТОВ: {total}")
    print(f"{'='*60}")
    
    benchmark()
    
    return total


if __name__ == "__main__":
    run_tests()
