import sys
sys.set_int_max_str_digits(100000)

# Test Newton with Python native ints
def test_newton_native():
    a = 123456789
    b = 3
    
    print("=== Native int Newton test ===")
    for k in [5, 10, 15, 20]:
        R = 10 ** k
        y = R // b + 1  # initial approximation
        
        # Newton iterations
        for _ in range(5):
            y_new = y * (2 * R - b * y) // R
            if y_new == y:
                break
            y = y_new
        
        q = a * y // R
        print(f"k={k}, R=10^{k}, y={y}, y/R={y/R}, q={q}, correct={a//b}, diff={q - a//b}")

test_newton_native()

# Now test BigInt
print("\n=== BigInt Newton test ===")
from bigint import BigInt

for a, b in [("10", "3"), ("100", "7"), ("123456789", "3")]:
    try:
        q, r = BigInt(a)._divide_newton(a, b)
        expected_q = str(int(a) // int(b))
        expected_r = str(int(a) % int(b))
        status = "✅" if q._value == expected_q and r._value == expected_r else "❌"
        print(f'{status} {a}/{b} = {q._value}, r={r._value} (expected {expected_q}, {expected_r})')
    except Exception as e:
        print(f"❌ {a}/{b}: ERROR: {e}")
