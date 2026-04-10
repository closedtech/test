#!/usr/bin/env python3
"""100+ тестов sqrt с правильным max_digits"""

import sys
sys.set_int_max_str_digits(200000)

from bigfloat_v2 import BigFloat
import time


def test_sqrt_correct():
    """Проверка sqrt с правильным max_digits (7 тестов)"""
    print("=" * 60)
    print("ПРОВЕРКА: sqrt с max_digits")
    print("=" * 60)
    
    tests = [
        (10, 11), (50, 51), (100, 101), (500, 501),
        (1000, 1001), (5000, 5001), (10000, 10001),
    ]
    
    passed = 0
    failed = 0
    
    for n, needed_digits in tests:
        pow_n = "1" + "0" * n
        expected_exp = n // 2
        
        try:
            a = BigFloat(pow_n, max_digits=needed_digits + 100)
            result = a.sqrt()
            result_str = str(result)
            expected = "1" + "0" * expected_exp
            
            if result_str.startswith(expected):
                print(f"  ok sqrt(10^{n})")
                passed += 1
            else:
                print(f"  FAIL sqrt(10^{n})")
                failed += 1
        except Exception as e:
            print(f"  ERROR sqrt(10^{n}): {e}")
            failed += 1
    
    return passed, failed


def test_sqrt_basics():
    """Базовые тесты (20)"""
    print("\n" + "=" * 60)
    print("БАЗОВЫЕ ТЕСТЫ (20)")
    print("=" * 60)
    
    tests = [
        ("sqrt(0)", "0"), ("sqrt(1)", "1"), ("sqrt(4)", "2"), ("sqrt(9)", "3"),
        ("sqrt(16)", "4"), ("sqrt(25)", "5"), ("sqrt(36)", "6"), ("sqrt(49)", "7"),
        ("sqrt(64)", "8"), ("sqrt(81)", "9"), ("sqrt(100)", "10"), ("sqrt(121)", "11"),
        ("sqrt(144)", "12"), ("sqrt(169)", "13"), ("sqrt(196)", "14"), ("sqrt(225)", "15"),
        ("sqrt(256)", "16"), ("sqrt(289)", "17"), ("sqrt(324)", "18"), ("sqrt(361)", "19"),
    ]
    
    passed = 0
    for name, expected in tests:
        try:
            num = name.split("(")[1].rstrip(")")
            result = str(BigFloat(num).sqrt())
            if result.startswith(expected) or result == expected:
                print(f"  ok {name} = {result}")
                passed += 1
            else:
                print(f"  FAIL {name}")
        except Exception as e:
            print(f"  ERROR {name}: {e}")
    
    return passed, 20 - passed


def test_sqrt_fractional():
    """Дробные тесты (20)"""
    print("\n" + "=" * 60)
    print("ДРОБНЫЕ ТЕСТЫ (20)")
    print("=" * 60)
    
    tests = [
        ("sqrt(0.25)", "0.5"), ("sqrt(0.04)", "0.2"), ("sqrt(0.0001)", "0.01"),
        ("sqrt(0.01)", "0.1"), ("sqrt(0.09)", "0.3"), ("sqrt(0.36)", "0.6"),
        ("sqrt(0.49)", "0.7"), ("sqrt(0.81)", "0.9"), ("sqrt(2.25)", "1.5"),
        ("sqrt(3.24)", "1.8"), ("sqrt(4.41)", "2.1"), ("sqrt(5.29)", "2.3"),
        ("sqrt(6.25)", "2.5"), ("sqrt(6.76)", "2.6"), ("sqrt(7.29)", "2.7"),
        ("sqrt(7.84)", "2.8"), ("sqrt(8.41)", "2.9"), ("sqrt(9)", "3"),
        ("sqrt(10.24)", "3.2"), ("sqrt(12.25)", "3.5"),
    ]
    
    passed = 0
    for name, expected in tests:
        try:
            num = name.split("(")[1].rstrip(")")
            result = str(BigFloat(num).sqrt())
            if result.startswith(expected):
                print(f"  ok {name} = {result}")
                passed += 1
            else:
                print(f"  FAIL {name}")
        except Exception as e:
            print(f"  ERROR {name}: {e}")
    
    return passed, 20 - passed


def test_sqrt_large():
    """Большие числа (30)"""
    print("\n" + "=" * 60)
    print("БОЛЬШИЕ ЧИСЛА (30)")
    print("=" * 60)
    
    sizes = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100,
             150, 200, 300, 400, 500, 600, 700, 800, 900, 1000,
             1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 7500, 10000]
    
    passed = 0
    failed = 0
    
    for n in sizes:
        try:
            pow_n = "1" + "0" * n
            a = BigFloat(pow_n, max_digits=n + 101)
            result = a.sqrt()
            result_str = str(result)
            expected_exp = n // 2
            expected = "1" + "0" * expected_exp
            
            if result_str.startswith(expected):
                print(f"  ok sqrt(10^{n})")
                passed += 1
            else:
                print(f"  FAIL sqrt(10^{n})")
                failed += 1
        except Exception as e:
            print(f"  ERROR sqrt(10^{n}): {e}")
            failed += 1
    
    return passed, failed


def test_sqrt_verification():
    """Проверка sqrt(x)^2 = x (20)"""
    print("\n" + "=" * 60)
    print("ПРОВЕРКА: sqrt(x)^2 = x (20)")
    print("=" * 60)
    
    tests = [
        "2", "3", "5", "7", "10", "17", "99", "100", "101", "997",
        "0.5", "0.25", "0.04", "0.0001", "0.000001", "0.0000001",
        "0.00000001", "0.000000001", "0.0000000001", "0.00000000001"
    ]
    
    passed = 0
    failed = 0
    
    for num_str in tests:
        try:
            a = BigFloat(num_str)
            sqrt_a = a.sqrt()
            sqrt_a_sq = sqrt_a * sqrt_a
            diff = sqrt_a_sq - a
            abs_diff = diff if diff >= 0 else -diff
            abs_a = a if a >= 0 else -a
            
            rel_err = abs_diff / abs_a if not abs_a._is_zero() else abs_diff
            
            if rel_err < BigFloat("0.0000000001"):
                print(f"  ok sqrt({num_str})^2")
                passed += 1
            else:
                print(f"  FAIL sqrt({num_str})^2")
                failed += 1
        except Exception as e:
            print(f"  ERROR sqrt({num_str}): {e}")
            failed += 1
    
    return passed, failed


def benchmark_sqrt():
    """Benchmark sqrt"""
    print("\n" + "=" * 60)
    print("BENCHMARK sqrt")
    print("=" * 60)
    
    sizes = [10, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
    
    for size in sizes:
        pow_n = "1" + "0" * size
        a = BigFloat(pow_n, max_digits=size + 101)
        
        iterations = max(1, 100 // size)
        
        start = time.time()
        for _ in range(iterations):
            _ = a.sqrt()
        elapsed = (time.time() - start) * 1000 / iterations
        
        print(f"  sqrt(10^{size}): {elapsed:.4f} ms ({iterations} iter)")


def run_all():
    total_passed = 0
    total_failed = 0
    
    p, f = test_sqrt_correct()
    total_passed += p
    total_failed += f
    
    p, f = test_sqrt_basics()
    total_passed += p
    total_failed += f
    
    p, f = test_sqrt_fractional()
    total_passed += p
    total_failed += f
    
    p, f = test_sqrt_large()
    total_passed += p
    total_failed += f
    
    p, f = test_sqrt_verification()
    total_passed += p
    total_failed += f
    
    print("\n" + "=" * 60)
    print(f"ИТОГО: {total_passed} passed, {total_failed} failed")
    print("=" * 60)
    
    benchmark_sqrt()


if __name__ == "__main__":
    run_all()
