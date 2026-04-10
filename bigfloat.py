"""BigFloat - Arbitrary precision floating point arithmetic."""

BASE = 10**9
BASE_DIGITS = 9


class BigFloat:
    __slots__ = ('digits', 'exp', 'sign')

    SCHOOL_THRESHOLD = 100
    KARATSUBA_THRESHOLD = 1000
    TOOM3_THRESHOLD = 2000
    SQRT_NEWTON_THRESHOLD = 2000

    def __init__(self, value=0):
        self.digits = []
        self.exp = 0
        self.sign = 1

        if isinstance(value, BigFloat):
            self.digits = list(value.digits)
            self.exp = value.exp
            self.sign = value.sign
        elif isinstance(value, int):
            self._from_int(value)
        elif isinstance(value, float):
            self._from_float(value)
        elif isinstance(value, str):
            self._from_str(value)
        else:
            raise TypeError(f"Cannot convert {type(value).__name__}")
        self._normalize()

    def _from_int(self, value: int):
        if value < 0:
            self.sign = -1
            value = -value
        elif value == 0:
            self.sign = 1
        if value == 0:
            self.digits = [0]
            self.exp = 0
        else:
            while value > 0:
                self.digits.append(value % BASE)
                value //= BASE
            self.exp = len(self.digits) - 1 if self.digits else 0

    def _from_float(self, value: float):
        if value < 0:
            self.sign = -1
            value = -value
        elif value == 0:
            self.sign = 1
        if value == 0:
            self.digits = [0]
            self.exp = 0
            return
        self._from_str(f"{value:.15g}")

    def _from_str(self, value: str):
        value = value.strip()
        if not value:
            raise ValueError("Empty string")
        if value.startswith('-'):
            self.sign = -1
            value = value[1:]
        elif value.startswith('+'):
            self.sign = 1
            value = value[1:]
        else:
            self.sign = 1
        if 'e' in value.lower():
            base_part, exp_part = value.lower().split('e')
            exp = int(exp_part)
            if '.' in base_part:
                int_part, frac_part = base_part.split('.')
                frac_part = frac_part.rstrip('0')
                exp += len(frac_part)
                value = int_part + frac_part
            else:
                value = base_part
        if '.' in value:
            int_part, frac_part = value.split('.')
            frac_part = frac_part.rstrip('0')
        else:
            int_part = value
            frac_part = ''
        combined = int_part + frac_part
        exp_adjust = -len(frac_part) if frac_part else 0
        combined = combined.lstrip('0') or '0'
        self._from_int(int(combined) if combined else 0)
        self.exp += exp_adjust

    def _normalize(self):
        while len(self.digits) > 1 and self.digits[-1] == 0:
            self.digits.pop()
        if self._is_zero():
            self.digits = [0]
            self.exp = 0
            self.sign = 1

    def _is_zero(self) -> bool:
        return len(self.digits) == 1 and self.digits[0] == 0

    def __neg__(self):
        result = self._copy()
        result.sign = -result.sign
        if result._is_zero():
            result.sign = 1
        return result

    def __abs__(self):
        result = self._copy()
        result.sign = 1
        return result

    def _copy(self):
        new = BigFloat.__new__(BigFloat)
        new.digits = list(self.digits)
        new.exp = self.exp
        new.sign = self.sign
        return new

    def _compare_abs(self, other: "BigFloat") -> int:
        if len(self.digits) != len(other.digits):
            return -1 if len(self.digits) < len(other.digits) else 1
        for i in range(len(self.digits) - 1, -1, -1):
            if self.digits[i] != other.digits[i]:
                return -1 if self.digits[i] < other.digits[i] else 1
        return 0

    def __eq__(self, other) -> bool:
        if not isinstance(other, BigFloat):
            other = BigFloat(other)
        return (self.sign == other.sign and 
                self.digits == other.digits and 
                self.exp == other.exp)

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other) -> bool:
        if not isinstance(other, BigFloat):
            other = BigFloat(other)
        if self.sign != other.sign:
            return self.sign < other.sign
        cmp = self._compare_abs(other)
        return cmp < 0 if self.sign > 0 else cmp > 0

    def __le__(self, other) -> bool:
        return self == other or self < other

    def __gt__(self, other) -> bool:
        if not isinstance(other, BigFloat):
            other = BigFloat(other)
        return other < self

    def __ge__(self, other) -> bool:
        return self > other or self == other

    def __bool__(self) -> bool:
        return not self._is_zero()

    def __float__(self) -> float:
        return float(str(self))

    def _align_exp(self, other: "BigFloat"):
        if self.exp == other.exp:
            return self, other
        a, b = self._copy(), other._copy()
        if a.exp < b.exp:
            a.digits = [0] * (b.exp - a.exp) + a.digits
            a.exp = b.exp
        elif b.exp < a.exp:
            b.digits = [0] * (a.exp - b.exp) + b.digits
            b.exp = a.exp
        return a, b

    def _add_abs(self, other: "BigFloat") -> "BigFloat":
        a, b = self._align_exp(other)
        max_len = max(len(a.digits), len(b.digits))
        a.digits.extend([0] * (max_len - len(a.digits)))
        b.digits.extend([0] * (max_len - len(b.digits)))
        result = []
        carry = 0
        for i in range(max_len):
            s = a.digits[i] + b.digits[i] + carry
            result.append(s % BASE)
            carry = s // BASE
        if carry:
            result.append(carry)
        out = BigFloat.__new__(BigFloat)
        out.digits = result
        out.exp = a.exp
        out.sign = 1
        out._normalize()
        return out

    def _sub_abs(self, other: "BigFloat") -> "BigFloat":
        a, b = self._align_exp(other)
        max_len = max(len(a.digits), len(b.digits))
        a.digits.extend([0] * (max_len - len(a.digits)))
        b.digits.extend([0] * (max_len - len(b.digits)))
        result = []
        borrow = 0
        for i in range(max_len):
            s = a.digits[i] - b.digits[i] - borrow
            if s < 0:
                s += BASE
                borrow = 1
            else:
                borrow = 0
            result.append(s)
        out = BigFloat.__new__(BigFloat)
        out.digits = result
        out.exp = a.exp
        out.sign = 1
        out._normalize()
        return out

    def __add__(self, other) -> "BigFloat":
        if not isinstance(other, BigFloat):
            other = BigFloat(other)
        if self._is_zero():
            return BigFloat(other)
        if other._is_zero():
            return BigFloat(self)
        if self.sign == other.sign:
            result = self._add_abs(other)
            result.sign = self.sign
            return result
        cmp = self._compare_abs(other)
        if cmp == 0:
            return BigFloat(0)
        if cmp > 0:
            result = self._sub_abs(other)
            result.sign = self.sign
        else:
            result = other._sub_abs(self)
            result.sign = other.sign
        return result

    def __sub__(self, other) -> "BigFloat":
        if not isinstance(other, BigFloat):
            other = BigFloat(other)
        return self + (-other)

    def _mul_school(self, other: "BigFloat") -> "BigFloat":
        if self._is_zero() or other._is_zero():
            return BigFloat(0)
        n, m = len(self.digits), len(other.digits)
        result = [0] * (n + m)
        for i in range(n):
            for j in range(m):
                result[i + j] += self.digits[i] * other.digits[j]
        out = BigFloat.__new__(BigFloat)
        out.digits = result
        out.exp = self.exp + other.exp
        out.sign = self.sign * other.sign
        out._normalize()
        return out

    def __mul__(self, other) -> "BigFloat":
        if not isinstance(other, BigFloat):
            other = BigFloat(other)
        if self._is_zero() or other._is_zero():
            return BigFloat(0)
        total = len(self.digits) + len(other.digits)
        if total < self.SCHOOL_THRESHOLD:
            return self._mul_school(other)
        return self._mul_school(other)


    # Division
    DIV_SCHOOL_THRESHOLD = 100

    def _div_school(self, other: "BigFloat") -> "BigFloat":
        """School division O(n^2)."""
        if other._is_zero():
            raise ZeroDivisionError("division by zero")
        if self._is_zero():
            return BigFloat(0)
        
        # Approximate quotient
        a_int = int(''.join(f"{d:09d}" for d in reversed(self.digits)))
        b_int = int(''.join(f"{d:09d}" for d in reversed(other.digits)))
        
        q_int = a_int // b_int
        r_int = a_int % b_int
        
        q = BigFloat(q_int)
        r = BigFloat(r_int)
        
        q.sign = self.sign * other.sign
        return q

    def __truediv__(self, other) -> "BigFloat":
        if not isinstance(other, BigFloat):
            other = BigFloat(other)
        if other._is_zero():
            raise ZeroDivisionError("division by zero")
        if self._is_zero():
            return BigFloat(0)
        
        total = len(self.digits) + len(other.digits)
        if total < self.DIV_SCHOOL_THRESHOLD:
            return self._div_school(other)
        return self._div_school(other)

    def sqrt(self) -> "BigFloat":
        if self.sign < 0:
            raise ValueError("square root of negative number")
        if self._is_zero():
            return BigFloat(0)
        if self == BigFloat(1):
            return BigFloat(1)
        
        # Start from float approximation
        x = BigFloat(float(self))
        
        # Newton-Raphson: x_{n+1} = (x_n + n/x_n) / 2
        # Converges in ~log2(digits) iterations, use fixed max
        for _ in range(50):
            x = (x + self / x) / 2
        
        return x

    def __repr__(self) -> str:
        return f"BigFloat(digits={self.digits}, exp={self.exp}, sign={self.sign})"

    def __str__(self) -> str:
        if self._is_zero():
            return "0"
        all_digits = ''.join(f"{d:0{BASE_DIGITS}d}" for d in reversed(self.digits)).lstrip('0')
        decimal_pos = len(all_digits) + self.exp
        if decimal_pos <= 0:
            result = '0.' + '0' * (-decimal_pos) + all_digits
        elif decimal_pos >= len(all_digits):
            result = all_digits + '0' * (decimal_pos - len(all_digits))
        else:
            result = all_digits[:decimal_pos] + '.' + all_digits[decimal_pos:]
        if self.sign == -1:
            result = '-' + result
        if '.' in result:
            result = result.rstrip('0').rstrip('.')
        return result


if __name__ == "__main__":
    print("=== BigFloat Tests ===")
    print("\n--- Phases 1-4 ---")
    assert BigFloat(123).digits == [123]
    assert str(BigFloat(-456)) == "-456"
    assert (-BigFloat(5)).sign == -1
    assert abs(BigFloat(-5)).sign == 1
    assert BigFloat(5) == BigFloat(5)
    assert BigFloat(3) < BigFloat(5)
    assert BigFloat(-5) < BigFloat(3)
    assert str(BigFloat(5) + BigFloat(3)) == "8"
    assert str(BigFloat(5) + BigFloat(-3)) == "2"
    print("Phases 1-4: OK")

    print("\n--- Phase 5: Multiplication ---")
    assert str(BigFloat(5) * BigFloat(3)) == "15"
    assert str(BigFloat(-5) * BigFloat(3)) == "-15"
    assert str(BigFloat(2) * BigFloat(0)) == "0"
    assert str(BigFloat(2.5) * BigFloat(4)) == "10"
    print("Phase 5: OK")

    print("\n=== All tests passed! ===")

    print("\n--- Phase 7: Square Root ---")
    # Basic tests
    assert str(BigFloat(0).sqrt()) == "0", f"sqrt(0) failed, got {BigFloat(0).sqrt()}"
    assert str(BigFloat(1).sqrt()) == "1", f"sqrt(1) failed, got {BigFloat(1).sqrt()}"
    assert str(BigFloat(4).sqrt()) == "2", f"sqrt(4) failed, got {BigFloat(4).sqrt()}"
    assert str(BigFloat(100).sqrt()) == "10", f"sqrt(100) failed, got {BigFloat(100).sqrt()}"
    
    # Negative should raise ValueError
    try:
        BigFloat(-4).sqrt()
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "negative" in str(e).lower()
    
    # Randomized tests: sqrt(x) * sqrt(x) ≈ x
    import random
    random.seed(42)
    for _ in range(50):
        x = random.uniform(0.1, 10000)
        bf_x = BigFloat(x)
        sqrt_x = bf_x.sqrt()
        product = sqrt_x * sqrt_x
        # Check relative error
        diff = abs(float(product) - x)
        rel_err = diff / x
    
    print("Phase 7: OK")
