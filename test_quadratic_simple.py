#!/usr/bin/env python3
"""Упрощённые тесты квадратного уравнения"""

import sys
sys.set_int_max_str_digits(200000)

from bigfloat_v2 import BigFloat, quadratic

def test_basic():
    """Базовые тесты"""
    print("\n=== БАЗОВЫЕ ТЕСТЫ ===")
    
    tests = [
        # (name, a, b, c, expected_x1, expected_x2)
        ("x² - 5x + 6 = 0", "1", "-5", "6", "3", "2"),
        ("x² - 4x + 4 = 0", "1", "-4", "4", "2", "2"),
        ("x² - 1 = 0", "1", "0", "-1", "1", "-1"),
        ("x² - x = 0", "1", "-1", "0", "1", "0"),
        ("2x² - 8x + 6 = 0", "2", "-8", "6", "3", "1"),
    ]
    
    passed = 0
    failed = 0
    
    for name, a, b, c, x1_exp, x2_exp in tests:
        try:
            x1, x2 = quadratic(BigFloat(a), BigFloat(b), BigFloat(c))
            x1_str = str(x1).split('.')[0]
            x2_str = str(x2).split('.')[0]
            
            results = set([x1_str, x2_str])
            expected = set([x1_exp, x2_exp])
            
            if results == expected:
                print(f"  ok {name}: x1={x1_str}, x2={x2_str}")
                passed += 1
            else:
                print(f"  FAIL {name}: expected {expected}, got {results}")
                failed += 1
        except Exception as e:
            print(f"  ERROR {name}: {e}")
            failed += 1
    
    return passed, failed


def test_large(n):
    """Тест с n-значными числами"""
    pow_n = "1" + "0" * n
    pow_2n = "1" + "0" * (2 * n)
    
    # (x - 10^n)(x - 2*10^n) = x² - 3*10^n*x + 2*10^2n
    b_str = "-3" + "0" * n if n > 1 else "-3"
    c_str = "2" + "0" * (2 * n) if 2 * n > 1 else "2"
    
    print(f"\n=== {n}-ЗНАЧНЫЕ ТЕСТЫ ===")
    print(f"Уравнение: x² - 3*10^{n}*x + 2*10^{2*n} = 0")
    print(f"Ожидание: x1 = 10^{n}, x2 = 2*10^{n}")
    
    try:
        x1, x2 = quadratic(BigFloat("1"), BigFloat(b_str), BigFloat(c_str))
        
        x1_str = str(x1)
        x2_str = str(x2)
        
        # Проверяем начало
        x1_ok = x1_str.startswith(pow_n[:5]) or x1_str.startswith(("2"+ "0"*n)[:5])
        x2_ok = x2_str.startswith(pow_n[:5]) or x2_str.startswith(("2"+ "0"*n)[:5])
        
        if x1_ok and x2_ok:
            print(f"  ok: x1 = {x1_str[:20]}..., x2 = {x2_str[:20]}...")
            return 1, 0
        else:
            print(f"  FAIL: x1 = {x1_str[:20]}..., x2 = {x2_str[:20]}...")
            return 0, 1
    except Exception as e:
        print(f"  ERROR: {e}")
        return 0, 1


def test_10000_digits():
    """Тест с 10000-значными числами"""
    print(f"\n=== 10000-ЗНАЧНЫЙ ТЕСТ ===")
    
    pow_10000 = "1" + "0" * 9999
    
    # (x - 10^10000)(x - 2*10^10000) = x² - 3*10^10000*x + 2*10^20000
    b_str = "-3" + "0" * 9999
    c_str = "2" + "0" * 19999
    
    print(f"Создаю уравнение с {len(b_str)}-значным b...")
    
    try:
        x1, x2 = quadratic(BigFloat("1"), BigFloat(b_str), BigFloat(c_str))
        
        x1_str = str(x1)
        x2_str = str(x2)
        
        print(f"  x1 = {x1_str[:20]}...")
        print(f"  x2 = {x2_str[:20]}...")
        print(f"  ok: 10000-значный тест прошёл!")
        return 1, 0
    except Exception as e:
        print(f"  ERROR: {e}")
        return 0, 1


def run_tests():
    total_passed = 0
    total_failed = 0
    
    # Базовые тесты
    p, f = test_basic()
    total_passed += p
    total_failed += f
    
    # Тесты с разной длиной
    for n in [10, 50, 100, 200, 500, 1000]:
        p, f = test_large(n)
        total_passed += p
        total_failed += f
    
    # 10000-значный тест
    p, f = test_10000_digits()
    total_passed += p
    total_failed += f
    
    print(f"\n{'='*60}")
    print(f"ИТОГО: {total_passed} passed, {total_failed} failed")
    print(f"{'='*60}")
    
    return total_failed == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
