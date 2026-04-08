"""Minimal test for division."""
import sys
sys.path.insert(0, '/home/user/.openclaw/workspace')
from bigint import BigInt

# Test small correctness
tests = [
    ("100", "7"),
    ("1000", "3"),
    ("123456789", "12345"),
]

print("Correctness:")
for a, b in tests:
    bi_a = BigInt(a)
    bi_b = BigInt(b)
    q, r = bi_a._divmod(bi_b)
    eq = int(a) // int(b)
    er = int(a) % int(b)
    ok = q._value == str(eq) and r._value == str(er)
    print(f"  {'ok' if ok else 'FAIL'} {a}/{b} q={q._value} r={r._value}")

# 500 digit test
print("\n500 digits:")
a = "9" * 500
b = "1" + "9" * 250
a_int = int(a)
b_int = int(b)

bi_a = BigInt(a)
bi_b = BigInt(b)

BigInt.DIV_SCHOOL_THRESHOLD = 99999
BigInt.DIV_BURNIKEL_THRESHOLD = 99999
q, r = bi_a._divmod(bi_b)
ok = q._value == str(a_int // b_int) and r._value == str(a_int % b_int)
print(f"  school: {'ok' if ok else 'FAIL'}")

BigInt.DIV_SCHOOL_THRESHOLD = 1
BigInt.DIV_BURNIKEL_THRESHOLD = 99999
import time
t0 = time.perf_counter()
try:
    q, r = bi_a._divmod(bi_b)
    t = time.perf_counter() - t0
    ok = q._value == str(a_int // b_int) and r._value == str(a_int % b_int)
    print(f"  burnikel: {'ok' if ok else 'FAIL'} ({t:.3f}s)")
except Exception as e:
    print(f"  burnikel: FAIL ({e})")

BigInt.DIV_SCHOOL_THRESHOLD = 1
BigInt.DIV_BURNIKEL_THRESHOLD = 1
t0 = time.perf_counter()
try:
    q, r = bi_a._divmod(bi_b)
    t = time.perf_counter() - t0
    ok = q._value == str(a_int // b_int) and r._value == str(a_int % b_int)
    print(f"  barrett: {'ok' if ok else 'FAIL'} ({t:.3f}s)")
except Exception as e:
    print(f"  barrett: FAIL ({e})")

# 1000 digit test
print("\n1000 digits:")
a = "9" * 1000
b = "1" + "9" * 500
a_int = int(a)
b_int = int(b)

bi_a = BigInt(a)
bi_b = BigInt(b)

BigInt.DIV_SCHOOL_THRESHOLD = 99999
BigInt.DIV_BURNIKEL_THRESHOLD = 99999
import time
t0 = time.perf_counter()
q, r = bi_a._divmod(bi_b)
t = time.perf_counter() - t0
ok = q._value == str(a_int // b_int) and r._value == str(a_int % b_int)
print(f"  school: {'ok' if ok else 'FAIL'} ({t:.3f}s)")

BigInt.DIV_SCHOOL_THRESHOLD = 1
BigInt.DIV_BURNIKEL_THRESHOLD = 99999
t0 = time.perf_counter()
try:
    q, r = bi_a._divmod(bi_b)
    t = time.perf_counter() - t0
    ok = q._value == str(a_int // b_int) and r._value == str(a_int % b_int)
    print(f"  burnikel: {'ok' if ok else 'FAIL'} ({t:.3f}s)")
except Exception as e:
    print(f"  burnikel: FAIL ({e})")

BigInt.DIV_SCHOOL_THRESHOLD = 1
BigInt.DIV_BURNIKEL_THRESHOLD = 1
t0 = time.perf_counter()
try:
    q, r = bi_a._divmod(bi_b)
    t = time.perf_counter() - t0
    ok = q._value == str(a_int // b_int) and r._value == str(a_int % b_int)
    print(f"  barrett: {'ok' if ok else 'FAIL'} ({t:.3f}s)")
except Exception as e:
    print(f"  barrett: FAIL ({e})")
