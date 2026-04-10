#!/usr/bin/env python3
"""Benchmark division methods in BigInt."""

import sys
import time
import random

sys.path.insert(0, '/home/user/.openclaw/workspace')
from bigint import BigInt

def rand(n):
    first = str(random.randint(1, 9))
    return first + ''.join(str(random.randint(0, 9)) for _ in range(n - 1))

def bench(name, a, b):
    bi_a = BigInt(a)
    bi_b = BigInt(b)

    t0 = time.perf_counter()
    q, r = bi_a._divide_school(a, b)
    t_school = time.perf_counter() - t0

    t0 = time.perf_counter()
    q2, r2 = bi_a._divide_burnikel(a, b)
    t_burn = time.perf_counter() - t0

    t0 = time.perf_counter()
    q3, r3 = bi_a._divide_barrett(a, b)
    t_bar = time.perf_counter() - t0

    # verify all match
    assert q._value == q2._value == q3._value, f"Mismatch: {q._value} vs {q2._value} vs {q3._value}"
    assert r._value == r2._value == r3._value, f"Rem r mismatch"

    print(f"{name}: school={t_school*1000:8.2f}ms  burnikel={t_burn*1000:8.2f}ms  barrett={t_bar*1000:8.2f}ms")

    return t_school, t_burn, t_bar

print("=== BigInt Division Benchmarks ===\n")

print("1000-digit / 500-digit:")
a, b = rand(1000), rand(500)
bench("1000/500", a, b)

print("\n5000-digit / 2000-digit:")
a, b = rand(5000), rand(2000)
bench("5000/2000", a, b)

# Multiple runs
print("\n--- 1000/500 avg (5 runs) ---")
ts = []; tb = []; tba = []
for _ in range(5):
    a, b = rand(1000), rand(500)
    bi_a = BigInt(a); bi_b = BigInt(b)

    t0 = time.perf_counter()
    q, r = bi_a._divide_school(a, b)
    ts.append(time.perf_counter() - t0)

    t0 = time.perf_counter()
    q2, r2 = bi_a._divide_burnikel(a, b)
    tb.append(time.perf_counter() - t0)

    t0 = time.perf_counter()
    q3, r3 = bi_a._divide_barrett(a, b)
    tba.append(time.perf_counter() - t0)

print(f"school avg={sum(ts)/5*1000:.2f}ms  burnikel avg={sum(tb)/5*1000:.2f}ms  barrett avg={sum(tba)/5*1000:.2f}ms")