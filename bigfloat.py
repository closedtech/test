"""BigFloat - Arbitrary precision floating point arithmetic."""

BASE = 10**9
BASE_DIGITS = 9


class BigFloat:
    __slots__ = ('digits', 'exp', 'sign')

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

    # Sign operations
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

    # Comparison
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

    # Addition/Subtraction
    def _align_exp(self, other: "BigFloat"):
        """Align exponents, return (self, other) with same exp."""
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
        """Add absolute values (both positive)."""
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
        """Subtract absolute values (self >= other)."""
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
        # Different signs
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

    # String representation
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

    # Phase 1-3
    print("\n--- Phases 1-3 ---")
    assert BigFloat(123).digits == [123]
    assert str(BigFloat(-456)) == "-456"
    assert (-BigFloat(5)).sign == -1
    assert abs(BigFloat(-5)).sign == 1
    assert BigFloat(5) == BigFloat(5)
    assert BigFloat(3) < BigFloat(5)
    assert BigFloat(-5) < BigFloat(3)
    print("Phases 1-3: OK")

    # Phase 4
    print("\n--- Phase 4: Add/Sub ---")
    assert str(BigFloat(5) + BigFloat(3)) == "8"
    assert str(BigFloat(5) + BigFloat(-3)) == "2"
    assert str(BigFloat(-5) + BigFloat(3)) == "-2"
    assert str(BigFloat(5) - BigFloat(3)) == "2"
    assert str(BigFloat(3) - BigFloat(5)) == "-2"
    assert str(BigFloat(5) + BigFloat(0)) == "5"
    assert str(BigFloat(0) + BigFloat(5)) == "5"
    assert str(BigFloat(5) - BigFloat(5)) == "0"
    print("Phase 4: OK")

    print("\n=== All tests passed! ===")
