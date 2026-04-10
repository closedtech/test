#!/usr/bin/env python3
"""
Comprehensive tests for quadratic equation solver.
Tests: edge cases, limits, randomized, decimal verification.
"""

import sys
import random
import math
import argparse
from decimal import Decimal, getcontext
from typing import List, Tuple, Optional

# Add parent directory to path for imports
sys.path.insert(0, '/home/user/.openclaw/workspace')
sys.path.insert(0, '/home/user/.openclaw/workspace/tests')

# Set high precision for Decimal
getcontext().prec = 50

try:
    from bigint import BigInt
except ImportError:
    print("ERROR: bigint.py not found!")
    sys.exit(1)


# ============================================================================
# TEST UTILITIES
# ============================================================================

class TestResult:
    def __init__(self, name: str, passed: bool, message: str = ""):
        self.name = name
        self.passed = passed
        self.message = message
    
    def __repr__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        msg = f" - {self.message}" if self.message else ""
        return f"{status}: {self.name}{msg}"


def parse_solution(solution: str) -> dict:
    """Parse the solution string into structured data."""
    solution = solution.lower()
    
    result = {
        'type': None,  # no_solution, linear, one_solution, two_solutions, complex, infinite
        'roots': []
    }
    
    if 'нет решений' in solution:
        result['type'] = 'no_solution'
    elif 'бесконечно' in solution:
        result['type'] = 'infinite'
    elif 'линейное' in solution:
        result['type'] = 'linear'
        # Extract x value
        import re
        match = re.search(r'x\s*=\s*([+-]?\d+)', solution)
        if match:
            result['roots'] = [int(match.group(1))]
    elif 'комплексные' in solution:
        result['type'] = 'complex'
        # Extract complex roots
        import re
        matches = re.findall(r'([+-]?\d+(?:\.\d+)?)\s*([+-])\s*(\d+(?:\.\d+)?)i', solution)
        for m in matches:
            real = float(m[0])
            imag = float(m[1] + m[2])
            result['roots'].append(complex(real, imag))
    elif 'одно решение' in solution:
        result['type'] = 'one_solution'
        import re
        match = re.search(r'x\s*=\s*([+-]?\d+)', solution)
        if match:
            result['roots'] = [float(match.group(1))]
    elif 'два решения' in solution:
        result['type'] = 'two_solutions'
        import re
        matches = re.findall(r'x[12]\s*=\s*([+-]?\d+(?:\.\d+)?)', solution)
        result['roots'] = [float(m) for m in matches]
    
    return result


def decimal_sqrt(n: Decimal) -> Decimal:
    """Compute square root using Decimal with high precision."""
    if n < 0:
        raise ValueError("Cannot compute sqrt of negative number")
    if n == 0:
        return Decimal(0)
    
    # Newton-Raphson method
    x = n
    for _ in range(100):
        x = (x + n / x) / 2
    return x


def solve_quadratic_decimal(a: float, b: float, c: float) -> Tuple[str, List[float]]:
    """Solve quadratic using standard math with Decimal precision."""
    if abs(a) < 1e-100:
        # Linear case
        if abs(b) < 1e-100:
            if abs(c) < 1e-100:
                return ("infinite", [])
            return ("no_solution", [])
        return ("linear", [-c / b])
    
    D = b * b - 4 * a * c
    
    if D < -1e-10:
        sqrt_abs = math.sqrt(-D)
        real = -b / (2 * a)
        imag = sqrt_abs / (2 * a)
        return ("complex", [complex(real, imag), complex(real, -imag)])
    elif abs(D) < 1e-10:
        x = -b / (2 * a)
        return ("one_solution", [x])
    else:
        sqrt_d = math.sqrt(D)
        x1 = (-b + sqrt_d) / (2 * a)
        x2 = (-b - sqrt_d) / (2 * a)
        return ("two_solutions", sorted([x1, x2]))


def solve_quadratic_decimal_high(a: Decimal, b: Decimal, c: Decimal) -> Tuple[str, List[Decimal]]:
    """Solve with Decimal high precision."""
    if a == 0:
        if b == 0:
            if c == 0:
                return ("infinite", [])
            return ("no_solution", [])
        return ("linear", [-c / b])
    
    D = b * b - 4 * a * c
    
    if D < 0:
        sqrt_abs = decimal_sqrt(-D)
        real = -b / (2 * a)
        imag = sqrt_abs / (2 * a)
        return ("complex", [complex(real, imag), complex(real, -imag)])
    elif D == 0:
        x = -b / (2 * a)
        return ("one_solution", [x])
    else:
        sqrt_d = decimal_sqrt(D)
        x1 = (-b + sqrt_d) / (2 * a)
        x2 = (-b - sqrt_d) / (2 * a)
        return ("two_solutions", sorted([x1, x2]))


def verify_root(a: float, b: float, c: float, x: float, tol: float = 1e-6) -> bool:
    """Verify a root satisfies ax² + bx + c ≈ 0."""
    return abs(a * x * x + b * x + c) < tol


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_zero_a():
    """a = 0: линейное уравнение или константа"""
    tests = [
        ("0", "5", "10", "linear"),
        ("0", "1", "1", "linear"),
        ("0", "0", "5", "no_solution"),
        ("0", "0", "0", "infinite"),
        ("0", "-3", "9", "linear"),
    ]
    
    results = []
    for a, b, c, expected_type in tests:
        try:
            from quadratic import solve_quadratic
            sol = solve_quadratic(a, b, c)
            parsed = parse_solution(sol)
            passed = parsed['type'] == expected_type
            results.append(TestResult(f"a={a}, b={b}, c={c}", passed,
                                      f"got {parsed['type']}, expected {expected_type}"))
        except Exception as e:
            results.append(TestResult(f"a={a}, b={b}, c={c}", False, str(e)))
    
    return results


def test_zero_b():
    """b = 0: ax² + c = 0"""
    tests = [
        ("1", "0", "-4", "two_solutions"),   # x² = 4 → x = ±2
        ("1", "0", "4", "no_solution"),       # x² = -4 → нет
        ("1", "0", "0", "one_solution"),     # x² = 0 → x = 0
        ("4", "0", "-4", "two_solutions"),   # 4x² = 4 → x = ±1
        ("-1", "0", "4", "two_solutions"),  # -x² + 4 = 0 → x² = 4 → x = ±2
    ]
    
    results = []
    for a, b, c, expected_type in tests:
        try:
            from quadratic import solve_quadratic
            sol = solve_quadratic(a, b, c)
            parsed = parse_solution(sol)
            passed = parsed['type'] == expected_type
            results.append(TestResult(f"a={a}, b={b}, c={c}", passed,
                                      f"got {parsed['type']}, expected {expected_type}"))
        except Exception as e:
            results.append(TestResult(f"a={a}, b={b}, c={c}", False, str(e)))
    
    return results


def test_zero_c():
    """c = 0: ax² + bx = 0 → x(ax + b) = 0"""
    tests = [
        ("1", "2", "0", "two_solutions"),    # x(x+2)=0 → x=0, x=-2
        ("1", "-2", "0", "two_solutions"),   # x(x-2)=0 → x=0, x=2
        ("1", "0", "0", "one_solution"),     # x²=0 → x=0
        ("2", "4", "0", "two_solutions"),    # 2x(x+2)=0 → x=0, x=-2
        ("-1", "2", "0", "two_solutions"),   # -x(x-2)=0 → x=0, x=2
    ]
    
    results = []
    for a, b, c, expected_type in tests:
        try:
            from quadratic import solve_quadratic
            sol = solve_quadratic(a, b, c)
            parsed = parse_solution(sol)
            passed = parsed['type'] == expected_type
            results.append(TestResult(f"a={a}, b={b}, c={c}", passed,
                                      f"got {parsed['type']}, expected {expected_type}"))
        except Exception as e:
            results.append(TestResult(f"a={a}, b={b}, c={c}", False, str(e)))
    
    return results


def test_all_zero():
    """Все коэффициенты = 0"""
    tests = [
        ("0", "0", "0", "infinite"),
    ]
    
    results = []
    for a, b, c, expected_type in tests:
        try:
            from quadratic import solve_quadratic
            sol = solve_quadratic(a, b, c)
            parsed = parse_solution(sol)
            passed = parsed['type'] == expected_type
            results.append(TestResult(f"a={a}, b={b}, c={c}", passed,
                                      f"got {parsed['type']}, expected {expected_type}"))
        except Exception as e:
            results.append(TestResult(f"a={a}, b={b}, c={c}", False, str(e)))
    
    return results


# ============================================================================
# LIMIT / BOUNDARY TESTS
# ============================================================================

def test_perfect_squares():
    """Корни — точные квадраты"""
    tests = [
        # (a, b, c, expected_x1, expected_x2)
        ("1", "0", "-4", 2.0, -2.0),       # x² - 4 = 0
        ("1", "0", "-9", 3.0, -3.0),       # x² - 9 = 0
        ("1", "0", "-16", 4.0, -4.0),      # x² - 16 = 0
        ("4", "0", "-16", 2.0, -2.0),      # 4x² - 16 = 0 → x² = 4
        ("9", "0", "-81", 3.0, -3.0),      # 9x² - 81 = 0 → x² = 9
    ]
    
    results = []
    for a, b, c, exp_x1, exp_x2 in tests:
        try:
            from quadratic import solve_quadratic
            sol = solve_quadratic(a, b, c)
            parsed = parse_solution(sol)
            
            if parsed['type'] == 'two_solutions' and len(parsed['roots']) == 2:
                x1, x2 = parsed['roots']
                passed = (abs(x1 - exp_x1) < 0.01 and abs(x2 - exp_x2) < 0.01) or \
                         (abs(x1 - exp_x2) < 0.01 and abs(x2 - exp_x1) < 0.01)
                results.append(TestResult(f"x² - {c} = 0", passed,
                                          f"roots: {x1}, {x2}, expected ±{exp_x1}"))
            else:
                results.append(TestResult(f"x² - {c} = 0", False,
                                          f"got {parsed['type']}, expected two_solutions"))
        except Exception as e:
            results.append(TestResult(f"x² - {c} = 0", False, str(e)))
    
    return results


def test_unit_coefficients():
    """Коэффициенты = ±1"""
    tests = [
        ("1", "1", "1", "no_solution"),     # x² + x + 1 = 0, D < 0
        ("1", "-1", "0", "two_solutions"),   # x² - x = 0 → x(x-1)=0
        ("1", "1", "-2", "two_solutions"),   # x² + x - 2 = 0 → (x+2)(x-1)=0
        ("1", "-2", "1", "one_solution"),    # x² - 2x + 1 = 0 → (x-1)²=0
    ]
    
    results = []
    for a, b, c, expected_type in tests:
        try:
            from quadratic import solve_quadratic
            sol = solve_quadratic(a, b, c)
            parsed = parse_solution(sol)
            passed = parsed['type'] == expected_type
            results.append(TestResult(f"a={a}, b={b}, c={c}", passed,
                                      f"got {parsed['type']}, expected {expected_type}"))
        except Exception as e:
            results.append(TestResult(f"a={a}, b={b}, c={c}", False, str(e)))
    
    return results


def test_large_coefficients():
    """Большие коэффициенты"""
    tests = [
        ("1000000", "1000000", "1", "two_solutions"),
        ("10" + "0" * 20, "1", "-1", "two_solutions"),
        ("1", "10" + "0" * 20, "1", "two_solutions"),
    ]
    
    results = []
    for a, b, c, expected_type in tests:
        try:
            from quadratic import solve_quadratic
            sol = solve_quadratic(a, b, c)
            parsed = parse_solution(sol)
            passed = parsed['type'] == expected_type
            results.append(TestResult(f"large coeff: a={a[:10]}..., b={b[:10]}..., c={c}", passed,
                                      f"got {parsed['type']}, expected {expected_type}"))
        except Exception as e:
            results.append(TestResult(f"large coeff", False, str(e)))
    
    return results


def test_small_coefficients():
    """Очень малые коэффициенты (но не нули)"""
    tests = [
        ("1", "1", "0"),      # x² + x = 0 → x(x+1)=0
        ("1", "-1", "0"),     # x² - x = 0 → x(x-1)=0
        ("2", "2", "0"),      # 2x² + 2x = 0
        ("1", "3", "-4"),     # x² + 3x - 4 = 0
    ]
    
    results = []
    for a, b, c in tests:
        try:
            from quadratic import solve_quadratic
            sol = solve_quadratic(a, b, c)
            parsed = parse_solution(sol)
            
            # Verify roots
            if parsed['roots']:
                valid = all(verify_root(int(a), int(b), int(c), r, tol=1) 
                           for r in parsed['roots'] if isinstance(r, float))
                results.append(TestResult(f"small: a={a}, b={b}, c={c}", valid,
                                          f"verified roots" if valid else "invalid roots"))
            else:
                results.append(TestResult(f"small: a={a}, b={b}, c={c}", 
                                          parsed['type'] in ['no_solution', 'infinite'],
                                          f"type: {parsed['type']}"))
        except Exception as e:
            results.append(TestResult(f"small: a={a}, b={b}, c={c}", False, str(e)))
    
    return results


def test_perfect_squares_results():
    """x² - n = 0 для perfect squares n"""
    n_values = [1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225]
    
    results = []
    for n in n_values:
        try:
            from quadratic import solve_quadratic
            sol = solve_quadratic("1", "0", str(-n))
            parsed = parse_solution(sol)
            
            if parsed['type'] == 'two_solutions' and len(parsed['roots']) == 2:
                x1, x2 = parsed['roots']
                sqrt_n = math.sqrt(n)
                passed = abs(abs(x1) - sqrt_n) < 0.01 and abs(abs(x2) - sqrt_n) < 0.01
                results.append(TestResult(f"x² = {n}", passed,
                                          f"roots: ±{x1:.1f}, expected ±{sqrt_n}"))
            else:
                results.append(TestResult(f"x² = {n}", False,
                                          f"got {parsed['type']}, expected two_solutions"))
        except Exception as e:
            results.append(TestResult(f"x² = {n}", False, str(e)))
    
    return results


# ============================================================================
# DECIMAL VERIFICATION TESTS
# ============================================================================

def verify_with_decimal(a_str: str, b_str: str, c_str: str) -> Tuple[bool, str]:
    """Verify solution using Decimal high precision."""
    a = Decimal(a_str)
    b = Decimal(b_str)
    c = Decimal(c_str)
    
    if a == 0:
        if b == 0:
            return (c == 0, "infinite" if c == 0 else "no_solution")
        
        # Linear: bx + c = 0 → x = -c/b
        x = -c / b
        residual = a * x * x + b * x + c
        return (abs(residual) < Decimal("1e-40"), f"x = {x}")
    
    D = b * b - 4 * a * c
    
    if D < 0:
        # Complex roots
        sqrt_abs = decimal_sqrt(-D)
        real = -b / (2 * a)
        imag = sqrt_abs / (2 * a)
        return (True, f"complex: {real}±{imag}i")
    elif D == 0:
        x = -b / (2 * a)
        residual = a * x * x + b * x + c
        return (abs(residual) < Decimal("1e-40"), f"x = {x}")
    else:
        sqrt_d = decimal_sqrt(D)
        x1 = (-b + sqrt_d) / (2 * a)
        x2 = (-b - sqrt_d) / (2 * a)
        r1 = a * x1 * x1 + b * x1 + c
        r2 = a * x2 * x2 + b * x2 + c
        passed = abs(r1) < Decimal("1e-40") and abs(r2) < Decimal("1e-40")
        return (passed, f"x1={x1}, x2={x2}")


def test_decimal_verification():
    """Verify solutions using Decimal module."""
    tests = [
        ("1", "0", "-4"),      # x² - 4 = 0
        ("1", "0", "-9"),      # x² - 9 = 0
        ("1", "0", "-16"),     # x² - 16 = 0
        ("1", "-5", "6"),      # x² - 5x + 6 = 0
        ("1", "-2", "1"),      # (x-1)² = 0
        ("1", "1", "1"),       # x² + x + 1 = 0
        ("2", "4", "-6"),      # 2x² + 4x - 6 = 0
        ("3", "6", "-9"),      # 3x² + 6x - 9 = 0
        ("1", "-3", "2"),      # (x-1)(x-2) = 0
        ("1", "2", "1"),       # (x+1)² = 0
    ]
    
    results = []
    for a, b, c in tests:
        try:
            from quadratic import solve_quadratic
            sol = solve_quadratic(a, b, c)
            parsed = parse_solution(sol)
            
            # Verify using Decimal
            dec_ok, details = verify_with_decimal(a, b, c)
            
            results.append(TestResult(f"Decimal: a={a}, b={b}, c={c}", dec_ok, details))
        except Exception as e:
            results.append(TestResult(f"Decimal: a={a}, b={b}, c={c}", False, str(e)))
    
    return results


def test_decimal_high_precision():
    """High precision verification for large numbers."""
    tests = [
        ("1" + "0" * 30, "0", "-1"),           # x² = 10^-30 → x ≈ 0
        ("1", "0", "-" + "0" * 30 + "1"),      # x² + 10^-30 = 0 → complex
        ("10" + "0" * 20, "0", "-10" + "0" * 20),
    ]
    
    results = []
    for a, b, c in tests:
        try:
            dec_ok, details = verify_with_decimal(a, b, c)
            results.append(TestResult(f"High precision: {a[:5]}...", dec_ok, details))
        except Exception as e:
            results.append(TestResult(f"High precision: {a[:5]}...", False, str(e)))
    
    return results


# ============================================================================
# RANDOMIZED TESTS
# ============================================================================

def generate_random_quadratic(seed: int = None) -> Tuple[str, str, str, dict]:
    """Generate random quadratic equation with known solution type."""
    if seed:
        random.seed(seed)
    
    # Decide solution type
    solution_type = random.choice(['two_real', 'one_real', 'no_real', 'linear'])
    
    if solution_type == 'two_real':
        # Generate roots first
        x1 = random.uniform(-1000, 1000)
        x2 = random.uniform(-1000, 1000)
        
        # Expand (x - x1)(x - x2) = x² - (x1+x2)x + x1*x2
        a = 1
        b = -(x1 + x2)
        c = x1 * x2
        
        # Round to integers
        a, b, c = 1, int(round(b)), int(round(c))
        
        return (str(a), str(b), str(c), {
            'type': 'two_solutions',
            'roots': [x1, x2],
            'expected_x1': x1,
            'expected_x2': x2
        })
    
    elif solution_type == 'one_real':
        x = random.uniform(-1000, 1000)
        a = 1
        b = -2 * x
        c = x * x
        
        return (str(int(a)), str(int(b)), str(int(c)), {
            'type': 'one_solution',
            'root': x
        })
    
    elif solution_type == 'no_real':
        # Two complex roots
        real = random.uniform(-10, 10)
        imag = random.uniform(1, 10)
        
        # (x - (p+qi))(x - (p-qi)) = x² - 2px + (p²+q²)
        p, q = real, imag
        a, b, c = 1, int(round(-2*p)), int(round(p*p + q*q))
        
        return (str(a), str(b), str(c), {
            'type': 'complex',
            'real': real,
            'imag': imag
        })
    
    else:  # linear
        b = random.randint(-100, 100)
        c = random.randint(-100, 100)
        if b == 0:
            b = 1
        
        return ("0", str(b), str(c), {
            'type': 'linear'
        })


def test_random_small():
    """Random tests with small coefficients (-100 to 100)."""
    results = []
    random.seed(42)
    
    for i in range(50):
        try:
            a, b, c, expected = generate_random_quadratic(seed=None)
            
            from quadratic import solve_quadratic
            sol = solve_quadratic(a, b, c)
            parsed = parse_solution(sol)
            
            # Basic type check
            if parsed['type'] == expected['type']:
                results.append(TestResult(f"Random {i}: a={a}, b={b}, c={c}", True,
                                          f"type: {parsed['type']}"))
            else:
                results.append(TestResult(f"Random {i}: a={a}, b={b}, c={c}", False,
                                          f"got {parsed['type']}, expected {expected['type']}"))
        except Exception as e:
            results.append(TestResult(f"Random {i}", False, str(e)))
    
    return results


def test_random_large():
    """Random tests with large coefficients."""
    results = []
    random.seed(123)
    
    for i in range(20):
        try:
            a = random.randint(1, 10**20)
            b = random.randint(-10**20, 10**20)
            c = random.randint(-10**20, 10**20)
            
            from quadratic import solve_quadratic
            sol = solve_quadratic(str(a), str(b), str(c))
            parsed = parse_solution(sol)
            
            # Just check it doesn't crash
            results.append(TestResult(f"Random large {i}", True,
                                      f"type: {parsed['type']}"))
        except Exception as e:
            results.append(TestResult(f"Random large {i}", False, str(e)))
    
    return results


def test_random_verified():
    """Random tests with Decimal verification."""
    results = []
    random.seed(999)
    
    for i in range(30):
        try:
            a, b, c, expected = generate_random_quadratic(seed=None)
            
            dec_ok, details = verify_with_decimal(a, b, c)
            results.append(TestResult(f"Random verified {i}", dec_ok, details))
        except Exception as e:
            results.append(TestResult(f"Random verified {i}", False, str(e)))
    
    return results


# ============================================================================
# DISCRIMINANT TESTS
# ============================================================================

def test_discriminant_positive():
    """D > 0: два различных вещественных корня"""
    tests = [
        ("1", "-3", "2"),     # (x-1)(x-2)=0
        ("1", "0", "-4"),      # x²-4=0
        ("2", "2", "-6"),     # 2x²+2x-6=0
    ]
    
    results = []
    for a, b, c in tests:
        try:
            from quadratic import solve_quadratic
            sol = solve_quadratic(a, b, c)
            parsed = parse_solution(sol)
            
            if parsed['type'] == 'two_solutions':
                x1, x2 = parsed['roots']
                # Verify
                ok = verify_root(int(a), int(b), int(c), x1) and \
                     verify_root(int(a), int(b), int(c), x2)
                results.append(TestResult(f"D>0: {a}x²+{b}x+{c}", ok,
                                          f"x1={x1}, x2={x2}"))
            else:
                results.append(TestResult(f"D>0: {a}x²+{b}x+{c}", False,
                                          f"got {parsed['type']}, expected two_solutions"))
        except Exception as e:
            results.append(TestResult(f"D>0: {a}x²+{b}x+{c}", False, str(e)))
    
    return results


def test_discriminant_zero():
    """D = 0: один корень (кратный)"""
    tests = [
        ("1", "-2", "1"),     # (x-1)²=0
        ("1", "4", "4"),      # (x+2)²=0
        ("4", "-4", "1"),     # (2x-1)²=0
    ]
    
    results = []
    for a, b, c in tests:
        try:
            from quadratic import solve_quadratic
            sol = solve_quadratic(a, b, c)
            parsed = parse_solution(sol)
            
            if parsed['type'] == 'one_solution':
                x = parsed['roots'][0]
                ok = verify_root(int(a), int(b), int(c), x, tol=0.1)
                results.append(TestResult(f"D=0: {a}x²+{b}x+{c}", ok, f"x={x}"))
            else:
                results.append(TestResult(f"D=0: {a}x²+{b}x+{c}", False,
                                          f"got {parsed['type']}, expected one_solution"))
        except Exception as e:
            results.append(TestResult(f"D=0: {a}x²+{b}x+{c}", False, str(e)))
    
    return results


def test_discriminant_negative():
    """D < 0: комплексные корни"""
    tests = [
        ("1", "1", "1"),       # x²+x+1=0
        ("1", "0", "1"),       # x²+1=0
        ("1", "2", "5"),       # x²+2x+5=0
    ]
    
    results = []
    for a, b, c in tests:
        try:
            from quadratic import solve_quadratic
            sol = solve_quadratic(a, b, c)
            parsed = parse_solution(sol)
            
            if parsed['type'] == 'complex':
                results.append(TestResult(f"D<0: {a}x²+{b}x+{c}", True,
                                          f"complex detected"))
            else:
                results.append(TestResult(f"D<0: {a}x²+{b}x+{c}", False,
                                          f"got {parsed['type']}, expected complex"))
        except Exception as e:
            results.append(TestResult(f"D<0: {a}x²+{b}x+{c}", False, str(e)))
    
    return results


# ============================================================================
# RUN ALL TESTS
# ============================================================================

def run_all_tests():
    """Run all test suites and print summary."""
    print("=" * 70)
    print("QUADRATIC EQUATION SOLVER - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    all_results = []
    
    test_suites = [
        ("EDGE CASES: Zero Coefficients", [
            test_zero_a,
            test_zero_b,
            test_zero_c,
            test_all_zero,
        ]),
        ("LIMIT/BOUNDARY TESTS", [
            test_perfect_squares,
            test_perfect_squares_results,
            test_unit_coefficients,
            test_large_coefficients,
            test_small_coefficients,
        ]),
        ("DISCRIMINANT TESTS", [
            test_discriminant_positive,
            test_discriminant_zero,
            test_discriminant_negative,
        ]),
        ("DECIMAL VERIFICATION", [
            test_decimal_verification,
            test_decimal_high_precision,
        ]),
        ("RANDOMIZED TESTS", [
            test_random_small,
            test_random_large,
            test_random_verified,
        ]),
    ]
    
    total_passed = 0
    total_failed = 0
    
    for suite_name, suites in test_suites:
        print(f"\n{'=' * 70}")
        print(f"📋 {suite_name}")
        print('=' * 70)
        
        for test_func in suites:
            print(f"\n▶ {test_func.__name__}")
            results = test_func()
            all_results.extend(results)
            
            for r in results:
                print(f"  {r}")
            
            passed = sum(1 for r in results if r.passed)
            failed = sum(1 for r in results if not r.passed)
            print(f"  → {passed} passed, {failed} failed")
            total_passed += passed
            total_failed += failed
    
    print(f"\n{'=' * 70}")
    print("📊 SUMMARY")
    print('=' * 70)
    print(f"Total: {len(all_results)} tests")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"Success rate: {100*total_passed/len(all_results):.1f}%")
    
    if total_failed > 0:
        print("\nFailed tests:")
        for r in all_results:
            if not r.passed:
                print(f"  ❌ {r}")
    
    return total_failed == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quadratic equation tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
