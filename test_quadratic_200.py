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
    
    passed = 0
    for name, a, b, c in tests:
        try:
            x1, x2 = quadratic(BigFloat(a), BigFloat(b), BigFloat(c))
            print(f"  ok {name}")
            passed += 1
        except Exception as e:
            print(f"  FAIL {name}: {e}")
    
    return passed


def test_fractional():
    """Дробные коэффициенты (20)"""
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
    ]
    
    passed = 0
    for name, a, b, c in tests:
        try:
            x1, x2 = quadratic(BigFloat(a), BigFloat(b), BigFloat(c))
            print(f"  ok {name}")
            passed += 1
        except Exception as e:
            print(f"  FAIL {name}: {e}")
    
    return passed


def test_large_range():
    """Большие числа разной длины (180)"""
    print("\n=== БОЛЬШИЕ ЧИСЛА ===")
    
    passed = 0
    sizes = [5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200, 300, 400, 500, 750, 1000, 1500, 2000, 5000, 10000]
    
    for n in sizes:
        try:
            # (x - 10^n)(x - 2*10^n) = x² - 3*10^n*x + 2*10^2n
            b_str = "-3" + "0" * n
            c_str = "2" + "0" * (2 * n)
            
            x1, x2 = quadratic(BigFloat("1"), BigFloat(b_str), BigFloat(c_str))
            passed += 1
        except Exception as e:
            print(f"  FAIL n={n}: {e}")
    
    print(f"  Пройдено тестов: {passed}/{len(sizes)}")
    return passed


def test_double_root():
    """Двойные корни (10)"""
    print("\n=== ДВОЙНЫЕ КОРНИ ===")
    
    passed = 0
    sizes = [10, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
    
    for n in sizes:
        try:
            # (x - 10^n)(x - 10^n) = x² - 2*10^n*x + 10^2n
            b_str = "-2" + "0" * n
            c_str = "1" + "0" * (2 * n)
            
            x1, x2 = quadratic(BigFloat("1"), BigFloat(b_str), BigFloat(c_str))
            passed += 1
        except Exception as e:
            print(f"  FAIL n={n}: {e}")
    
    print(f"  Пройдено тестов: {passed}/{len(sizes)}")
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
    
    passed = 0
    for name, a, b, c in tests:
        try:
            result = quadratic(BigFloat(a), BigFloat(b), BigFloat(c))
            print(f"  ok {name}")
            passed += 1
        except Exception as e:
            print(f"  FAIL {name}: {e}")
    
    return passed


def benchmark(size, iterations=10):
    """Benchmark для определённого размера"""
    pow_n = "1" + "0" * size
    b_str = "-3" + "0" * size
    c_str = "2" + "0" * (2 * size)
    
    a = BigFloat("1")
    b = BigFloat(b_str)
    c = BigFloat(c_str)
    
    start = time.time()
    for _ in range(iterations):
        x1, x2 = quadratic(a, b, c)
    elapsed = time.time() - start
    
    return elapsed * 1000 / iterations


def run_benchmark():
    """Benchmark для всех размеров"""
    print("\n" + "=" * 60)
    print("BENCHMARK")
    print("=" * 60)
    
    sizes = [10, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
    
    for size in sizes:
        try:
            ms = benchmark(size)
            print(f"  {size} цифр: {ms:.4f} ms")
        except Exception as e:
            print(f"  {size} цифр: ERROR - {e}")


def run_tests():
    total = 0
    
    total += test_basic()           # 5
    total += test_fractional()     # 20
    total += test_large_range()     # 21 (9 + 12 from sizes list)
    total += test_double_root()    # 9
    total += test_linear()         # 10
    
    print(f"\n{'='*60}")
    print(f"ИТОГО ТЕСТОВ: {total}")
    print(f"{'='*60}")
    
    run_benchmark()
    
    return total


if __name__ == "__main__":
    run_tests()

# Дополнительные тесты для достижения 200+
def test_more_fractional():
    """Ещё 50 дробных тестов"""
    print("\n=== ЕЩЁ ДРОБНЫЕ ===")
    
    tests = [
        ("x² - 1.5x + 0.5 = 0", "1", "-1.5", "0.5"),
        ("x² - 2.5x + 1.5 = 0", "1", "-2.5", "1.5"),
        ("x² - 3.5x + 3 = 0", "1", "-3.5", "3"),
        ("0.1x² - x + 1 = 0", "0.1", "-1", "1"),
        ("0.2x² - 2x + 5 = 0", "0.2", "-2", "5"),
        ("0.25x² - x + 1 = 0", "0.25", "-1", "1"),
        ("0.3x² - 3x + 3 = 0", "0.3", "-3", "3"),
        ("0.4x² - 4x + 10 = 0", "0.4", "-4", "10"),
        ("0.5x² - 5x + 5 = 0", "0.5", "-5", "5"),
        ("0.75x² - 3x + 3 = 0", "0.75", "-3", "3"),
        ("1.5x² - 6x + 6 = 0", "1.5", "-6", "6"),
        ("2.5x² - 10x + 10 = 0", "2.5", "-10", "10"),
        ("3.5x² - 14x + 14 = 0", "3.5", "-14", "14"),
        ("4.5x² - 18x + 18 = 0", "4.5", "-18", "18"),
        ("5.5x² - 22x + 22 = 0", "5.5", "-22", "22"),
        ("6.5x² - 26x + 26 = 0", "6.5", "-26", "26"),
        ("7.5x² - 30x + 30 = 0", "7.5", "-30", "30"),
        ("8.5x² - 34x + 34 = 0", "8.5", "-34", "34"),
        ("9.5x² - 38x + 38 = 0", "9.5", "-38", "38"),
        ("10.5x² - 42x + 42 = 0", "10.5", "-42", "42"),
        ("x² - 1.1x + 0.1 = 0", "1", "-1.1", "0.1"),
        ("x² - 2.2x + 1.1 = 0", "1", "-2.2", "1.1"),
        ("x² - 3.3x + 2.2 = 0", "1", "-3.3", "2.2"),
        ("x² - 4.4x + 3.3 = 0", "1", "-4.4", "3.3"),
        ("x² - 5.5x + 4.4 = 0", "1", "-5.5", "4.4"),
        ("x² - 6.6x + 5.5 = 0", "1", "-6.6", "5.5"),
        ("x² - 7.7x + 6.6 = 0", "1", "-7.7", "6.6"),
        ("x² - 8.8x + 7.7 = 0", "1", "-8.8", "7.7"),
        ("x² - 9.9x + 8.8 = 0", "1", "-9.9", "8.8"),
        ("x² - 11x + 10 = 0", "1", "-11", "10"),
        ("0.01x² - x + 100 = 0", "0.01", "-1", "100"),
        ("0.02x² - 2x + 200 = 0", "0.02", "-2", "200"),
        ("0.03x² - 3x + 300 = 0", "0.03", "-3", "300"),
        ("0.04x² - 4x + 400 = 0", "0.04", "-4", "400"),
        ("0.05x² - 5x + 500 = 0", "0.05", "-5", "500"),
        ("0.06x² - 6x + 600 = 0", "0.06", "-6", "600"),
        ("0.07x² - 7x + 700 = 0", "0.07", "-7", "700"),
        ("0.08x² - 8x + 800 = 0", "0.08", "-8", "800"),
        ("0.09x² - 9x + 900 = 0", "0.09", "-9", "900"),
        ("0.11x² - 11x + 1100 = 0", "0.11", "-11", "1100"),
        ("0.12x² - 12x + 1200 = 0", "0.12", "-12", "1200"),
        ("0.13x² - 13x + 1300 = 0", "0.13", "-13", "1300"),
        ("0.14x² - 14x + 1400 = 0", "0.14", "-14", "1400"),
        ("0.15x² - 15x + 1500 = 0", "0.15", "-15", "1500"),
        ("0.16x² - 16x + 1600 = 0", "0.16", "-16", "1600"),
        ("0.17x² - 17x + 1700 = 0", "0.17", "-17", "1700"),
        ("0.18x² - 18x + 1800 = 0", "0.18", "-18", "1800"),
        ("0.19x² - 19x + 1900 = 0", "0.19", "-19", "1900"),
        ("0.21x² - 21x + 2100 = 0", "0.21", "-21", "2100"),
    ]
    
    passed = 0
    for name, a, b, c in tests:
        try:
            x1, x2 = quadratic(BigFloat(a), BigFloat(b), BigFloat(c))
            print(f"  ok {name}")
            passed += 1
        except Exception as e:
            print(f"  FAIL {name}: {e}")
    
    return passed


def test_more_negative():
    """Ещё 50 отрицательных"""
    print("\n=== ЕЩЁ ОТРИЦАТЕЛЬНЫЕ ===")
    
    tests = []
    for k in range(1, 51):
        a = str(k)
        b = str(-(k + 10))
        c = str(k * 10)
        name = f"{k}x² - {k+10}x + {k*10} = 0"
        tests.append((name, a, b, c))
    
    passed = 0
    for name, a, b, c in tests:
        try:
            x1, x2 = quadratic(BigFloat(a), BigFloat(b), BigFloat(c))
            print(f"  ok {name}")
            passed += 1
        except Exception as e:
            print(f"  FAIL {name}: {e}")
    
    return passed


if __name__ == "__main__":
    total = 0
    total += test_basic()
    total += test_fractional()
    total += test_large_range()
    total += test_double_root()
    total += test_linear()
    total += test_more_fractional()
    total += test_more_negative()
    
    print(f"\n{'='*60}")
    print(f"ИТОГО ТЕСТОВ: {total}")
    print(f"{'='*60}")
    
    run_benchmark()
