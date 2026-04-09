"""Bubble Sort implementation with optimizations."""


def bubble_sort(arr: list) -> list:
    """Basic bubble sort O(n²).
    
    Repeatedly swaps adjacent elements if they're in wrong order.
    """
    arr = arr.copy()
    n = len(arr)
    
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        
        if not swapped:
            break
    
    return arr


def bubble_sort_optimized(arr: list) -> list:
    """Optimized bubble sort O(n) best case.
    
    Optimizations:
    1. Early termination if no swaps (list is sorted)
    2. Reduced pass range (largest elements already in place)
    """
    arr = arr.copy()
    n = len(arr)
    right = n - 1  # Right boundary of unsorted portion
    
    while right > 0:
        new_right = 0
        for j in range(right):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                new_right = j
        
        if new_right == 0:
            break  # No swaps means sorted
        
        right = new_right
    
    return arr


def bubble_sort_with_steps(arr: list) -> tuple[list, list]:
    """Bubble sort that returns each step for visualization.
    
    Returns:
        tuple: (sorted_array, list of all intermediate states)
    """
    arr = arr.copy()
    n = len(arr)
    steps = [arr.copy()]
    
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
                steps.append(arr.copy())
        
        if not swapped:
            break
    
    return arr, steps


if __name__ == "__main__":
    # Demo
    arr = [64, 34, 25, 12, 22, 11, 90]
    print(f"Original: {arr}")
    print(f"Sorted:   {bubble_sort_optimized(arr)}")
