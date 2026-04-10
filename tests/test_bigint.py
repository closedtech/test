#!/usr/bin/env python3
"""Test BigInt division correctness and benchmark."""

import sys
import time
import random
sys.path.insert(0, '/home/user/.openclaw/workspace')

from bigint import BigInt

def test_divmod(name, a, b):
    """Test a // b and a % b."""
    bi_a = BigInt(a)
    bi_b = BigInt(b)
    q, r = bi_a._divmod(bi_b)
    py_q = a // b
    py_r = a % b
    q_ok = int(q._value) == py_q
    r_ok = int(r._value) == py_r
    ok = q_ok and r_ok
    if not ok:
        print(f"FAIL {name}: {a} // {b}")
        print(f"  BigInt: q={q._value}, r={r._value}")
        print(f"  Python: q={py_q}, r={py_r}")
    return ok

def run_random_tests(n=200):
    """Random correctness tests."""
    failures = []
    print(f"Running {n} random tests...")
    for i in range(n):
        # Generate random integers of various sizes
        if i < 50:
            # Small numbers
            a = random.randint(0, 10**6)
            b = random.randint(1, 10**6)
        elif i < 100:
            # Medium numbers
            a = random.randint(0, 10**50)
            b = random.randint(1, 10**50)
        elif i < 160:
            # Large numbers (to exercise Newton/School)
            a = random.randint(0, 10**200)
            b = random.randint(1, 10**100)
        else:
            # Very large numbers
            a = random.randint(0, 10**500)
            b = random.randint(1, 10**250)
        
        # Also test negative numbers
        signs = [1, -1] if i % 3 == 0 else [1]
        for sign in signs:
            a_signed = a * sign
            if not test_divmod(f"random-{i}-sign={sign}", a_signed, b):
                failures.append((a_signed, b))
    
    print(f"  Passed: {n - len(failures)}/{n}")
    return failures

def test_edge_cases():
    """Test edge cases: 0, 1, powers of BASE, etc."""
    print("Testing edge cases...")
    failures = []
    
    cases = [
        (0, 1), (0, 123), (0, 999),
        (1, 1), (1, 2), (1, 999),
        (5, 5), (5, 3),
        (1000, 10), (1000, 100), (1000, 1000),
        (10**6, 10**3), (10**6, 10**6),
        (-1, 1), (1, -1), (-100, 3), (-100, -5),
        (-10**6, 10**3), (10**6, -10**3),
        (10**6 + 1, 10**6),
        (10**6 - 1, 10**6),
        (5, 100), (1, 999999),
    ]
    
    for a, b in cases:
        if not test_divmod(f"edge-{a}-{b}", a, b):
            failures.append((a, b))
    
    print(f"  Edge cases passed: {len(cases) - len(failures)}/{len(cases)}")
    return failures

def test_boundary_sizes():
    """Test at division algorithm threshold boundaries."""
    print("Testing boundary sizes...")
    failures = []
    
    for n_digits in [499, 500, 501, 600, 1000]:
        a = 10**n_digits + random.randint(0, 10**n_digits)
        b = random.randint(10**(n_digits//2), 10**(n_digits//2 + 5))
        if not test_divmod(f"boundary-{n_digits}d", a, b):
            failures.append((a, b))
    
    return failures

def benchmark():
    """Benchmark division performance."""
    print("\nBenchmarking division performance...")
    
    sizes = [
        (100, "100-digit / 50-digit"),
        (500, "500-digit / 250-digit"),
        (1000, "1000-digit / 500-digit"),
        (2000, "2000-digit / 1000-digit"),
    ]
    
    for n, desc in sizes:
        a = BigInt(10**n + 12345)
        b = BigInt(10**(n//2) + 789)
        
        start = time.time()
        for _ in range(3):
            q, r = a._divmod(b)
        elapsed = (time.time() - start) / 3
        
        print(f"  {desc}: {elapsed:.4f}s avg")
        
def main():
    print("=" * 60)
    print("BigInt Division Review")
    print("=" * 60)
    
    all_failures = []
    
    all_failures.extend(run_random_tests(200))
    all_failures.extend(test_edge_cases())
    all_failures.extend(test_boundary_sizes())
    
    print("\n" + "=" * 60)
    if all_failures:
        print(f"FAILURES: {len(all_failures)} tests failed")
        for a, b in all_failures[:10]:
            print(f"  {a} // {b}")
    else:
        print("ALL TESTS PASSED")
    
    benchmark()
    
    return len(all_failures)

if __name__ == "__main__":
    sys.exit(main())