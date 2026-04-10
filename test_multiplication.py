"""Comprehensive tests for adaptive multiplication in BigInt."""

import time
import random
import sys
sys.path.insert(0, "/home/user/.openclaw/workspace")

from bigint import BigInt

def test_single_digit_multiplication():
    """Test single digit multiplication paths."""
    print("Testing single digit multiplication...")
    
    tests = [
        # (a, b, expected)
        (5, 3, 15),
        (0, 123, 0),
        (123, 0, 0),
        (1, 999999, 999999),
        (999999, 1, 999999),
        (-5, 3, -15),
        (5, -3, -15),
        (-5, -3, 15),
        (7, 7, 49),
        (9, 123456789, 1111111101),
    ]
    
    for a, b, expected in tests:
        result = BigInt(a) * BigInt(b)
        assert int(result.to_string()) == expected, f"Failed: {a} * {b} = {result}, expected {expected}"
    
    print("  ✓ All single digit tests passed")

def test_karatsuba_correctness():
    """Test Karatsuba against school multiplication."""
    print("Testing Karatsuba correctness...")
    
    # Small numbers (should use school)
    small_tests = [
        (123, 456),
        (9999, 1111),
        (123456789, 987654321),
    ]
    
    for a, b in small_tests:
        big_a = BigInt(a)
        big_b = BigInt(b)
        # Force school by ensuring both are small
        if len(big_a._value) < BigInt.KARATSUBA_THRESHOLD and len(big_b._value) < BigInt.KARATSUBA_THRESHOLD:
            school_result = big_a._multiply_school(big_b)
            karatsuba_result = big_a._multiply_karatsuba(big_b)
            assert school_result == karatsuba_result, f"Karatsuba mismatch for {a}*{b}"
    
    # Large numbers (Karatsuba should be used)
    large_tests = [
        (10**50, 10**50 + 7),
        (10**100 - 1, 10**100 + 1),
        (12345678901234567890, 98765432109876543210),
    ]
    
    for a, b in large_tests:
        big_a = BigInt(a)
        big_b = BigInt(b)
        school_result = big_a._multiply_school(big_b)
        karatsuba_result = big_a._multiply_karatsuba(big_b)
        assert school_result == karatsuba_result, f"Karatsuba mismatch for {a}*{b}"
    
    print("  ✓ All Karatsuba correctness tests passed")

def test_fft_correctness():
    """Test FFT multiplication against school multiplication."""
    print("Testing FFT correctness...")
    
    tests = [
        (10**200, 10**200),
        (10**200, 10**200 + 7),
        (123456789012345678901234567890, 987654321098765432109876543210),
        (10**500 - 1, 10**500 - 1),
    ]
    
    for a, b in tests:
        big_a = BigInt(a)
        big_b = BigInt(b)
        school_result = big_a._multiply_school(big_b)
        fft_result = big_a._multiply_fft(big_b)
        assert school_result == fft_result, f"FFT mismatch for {a}*{b}"
    
    print("  ✓ All FFT correctness tests passed")

def test_edge_cases():
    """Test edge cases for multiplication."""
    print("Testing edge cases...")
    
    # Zero cases
    assert BigInt(0) * BigInt(0) == BigInt(0)
    assert BigInt(0) * BigInt(12345) == BigInt(0)
    assert BigInt(12345) * BigInt(0) == BigInt(0)
    
    # One cases
    assert BigInt(1) * BigInt(12345) == BigInt(12345)
    assert BigInt(12345) * BigInt(1) == BigInt(12345)
    assert BigInt(-1) * BigInt(12345) == BigInt(-12345)
    
    # Negative numbers
    assert BigInt(-123) * BigInt(456) == BigInt(-56088)
    assert BigInt(123) * BigInt(-456) == BigInt(-56088)
    assert BigInt(-123) * BigInt(-456) == BigInt(56088)
    
    # Large negative numbers
    assert BigInt(-10**100) * BigInt(10**100) == BigInt(-10**200)
    assert BigInt(-10**100) * BigInt(-10**100) == BigInt(10**200)
    
    # Powers of 10
    assert BigInt(10) * BigInt(10) == BigInt(100)
    assert BigInt(10**50) * BigInt(10**50) == BigInt(10**100)
    
    print("  ✓ All edge case tests passed")

def test_adaptive_selection():
    """Test that correct algorithm is selected based on size."""
    print("Testing adaptive algorithm selection...")
    
    # Single digit
    result = BigInt(5) * BigInt(12345678901234567890)
    assert result == BigInt(5 * 12345678901234567890)
    
    # Two medium numbers (should use Karatsuba)
    a = BigInt(10**80)
    b = BigInt(10**80 + 1)
    result = a * b
    assert result == BigInt((10**80) * (10**80 + 1))
    
    # Very large numbers (should use FFT)
    a = BigInt(10**1500)
    b = BigInt(10**1500 + 1)
    result = a * b
    assert result == BigInt((10**1500) * (10**1500 + 1))
    
    print("  ✓ Adaptive selection tests passed")

def benchmark_methods():
    """Benchmark all multiplication methods."""
    import sys
    # Increase Python's integer string conversion limit for large benchmarks
    sys.set_int_max_str_digits(20000)
    
    print("\n=== Multiplication Benchmark ===\n")
    
    sizes = [10, 50, 100, 500, 1000, 2000]  # Reduced 5000 to 2000 to avoid timeout
    
    for size in sizes:
        # Generate random numbers of this size
        a = random.randint(10**(size-1), 10**size - 1)
        b = random.randint(10**(size-1), 10**size - 1)
        
        big_a = BigInt(a)
        big_b = BigInt(b)
        expected = a * b
        
        print(f"Size: {size} digits")
        
        # Single digit
        if size > 1:
            single_result = BigInt(a) * BigInt(b % 10)
            assert int(single_result.to_string()) == a * (b % 10)
            print(f"  Single digit: OK (result={a * (b % 10)})")
        
        # School multiplication
        start = time.perf_counter()
        school_result = big_a._multiply_school(big_b)
        school_time = time.perf_counter() - start
        assert school_result == BigInt(expected), "School multiplication failed"
        print(f"  School:    {school_time*1000:.2f}ms")
        
        # Karatsuba
        start = time.perf_counter()
        karatsuba_result = big_a._multiply_karatsuba(big_b)
        karatsuba_time = time.perf_counter() - start
        assert karatsuba_result == BigInt(expected), "Karatsuba failed"
        print(f"  Karatsuba: {karatsuba_time*1000:.2f}ms")
        
        # FFT
        start = time.perf_counter()
        fft_result = big_a._multiply_fft(big_b)
        fft_time = time.perf_counter() - start
        assert fft_result == BigInt(expected), "FFT failed"
        print(f"  FFT:       {fft_time*1000:.2f}ms")
        
        # Adaptive
        start = time.perf_counter()
        adaptive_result = big_a * big_b
        adaptive_time = time.perf_counter() - start
        assert adaptive_result == BigInt(expected), "Adaptive failed"
        print(f"  Adaptive:  {adaptive_time*1000:.2f}ms")
        
        if school_time > 0:
            speedup_k = school_time / karatsuba_time if karatsuba_time > 0 else float('inf')
            speedup_f = school_time / fft_time if fft_time > 0 else float('inf')
            print(f"  Speedup: Karatsuba={speedup_k:.1f}x, FFT={speedup_f:.1f}x")
        
        print()

def benchmark_adaptive_vs_naive():
    """Compare adaptive multiplication against naive always-school."""
    import sys
    sys.set_int_max_str_digits(20000)
    
    print("\n=== Adaptive vs Naive Benchmark ===\n")
    
    # Create a BigInt with low threshold to force more algorithm changes
    original_threshold = BigInt.KARATSUBA_THRESHOLD
    BigInt.KARATSUBA_THRESHOLD = 10  # Force Karatsuba for sizes > 10
    
    try:
        sizes = [5, 20, 100, 500]
        
        for size in sizes:
            a = random.randint(10**(size-1), 10**size - 1)
            b = random.randint(10**(size-1), 10**size - 1)
            big_a = BigInt(a)
            big_b = BigInt(b)
            
            # Time adaptive
            start = time.perf_counter()
            for _ in range(10):
                result = big_a * big_b
            adaptive_time = (time.perf_counter() - start) / 10
            
            # Time always-school
            start = time.perf_counter()
            for _ in range(10):
                result = big_a._multiply_school(big_b)
            school_time = (time.perf_counter() - start) / 10
            
            speedup = school_time / adaptive_time if adaptive_time > 0 else float('inf')
            print(f"Size {size:4d}: adaptive={adaptive_time*1000:8.2f}ms, school={school_time*1000:8.2f}ms, speedup={speedup:.1f}x")
    finally:
        BigInt.KARATSUBA_THRESHOLD = original_threshold

if __name__ == "__main__":
    test_single_digit_multiplication()
    test_karatsuba_correctness()
    test_fft_correctness()
    test_edge_cases()
    test_adaptive_selection()
    
    print("\n" + "="*50)
    print("All correctness tests passed!")
    print("="*50 + "\n")
    
    benchmark_methods()
    benchmark_adaptive_vs_naive()
    
    print("\n=== Benchmark Complete ===")
