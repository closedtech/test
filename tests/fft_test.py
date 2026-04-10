"""Speed test for BigInt multiplication: school vs FFT."""
import time
import random
import sys
import math

sys.path.insert(0, '/home/user/.openclaw/workspace')

import bigint

def time_mul(name, a, b, iterations=3):
    """Time multiplication."""
    ba = bigint.BigInt(a)
    bb = bigint.BigInt(b)

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = ba * bb
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    avg = sum(times) / len(times)
    min_t = min(times)
    print(f"{name}: {avg*1000:.2f} ms avg, {min_t*1000:.2f} ms min ({iterations} runs)")
    return avg

def verify():
    """Verify FFT correctness."""
    print("=== Correctness verification ===")

    test_cases = [
        ("1" * 10, "1" * 10),
        ("123456", "789012"),
        ("1" * 100, "2" * 100),
        ("1" * 200, "1" * 200),
    ]

    all_pass = True
    for a, b in test_cases:
        ba = bigint.BigInt(a)
        bb = bigint.BigInt(b)

        school = ba._multiply_school(bb)
        fft = ba._multiply_fft(bb)

        if school.to_string() != fft.to_string():
            print(f"FAIL: {a[:20]}... x {b[:20]}...")
            all_pass = False
        else:
            print(f"OK: {len(a)} digits")

    # Random tests
    for size in [100, 200, 500]:
        for trial in range(3):
            a = "".join(str(random.randint(1, 9)) for _ in range(size))
            b = "".join(str(random.randint(1, 9)) for _ in range(size))
            ba = bigint.BigInt(a)
            bb = bigint.BigInt(b)
            school = ba._multiply_school(bb)
            fft = ba._multiply_fft(bb)
            if school.to_string() != fft.to_string():
                print(f"FAIL at {size} digits, trial {trial}")
                all_pass = False
            else:
                print(f"OK: {size} digits, trial {trial}")

    if all_pass:
        print("\nAll correctness tests PASSED!")
    return all_pass


if __name__ == "__main__":
    print("=" * 60)
    print("BigInt Multiplication Speed Test")
    print("=" * 60)

    verify()

    print("\n" + "=" * 60)
    print("SPEED BENCHMARKS")
    print("=" * 60)

    # Small (< threshold)
    print("\n--- Small numbers (~30 digits) ---")
    time_mul("School", "123456789012345678901234567890", "987654321098765432109876543210", iterations=100)

    # Threshold
    print("\n--- Threshold (100 digits) ---")
    time_mul("FFT", "1" + "0" * 99, "2" + "0" * 99, iterations=20)

    # 1000 digits
    print("\n--- 1000 digits ---")
    time_mul("FFT", "1" + "0" * 999, "2" + "0" * 999, iterations=5)
    time_mul("School", "1" + "0" * 999, "2" + "0" * 999, iterations=3)

    # 5000 digits
    print("\n--- 5000 digits ---")
    time_mul("FFT", "1" + "0" * 4999, "2" + "0" * 4999, iterations=3)

    # Random 1000
    print("\n--- Random 1000-digit ---")
    a = "".join(str(random.randint(1, 9)) for _ in range(1000))
    b = "".join(str(random.randint(1, 9)) for _ in range(1000))
    time_mul("FFT", a, b, iterations=3)
    time_mul("School", a, b, iterations=3)

    print("\n" + "=" * 60)
    print("FFT complexity: O(n log n) vs School O(n²)")
    print("=" * 60)
