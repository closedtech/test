"""BigFloat - Arbitrary precision floating point arithmetic.

Uses base 10^9 (1,000,000,000) with each digit stored as an int.
Little-endian: digits[0] is the least significant digit.
Exponent tracks the power of BASE corresponding to the first digit.
Sign is 1 or -1.
"""

BASE = 10**9
BASE_DIGITS = 9


class BigFloat:
    """
    Arbitrary precision floating point number.

    Attributes:
        digits: list[int] — little-endian base BASE digits
        exp: int — exponent (power of BASE for the most significant digit)
        sign: int — 1 or -1

    Representation: sign * sum(digits[i] * BASE^(i-exp)) for i in range(len(digits))
    """

    __slots__ = ('digits', 'exp', 'sign')

    def __init__(self, value=0):
        """Initialize a BigFloat from int, float, str, or BigFloat."""
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
            raise TypeError(f"Cannot convert {type(value).__name__} to BigFloat")

        self._normalize()

    def _from_int(self, value: int):
        """Convert an integer to BigFloat representation."""
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
        """Convert a float to BigFloat representation."""
        if value < 0:
            self.sign = -1
            value = -value
        elif value == 0:
            self.sign = 1

        if value == 0:
            self.digits = [0]
            self.exp = 0
            return

        str_val = f"{value:.15g}"
        self._from_str(str_val)

    def _from_str(self, value: str):
        """Convert a string to BigFloat representation."""
        value = value.strip()

        if not value:
            raise ValueError("Empty string cannot be converted to BigFloat")

        if value.startswith('-'):
            self.sign = -1
            value = value[1:]
        elif value.startswith('+'):
            self.sign = 1
            value = value[1:]
        else:
            self.sign = 1

        if value.lower() in ('inf', 'infinity'):
            raise ValueError("Infinity not supported")
        if value.lower() in ('nan', 'nans'):
            raise ValueError("NaN not supported")

        if 'e' in value.lower():
            base_part, exp_part = value.lower().split('e')
            exp = int(exp_part)
            if '.' in base_part:
                int_part, frac_part = base_part.split('.')
                frac_part = frac_part.rstrip('0')
                exp += len(frac_part)
                base_str = int_part + frac_part
            else:
                base_str = base_part
            self._from_str(base_str)
            self.exp += exp
            return

        if '.' in value:
            int_part, frac_part = value.split('.')
            frac_part = frac_part.rstrip('0')
        else:
            int_part = value
            frac_part = ''

        combined = int_part + frac_part
        exp_adjust = -len(frac_part) if frac_part else 0
        combined = combined.lstrip('0') or '0'

        val_int = int(combined) if combined != '' else 0
        self._from_int(val_int)
        self.exp += exp_adjust

    def _normalize(self):
        """Remove leading zeros and ensure proper representation."""
        while len(self.digits) > 1 and self.digits[-1] == 0:
            self.digits.pop()

        if self._is_zero():
            self.digits = [0]
            self.exp = 0
            self.sign = 1

    def _is_zero(self) -> bool:
        """Return True if the value is zero."""
        return len(self.digits) == 1 and self.digits[0] == 0

    # ---------- sign operations ----------
    def __neg__(self):
        """Return a new BigFloat with negated sign."""
        result = self._copy()
        result.sign = -result.sign
        if result._is_zero():
            result.sign = 1
        return result

    def __abs__(self):
        """Return a new BigFloat with absolute value (sign always 1)."""
        result = self._copy()
        result.sign = 1
        return result

    def _copy(self):
        """Return a new BigFloat with the same digits, exp, and sign."""
        new = BigFloat.__new__(BigFloat)
        new.digits = list(self.digits)
        new.exp = self.exp
        new.sign = self.sign
        return new

    # ---------- comparison ----------
    def _compare_abs(self, other: "BigFloat") -> int:
        """Compare absolute values. Returns -1, 0, or 1."""
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

    # ---------- string representation ----------
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

    # Phase 1
    print("\n--- Phase 1: Core ---")
    assert BigFloat(123).digits == [123]
    assert str(BigFloat(-456)) == "-456"
    assert BigFloat(0)._is_zero()
    print("Phase 1: OK")

    # Phase 2
    print("\n--- Phase 2: Sign ---")
    assert (-BigFloat(5)).sign == -1
    assert (-BigFloat(-5)).sign == 1
    assert abs(BigFloat(-5)).sign == 1
    print("Phase 2: OK")

    # Phase 3
    print("\n--- Phase 3: Comparison ---")
    assert BigFloat(5) == BigFloat(5)
    assert BigFloat(5) != BigFloat(3)
    assert BigFloat(3) < BigFloat(5)
    assert BigFloat(-5) < BigFloat(3)
    assert bool(BigFloat(5)) == True
    assert bool(BigFloat(0)) == False
    print("Phase 3: OK")

    print("\n=== All Phase 1-3 tests passed! ===")
