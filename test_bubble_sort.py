"""Tests for bubble sort implementations."""

import time
import random
from bubble_sort import bubble_sort, bubble_sort_optimized, bubble_sort_with_steps


def test_empty():
    assert bubble_sort([]) == []
    assert bubble_sort_optimized([]) == []
    print("✅ Empty array")


def test_single():
    assert bubble_sort([1]) == [1]
    assert bubble_sort_optimized([1]) == [1]
    print("✅ Single element")


def test_already_sorted():
    arr = [1, 2, 3, 4, 5]
    assert bubble_sort(arr) == [1, 2, 3, 4, 5]
    assert bubble_sort_optimized(arr) == [1, 2, 3, 4, 5]
    print("✅ Already sorted")


def test_reverse_sorted():
    arr = [5, 4, 3, 2, 1]
    assert bubble_sort(arr) == [1, 2, 3, 4, 5]
    assert bubble_sort_optimized(arr) == [1, 2, 3, 4, 5]
    print("✅ Reverse sorted")


def test_with_duplicates():
    arr = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    assert bubble_sort(arr) == [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9]
    assert bubble_sort_optimized(arr) == [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9]
    print("✅ With duplicates")


def test_negative_numbers():
    arr = [-5, 3, -2, 8, -1, 0]
    assert bubble_sort(arr) == [-5, -2, -1, 0, 3, 8]
    assert bubble_sort_optimized(arr) == [-5, -2, -1, 0, 3, 8]
    print("✅ Negative numbers")


def test_steps():
    arr = [5, 3, 8, 1]
    sorted_arr, steps = bubble_sort_with_steps(arr)
    assert sorted_arr == [1, 3, 5, 8]
    assert len(steps) > 1
    print(f"✅ Steps visualization ({len(steps)} states)")


def test_performance():
    arr = list(range(1000))
    random.shuffle(arr)
    
    t0 = time.time()
    bubble_sort(arr.copy())
    t_basic = time.time() - t0
    
    t0 = time.time()
    bubble_sort_optimized(arr.copy())
    t_opt = time.time() - t0
    
    print(f"✅ Performance: basic={t_basic:.4f}s, optimized={t_opt:.4f}s")
    print(f"   Speedup: {t_basic/t_opt:.2f}x")


if __name__ == "__main__":
    test_empty()
    test_single()
    test_already_sorted()
    test_reverse_sorted()
    test_with_duplicates()
    test_negative_numbers()
    test_steps()
    test_performance()
    print("\n🎉 All tests passed!")
