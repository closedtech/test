"""Quick division test."""
import sys
import time
sys.path.insert(0, '/home/user/.openclaw/workspace')
from bigint import BigInt

# Test correctness first
tests = [
    ("100", "7"),
    ("1000", "3"),
    ("123456789", "12345"),
    ("999999999", "999991"),
    ("1" + "0" * 100, "1" + "0" * 50),
    ("9" * 50, "9" * 25),
    ("999" * 20, "123"),
]

print("Correctness tests:")
for a, b in tests:
    bi_a = BigInt(a)
    bi_b = BigInt(b)
    q, r = bi_a._divmod(bi_b)
    eq = int(a) // int(b)
    er = int(a) % int(b)
    ok = q._value == str(eq) and r._value == str(er)
    print(f"  {'✓' if ok else '✗'} {a[:20]}... / {b} = q:{q._value[:20]}... r:{r._value}")

print("\nMedium correctness (1000-5000d):")
for nd in [100, 500, 900]:
    a = "9" * nd
    b = "1" + "9" * (nd // 2)
    a_int = int(a)
    b_int = int(b)
    eq = a_int // b_int
    er = a_int % b_int
    bi_a = BigInt(a)
    bi_b = BigInt(b)
    try:
        q, r = bi_a._divmod(bi_b)
        ok = q._value == str(eq) and r._value == str(er)
        print(f"  {'✓' if ok else '✗'} {nd}d: q={q._value[:20]}... r={r._value[:20]}...")
    except Exception as e:
        print(f"  ✗ {nd}d: {e}")

print("\nPerformance (1000d):")
a = "9" * 1000
b = "1" + "9" * 500
a_int = int(a)
b_int = int(b)

bi_a = BigInt(a)
bi_b = BigInt(b)

# Force school
BigInt.DIV_SCHOOL_THRESHOLD = 99999
BigInt.DIV_BURNIKEL_THRESHOLD = 99999
t0 = time.perf_counter()
q, r = bi_a._divmod(bi_b)
t_school = time.perf_counter() - t0
print(f"  school: {t_school:.3f}s")

# Force burnikel
BigInt.DIV_SCHOOL_THRESHOLD = 1
BigInt.DIV_BURNIKEL_THRESHOLD = 99999
t0 = time.perf_counter()
try:
    q, r = bi_a._divmod(bi_b)
    t_burnikel = time.perf_counter() - t0
    print(f"  burnikel: {t_burnikel:.3f}s")
except Exception as e:
    print(f"  burnikel: FAILED ({e})")

# Force barrett
BigInt.DIV_SCHOOL_THRESHOLD = 1
BigInt.DIV_BURNIKEL_THRESHOLD = 1
t0 = time.perf_counter()
try:
    q, r = bi_a._divmod(bi_b)
    t_barrett = time.perf_counter() - t0
    print(f"  barrett: {t_barrett:.3f}s")
except Exception as e:
    print(f"  barrett: FAILED ({e})")

# Auto
BigInt.DIV_SCHOOL_THRESHOLD = 1000
BigInt.DIV_BURNIKEL_THRESHOLD = 10000
t0 = time.perf_counter()
q, r = bi_a._divmod(bi_b)
t_auto = time.perf_counter() - t0
print(f"  auto (school): {t_auto:.3f}s")

print("\nPerformance (5000d):")
a = "9" * 5000
b = "1" + "9" * 2500
a_int = int(a)
b_int = int(b)

bi_a = BigInt(a)
bi_b = BigInt(b)

BigInt.DIV_SCHOOL_THRESHOLD = 99999
BigInt.DIV_BURNIKEL_THRESHOLD = 99999
t0 = time.perf_counter()
q, r = bi_a._divmod(bi_b)
t_school = time.perf_counter() - t0
print(f"  school: {t_school:.3f}s (skip)" if t_school > 5 else f"  school: {t_school:.3f}s")

# Force burnikel
BigInt.DIV_SCHOOL_THRESHOLD = 1
BigInt.DIV_BURNIKEL_THRESHOLD = 99999
t0 = time.perf_counter()
try:
    q, r = bi_a._divmod(bi_b)
    t_burnikel = time.perf_counter() - t0
    print(f"  burnikel: {t_burnikel:.3f}s")
except Exception as e:
    print(f"  burnikel: FAILED ({e})")

# Force barrett
BigInt.DIV_SCHOOL_THRESHOLD = 1
BigInt.DIV_BURNIKEL_THRESHOLD = 1
t0 = time.perf_counter()
try:
    q, r = bi_a._divmod(bi_b)
    t_barrett = time.perf_counter() - t0
    print(f"  barrett: {t_barrett:.3f}s")
except Exception as e:
    print(f"  barrett: FAILED ({e})")

# Auto
BigInt.DIV_SCHOOL_THRESHOLD = 1000
BigInt.DIV_BURNIKEL_THRESHOLD = 10000
t0 = time.perf_counter()
q, r = bi_a._divmod(bi_b)
t_auto = time.perf_counter() - t0
print(f"  auto (burnikel): {t_auto:.3f}s")
