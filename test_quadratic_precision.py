#!/usr/bin/env python3
"""Этап 1: Анализ проблемы точности quadratic"""

import sys
sys.set_int_max_str_digits(200000)

from bigfloat_v2 import BigFloat, quadratic
import math
import random

def pattern_111(n):
    return "1" * n

def pattern_222(n):
    return "2" * n

def pattern_333(n):
    return "3" * n

def pattern_123(n):
    seq = "1234567890"
    return (seq * (n // 10 + 1))[:n]

def pattern_321(n):
    seq = "9876543210"
    return (seq * (n // 10 + 1))[:n]

def pattern_1010(n):
    return ("10" * (n // 2 + 1))[:n]

def pattern_1212(n):
    return ("12" * (n // 2 + 1))[:n]

def pattern_123123(n):
    return ("123" * (n // 3 + 1))[:n]

def pattern_pi(n):
    pi = "31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"
    return pi[:n]

def pattern_e(n):
    e = "2718281828459045235360287471352662497757247093699959574966967627724076630353547595711"
    return e[:n]

def pattern_phi(n):
    phi = "161803398874989484820458683436563811772030917980576286213544862270526046281890244970720720418939113748475408807538689175212663386222357309980527005748213"
    return phi[:n]

def pattern_primes(n):
    primes = "2357111317192329313741434753596167717978389119710910310211112113113117"
    return (primes * (n // 50 + 1))[:n]

def pattern_fib(n):
    fib = "1123581321345589144233377610987150977056929717983691686352469148510395664"
    return (fib * (n // 64 + 1))[:n]

def generate_tests_100():
    tests = []
    
    patterns = [
        ("111", pattern_111),
        ("222", pattern_222),
        ("333", pattern_333),
        ("123", pattern_123),
        ("321", pattern_321),
        ("1010", pattern_1010),
        ("1212", pattern_1212),
        ("123123", pattern_123123),
        ("pi", pattern_pi),
        ("e", pattern_e),
        ("phi", pattern_phi),
        ("primes", pattern_primes),
        ("fib", pattern_fib),
    ]
    
    lengths = [10, 20, 50, 100, 200, 500, 1000]
    
    for i in range(100):
        len1 = lengths[i % len(lengths)]
        len2 = lengths[(i * 3 + 1) % len(lengths)]
        
        pat1_name, pat1_func = patterns[i % len(patterns)]
        pat2_name, pat2_func = patterns[(i * 7 + 3) % len(patterns)]
        
        x1_str = pat1_func(len1)
        x2_str = pat2_func(len2)
        
        a = BigFloat("1")
        x1 = BigFloat(x1_str)
        x2 = BigFloat(x2_str)
        b = -(x1 + x2)
        c = x1 * x2
        
        tests.append({
            'id': i,
            'x1_str': x1_str,
            'x2_str': x2_str,
            'x1': x1,
            'x2': x2,
            'a': a,
            'b': b,
            'c': c,
            'pat1': pat1_name,
            'pat2': pat2_name,
        })
    
    return tests


def verify_root(a, b, c, x):
    ax2 = a * x * x
    bx = b * x
    result = ax2 + bx + c
    abs_result = result if result >= 0 else -result
    abs_c = c if c >= 0 else -c
    if abs_c._is_zero():
        rel_error = abs_result
    else:
        rel_error = abs_result / abs_c
    return abs_result, rel_error


def run_tests():
    print("=" * 70)
    print("ЭТАП 1: АНАЛИЗ ПРОБЛЕМЫ ТОЧНОСТИ")
    print("=" * 70)
    
    tests = generate_tests_100()
    passed = 0
    failed = 0
    errors = []
    
    for test in tests[:10]:  # Сначала 10 для анализа
        tid = test['id']
        print(f"\n--- Тест {tid} ---")
        print(f"  x1 ({test['pat1']}): {test['x1_str'][:20]}...")
        print(f"  x2 ({test['pat2']}): {test['x2_str'][:20]}...")
        print(f"  a.max_digits = {test['a'].max_digits}")
        print(f"  b.max_digits = {test['b'].max_digits}")
        print(f"  c.max_digits = {test['c'].max_digits}")
        
        # Debug внутренних операций
        b_sq = test['b'] * test['b']
        four_ac = test['a'] * test['c'] * BigFloat("4")
        D = b_sq - four_ac
        
        print(f"  b*b.max_digits = {b_sq.max_digits}")
        print(f"  4ac.max_digits = {four_ac.max_digits}")
        print(f"  D.max_digits = {D.max_digits}")
        
        try:
            x1_r, x2_r = quadratic(test['a'], test['b'], test['c'])
            
            abs1, rel1 = verify_root(test['a'], test['b'], test['c'], x1_r)
            abs2, rel2 = verify_root(test['a'], test['b'], test['c'], x2_r)
            
            print(f"  x1_r: {str(x1_r)[:30]}...")
            print(f"  x2_r: {str(x2_r)[:30]}...")
            print(f"  rel_err x1: {str(rel1)[:20]}")
            print(f"  rel_err x2: {str(rel2)[:20]}")
            
            threshold = BigFloat("0.0000000001")
            if rel1 < threshold and rel2 < threshold:
                passed += 1
                print(f"  STATUS: OK")
            else:
                failed += 1
                errors.append({'id': tid, 'rel1': str(rel1), 'rel2': str(rel2)})
                print(f"  STATUS: FAIL")
                
        except Exception as e:
            failed += 1
            errors.append({'id': tid, 'error': str(e)})
            print(f"  ERROR: {e}")
    
    # Остальные 90 тестов без детального вывода
    for test in tests[10:]:
        try:
            x1_r, x2_r = quadratic(test['a'], test['b'], test['c'])
            _, rel1 = verify_root(test['a'], test['b'], test['c'], x1_r)
            _, rel2 = verify_root(test['a'], test['b'], test['c'], x2_r)
            
            threshold = BigFloat("0.0000000001")
            if rel1 < threshold and rel2 < threshold:
                passed += 1
            else:
                failed += 1
                errors.append({'id': test['id'], 'rel1': str(rel1)[:20], 'rel2': str(rel2)[:20]})
        except Exception as e:
            failed += 1
            errors.append({'id': test['id'], 'error': str(e)[:50]})
    
    print("\n" + "=" * 70)
    print(f"РЕЗУЛЬТАТ: {passed}/100 passed, {failed}/100 failed")
    print("=" * 70)
    
    if errors:
        print(f"\nОшибки ({min(10, len(errors))}):")
        for e in errors[:10]:
            if 'error' in e:
                print(f"  Тест {e['id']}: ERROR - {e['error']}")
            else:
                print(f"  Тест {e['id']}: rel1={e['rel1'][:15]}, rel2={e['rel2'][:15]}")
    
    return passed, failed


if __name__ == "__main__":
    run_tests()
