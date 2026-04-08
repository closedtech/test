import sys
sys.set_int_max_str_digits(100000)

from bigint import BigInt
import time
import random

# Basic tests
tests = [
    ("10", "3", "3", "1"),
    ("100", "7", "14", "2"),
    ("123456789", "3", "41152263", "0"),
]

print("=== Basic Tests ===")
all_pass = True
for a, b, eq, er in tests:
    q, r = BigInt(a)._divide_newton(a, b)
    if q._value == eq and r._value == er:
        print(f"OK {a}/{b} = {q}, r={r}")
    else:
        print(f"FAIL {a}/{b} = {q}, r={r} (expected {eq}, {er})")
        all_pass = False

if not all_pass:
    print("Some tests failed!")
    sys.exit(1)

# Benchmark
print("\n=== Benchmark ===")
def rand(n):
    return ''.join([str(random.randint(1,9)) for _ in range(n)])

for digits in [100, 500, 1000]:
    a = rand(digits)
    b = rand(digits // 2)
    
    t0 = time.perf_counter()
    q, r = BigInt(a)._divide_newton(a, b)
    t_newton = time.perf_counter() - t0
    
    t0 = time.perf_counter()
    q2, r2 = BigInt(a)._divide_school(a, b)
    t_school = time.perf_counter() - t0
    
    ratio = t_school/t_newton if t_newton > 0 else float('inf')
    correct = q._value == q2._value and r._value == r2._value
    print(f"{digits}d: Newton={t_newton:.3f}s, School={t_school:.3f}s, ratio={ratio:.1f}x, correct={correct}")

print("\nAll tests passed!")
