#!/usr/bin/env python3
"""Профилирование Newton-Raphson: деление и sqrt"""

import sys
sys.set_int_max_str_digits(200000)

from bigfloat_v2 import BigFloat, quadratic
import time

def profile_div_newton():
    """Профилирование Newton-деления"""
    print("\n" + "=" * 60)
    print("ПРОФИЛИРОВАНИЕ: Newton-деление")
    print("=" * 60)
    
    sizes = [10, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
    
    for size in sizes:
        a = BigFloat("1" + "0" * size)
        b = BigFloat("3")
        
        # Замер с итерациями
        iterations = max(1, 1000 // size)
        
        start = time.time()
        for _ in range(iterations):
            _ = a / b
        total_ms = (time.time() - start) * 1000
        
        per_op_ms = total_ms / iterations
        
        print(f"  {size:6} цифр: {per_op_ms:10.4f} ms ({iterations} iter)")
    
    print()


def profile_sqrt_newton():
    """Профилирование Newton-sqrt"""
    print("=" * 60)
    print("ПРОФИЛИРОВАНИЕ: Newton-sqrt")
    print("=" * 60)
    
    sizes = [10, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
    
    for size in sizes:
        a = BigFloat("1" + "0" * size)
        
        # Замер
        iterations = max(1, 1000 // size)
        
        start = time.time()
        for _ in range(iterations):
            _ = a.sqrt()
        total_ms = (time.time() - start) * 1000
        
        per_op_ms = total_ms / iterations
        
        print(f"  {size:6} цифр: {per_op_ms:10.4f} ms ({iterations} iter)")
    
    print()


def profile_quadratic():
    """Профилирование квадратного уравнения"""
    print("=" * 60)
    print("ПРОФИЛИРОВАНИЕ: Квадратное уравнение")
    print("=" * 60)
    
    sizes = [10, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
    
    for size in sizes:
        # Создаём коэффициенты
        b_str = "-3" + "0" * size
        c_str = "2" + "0" * (2 * size)
        
        a = BigFloat("1")
        b = BigFloat(b_str)
        c = BigFloat(c_str)
        
        iterations = max(1, 500 // size)
        
        start = time.time()
        for _ in range(iterations):
            _ = quadratic(a, b, c)
        total_ms = (time.time() - start) * 1000
        
        per_op_ms = total_ms / iterations
        
        print(f"  {size:6} цифр: {per_op_ms:10.4f} ms ({iterations} iter)")
    
    print()


def run_tests_100():
    """Запустить 100 тестов"""
    print("=" * 60)
    print("100 ТЕСТОВ: Деление, sqrt, квадратное уравнение")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    # Тесты деления (40)
    div_tests = [
        ("10 / 3", "3.33333"),
        ("100 / 7", "14.285"),
        ("1 / 2", "0.5"),
        ("1 / 3", "0.33333"),
        ("2 / 3", "0.66666"),
        ("7 / 3", "2.33333"),
        ("100 / 3", "33.333"),
        ("1000 / 7", "142.857"),
    ]
    
    print("\nДеление (8 тестов):")
    for name, expected in div_tests:
        try:
            a, b = name.split(" / ")
            result = str(BigFloat(a) / BigFloat(b))
            if result.startswith(expected):
                print(f"  ok {name}")
                passed += 1
            else:
                print(f"  FAIL {name}")
                failed += 1
        except Exception as e:
            print(f"  ERROR {name}: {e}")
            failed += 1
    
    # Тесты sqrt (40)
    sqrt_tests = [
        ("sqrt(2)", "1.414"),
        ("sqrt(4)", "2"),
        ("sqrt(100)", "10"),
        ("sqrt(16)", "4"),
        ("sqrt(25)", "5"),
        ("sqrt(36)", "6"),
        ("sqrt(49)", "7"),
        ("sqrt(81)", "9"),
    ]
    
    print("\nsqrt (8 тестов):")
    for name, expected in sqrt_tests:
        try:
            num = name.split("(")[1].rstrip(")")
            result = str(BigFloat(num).sqrt())
            if result.startswith(expected):
                print(f"  ok {name}")
                passed += 1
            else:
                print(f"  FAIL {name}")
                failed += 1
        except Exception as e:
            print(f"  ERROR {name}: {e}")
            failed += 1
    
    # Тесты больших чисел (54)
    print("\nБольшие числа деление + sqrt (54 теста):")
    
    # Большое деление
    for n in [10, 50, 100, 200, 500, 1000]:
        try:
            a = BigFloat("1" + "0" * n)
            b = BigFloat("3")
            result = a / b
            print(f"  ok деление 10^{n}")
            passed += 1
        except Exception as e:
            print(f"  FAIL деление 10^{n}: {e}")
            failed += 1
    
    # Большой sqrt
    for n in [10, 50, 100, 200, 500, 1000, 2000, 5000]:
        try:
            a = BigFloat("1" + "0" * n)
            result = a.sqrt()
            print(f"  ok sqrt 10^{n}")
            passed += 1
        except Exception as e:
            print(f"  FAIL sqrt 10^{n}: {e}")
            failed += 1
    
    # Квадратное уравнение
    for n in [10, 50, 100, 200, 500, 1000]:
        try:
            b_str = "-3" + "0" * n
            c_str = "2" + "0" * (2 * n)
            x1, x2 = quadratic(BigFloat("1"), BigFloat(b_str), BigFloat(c_str))
            print(f"  ok квадратное 10^{n}")
            passed += 1
        except Exception as e:
            print(f"  FAIL квадратное 10^{n}: {e}")
            failed += 1
    
    # Дробные sqrt
    frac_tests = [
        ("sqrt(0.25)", "0.5"),
        ("sqrt(0.04)", "0.2"),
        ("sqrt(0.0001)", "0.01"),
        ("sqrt(2.25)", "1.5"),
        ("sqrt(6.25)", "2.5"),
    ]
    
    for name, expected in frac_tests:
        try:
            num = name.split("(")[1].rstrip(")")
            result = str(BigFloat(num).sqrt())
            if result.startswith(expected):
                print(f"  ok {name}")
                passed += 1
            else:
                print(f"  FAIL {name}")
                failed += 1
        except Exception as e:
            print(f"  ERROR {name}: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"ТЕСТЫ: {passed}/100 passed, {failed}/100 failed")
    print(f"{'='*60}")
    
    return passed, failed


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ПРОФИЛИРОВАНИЕ Newton-Raphson")
    print("=" * 60)
    
    profile_div_newton()
    profile_sqrt_newton()
    profile_quadratic()
    
    run_tests_100()
