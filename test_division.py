"""Test division algorithms in BigInt."""
import time
import random
import sys
sys.path.insert(0, '/home/user/.openclaw/workspace')
from bigint import BigInt


def test_correctness():
    print("=== Correctness tests ===")
    cases = [
        ("100", "7"),
        ("1000", "3"),
        ("123456789", "12345"),
        ("999999999", "999991"),
        ("123456789012345678901234567890", "98765432109876543210987654321"),
        ("1" + "0" * 100, "1" + "0" * 50),
        ("9" * 50, "9" * 25),
        ("999" * 20, "123"),
        ("1" * 200, "3"),
    ]
    for a, b in cases:
        bi_a = BigInt(a)
        bi_b = BigInt(b)
        q, r = bi_a._divmod(bi_b)
        eq = int(a) // int(b)
        er = int(a) % int(b)
        qok = q._value == str(eq)
        rok = r._value == str(er)
        status = "✓" if (qok and rok) else "✗"
        print(f"  {status} {len(a)}d/{len(b)}d q={q._value[:25]}... r={r._value[:25]}...")
        if not (qok and rok):
            print(f"     Expected q={eq} r={er}")
    print()


def test_random(nd_a, nd_b, count=5):
    print(f"=== Random {nd_a}d/{nd_b}d ({count} cases) ===")
    for _ in range(count):
        na = random.randint(max(1, nd_a - 3), nd_a + 3)
        nb = random.randint(max(1, nd_b - 3), min(nd_b + 3, na))
        a = str(random.randint(10 ** (na - 1), 10 ** na - 1)) if na > 1 else str(random.randint(1, 9))
        b = str(random.randint(max(1, 10 ** (nb - 1)), min(10 ** nb - 1, int(a))))
        bi_a = BigInt(a)
        bi_b = BigInt(b)
        q, r = bi_a._divmod(bi_b)
        eq = int(a) // int(b)
        er = int(a) % int(b)
        if q._value == str(eq) and r._value == str(er):
            print(f"  ✓ {na}d/{nb}d")
        else:
            print(f"  ✗ FAIL {na}d/{nb}d: got q={q._value} r={r._value}, expected {eq} {er}")
    print()


def test_performance():
    print("=== Performance (vs Python int) ===")

    test_sets = [
        (1000, 500, 1),
        (5000, 2500, 1),
        (15000, 7500, 1),
    ]

    for nd_a, nd_b, iters in test_sets:
        print(f"\n--- {nd_a} digits / {nd_b} digits ---")

        a = "9" + "".join(random.choices("0123456789", k=nd_a - 1))
        b = "1" + "".join(random.choices("0123456789", k=nd_b - 1))
        a = str(int(a))
        b = str(int(b))

        a_int = int(a)
        b_int = int(b)
        expected_q = a_int // b_int
        expected_r = a_int % b_int

        # Python int baseline
        t0 = time.perf_counter()
        for _ in range(iters):
            py_q = a_int // b_int
            py_r = a_int % b_int
        t_python = time.perf_counter() - t0
        print(f"  Python int: {t_python:.4f}s")

        # Our BigInt -- normal (auto-select)
        bi_a = BigInt(a)
        bi_b = BigInt(b)
        t0 = time.perf_counter()
        for _ in range(iters):
            q, r = bi_a._divmod(bi_b)
        t_auto = time.perf_counter() - t0
        q_ok = q._value == str(expected_q)
        r_ok = r._value == str(expected_r)
        status = "✓" if (q_ok and r_ok) else "✗"
        print(f"  BigInt auto: {t_auto:.4f}s  {status}")

        # Force school
        saved_school = BigInt.DIV_SCHOOL_THRESHOLD
        saved_burnikel = BigInt.DIV_BURNIKEL_THRESHOLD
        BigInt.DIV_SCHOOL_THRESHOLD = 999999
        BigInt.DIV_BURNIKEL_THRESHOLD = 999999
        t0 = time.perf_counter()
        for _ in range(iters):
            q, r = bi_a._divmod(bi_b)
        t_school = time.perf_counter() - t0
        q_ok = q._value == str(expected_q)
        r_ok = r._value == str(expected_r)
        status = "✓" if (q_ok and r_ok) else "✗"
        print(f"  BigInt school: {t_school:.4f}s  {status}")
        BigInt.DIV_SCHOOL_THRESHOLD = saved_school
        BigInt.DIV_BURNIKEL_THRESHOLD = saved_burnikel

        # Force burnikel (only valid for 1000-10000)
        if 1000 <= nd_a <= 10000:
            saved = BigInt.DIV_BURNIKEL_THRESHOLD
            BigInt.DIV_SCHOOL_THRESHOLD = 1
            BigInt.DIV_BURNIKEL_THRESHOLD = 999999
            t0 = time.perf_counter()
            try:
                for _ in range(iters):
                    q, r = bi_a._divmod(bi_b)
                t_burnikel = time.perf_counter() - t0
                q_ok = q._value == str(expected_q)
                r_ok = r._value == str(expected_r)
                status = "✓" if (q_ok and r_ok) else "✗"
                print(f"  BigInt burnikel: {t_burnikel:.4f}s  {status}")
            except Exception as e:
                print(f"  BigInt burnikel: FAILED ({e})")
            BigInt.DIV_SCHOOL_THRESHOLD = saved_school
            BigInt.DIV_BURNIKEL_THRESHOLD = saved

        # Force barrett
        saved = BigInt.DIV_BURNIKEL_THRESHOLD
        BigInt.DIV_SCHOOL_THRESHOLD = 1
        BigInt.DIV_BURNIKEL_THRESHOLD = 1
        t0 = time.perf_counter()
        try:
            for _ in range(iters):
                q, r = bi_a._divmod(bi_b)
            t_barrett = time.perf_counter() - t0
            q_ok = q._value == str(expected_q)
            r_ok = r._value == str(expected_r)
            status = "✓" if (q_ok and r_ok) else "✗"
            print(f"  BigInt barrett: {t_barrett:.4f}s  {status}")
        except Exception as e:
            print(f"  BigInt barrett: FAILED ({e})")
        BigInt.DIV_SCHOOL_THRESHOLD = saved_school
        BigInt.DIV_BURNIKEL_THRESHOLD = saved_burnikel


if __name__ == "__main__":
    test_correctness()
    test_random(50, 20, 5)
    test_random(500, 250, 3)
    test_random(900, 450, 2)
    test_performance()
