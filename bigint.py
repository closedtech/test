"""BigInt - Arbitrary precision integer arithmetic in Python with FFT multiplication."""

import math


class BigInt:
    """Arbitrary precision integer using decimal string representation."""

    # Multiplication thresholds (digit count)
    SINGLE_DIGIT_THRESHOLD = 1
    KARATSUBA_THRESHOLD = 100
    FFT_THRESHOLD = 1000

    # Division thresholds (digit count)
    DIV_SCHOOL_THRESHOLD = 1000
    DIV_BURNIKEL_THRESHOLD = 10000

    def __init__(self, value: "int | str"):
        """Construct BigInt from string or int."""
        if isinstance(value, BigInt):
            self._value = value._value
            self._sign = value._sign
            return

        if isinstance(value, int):
            value = str(value)

        if not isinstance(value, str):
            raise TypeError(f"Expected str or int, got {type(value).__name__}")

        value = value.strip()
        if not value:
            raise ValueError("Empty string is not a valid integer")

        if value.startswith("-"):
            self._sign = "-"
            self._value = value[1:].lstrip("0") or "0"
        elif value.startswith("+"):
            self._sign = ""
            self._value = value[1:].lstrip("0") or "0"
        else:
            self._sign = ""
            self._value = value.lstrip("0") or "0"

        if not self._value.isdigit():
            raise ValueError(f"Invalid integer string: '{value}'")

    # ---------- comparison ----------
    def _compare(self, other: "BigInt") -> int:
        if self._sign != other._sign:
            return -1 if self._sign == "-" else 1
        cmp_val = 0
        if len(self._value) != len(other._value):
            cmp_val = -1 if len(self._value) < len(other._value) else 1
        else:
            cmp_val = -1 if self._value < other._value else (1 if self._value > other._value else 0)
        if self._sign == "-":
            cmp_val = -cmp_val
        return cmp_val

    def _compare_abs(self, other: "BigInt") -> int:
        if len(self._value) != len(other._value):
            return -1 if len(self._value) < len(other._value) else 1
        if self._value < other._value:
            return -1
        if self._value > other._value:
            return 1
        return 0

    def __eq__(self, other: "int | BigInt") -> bool:
        if isinstance(other, int):
            other = BigInt(other)
        elif not isinstance(other, BigInt):
            return False
        return self._compare(other) == 0

    def __lt__(self, other: "int | BigInt") -> bool:
        if isinstance(other, int):
            other = BigInt(other)
        return self._compare(other) < 0

    def __le__(self, other: "int | BigInt") -> bool:
        if isinstance(other, int):
            other = BigInt(other)
        return self._compare(other) <= 0

    def __gt__(self, other: "int | BigInt") -> bool:
        if isinstance(other, int):
            other = BigInt(other)
        return self._compare(other) > 0

    def __ge__(self, other: "int | BigInt") -> bool:
        if isinstance(other, int):
            other = BigInt(other)
        return self._compare(other) >= 0

    def __bool__(self) -> bool:
        return self._value != "0"

    def __repr__(self) -> str:
        return f"BigInt('{self._sign}{self._value}')"

    def to_string(self) -> str:
        return f"{self._sign}{self._value}"

    def __neg__(self) -> "BigInt":
        result = BigInt.__new__(BigInt)
        result._value = self._value
        result._sign = "-" if self._sign == "" else ""
        return result

    def __pos__(self) -> "BigInt":
        return BigInt(self)

    def abs(self) -> "BigInt":
        result = BigInt(self)
        result._sign = ""
        return result

    # ---------- addition ----------
    def __add__(self, other: "int | BigInt") -> "BigInt":
        if isinstance(other, int):
            other = BigInt(other)
        elif not isinstance(other, BigInt):
            return NotImplemented
        return self._add(other)

    def _add(self, other: "BigInt") -> "BigInt":
        if self._sign == other._sign:
            result = BigInt(self)
            result._value = self._add_abs(other._value)
            return result
        cmp = self._compare_abs(other)
        if cmp == 0:
            return BigInt(0)
        if cmp > 0:
            result = BigInt(self)
            result._value = self._sub_abs(other._value)
        else:
            result = BigInt(other)
            result._value = self._sub_abs(other._value)
        return result

    def _add_abs(self, b: str) -> str:
        max_len = max(len(self._value), len(b))
        a = self._value.zfill(max_len)
        b = b.zfill(max_len)
        carry = 0
        result = []
        for i in range(max_len - 1, -1, -1):
            s = int(a[i]) + int(b[i]) + carry
            result.append(str(s % 10))
            carry = s // 10
        if carry:
            result.append(str(carry))
        return "".join(reversed(result))

    # ---------- subtraction ----------
    def __sub__(self, other: "int | BigInt") -> "BigInt":
        if isinstance(other, int):
            other = BigInt(other)
        elif not isinstance(other, BigInt):
            return NotImplemented
        return self._sub(other)

    def _sub(self, other: "BigInt") -> "BigInt":
        if self._sign != other._sign:
            result = BigInt(self)
            result._value = self._add_abs(other._value)
            return result
        cmp = self._compare_abs(other)
        if cmp == 0:
            return BigInt(0)
        if cmp > 0:
            result = BigInt(self)
            result._value = self._sub_abs(other._value)
        else:
            result = BigInt(other)
            result._sign = "-" if self._sign == "" else ""
            result._value = other._sub_abs(self._value)
        return result

    def _sub_abs(self, b: str) -> str:
        max_len = max(len(self._value), len(b))
        a = self._value.zfill(max_len)
        b = b.zfill(max_len)
        borrow = 0
        result = []
        for i in range(max_len - 1, -1, -1):
            s = int(a[i]) - int(b[i]) - borrow
            if s < 0:
                s += 10
                borrow = 1
            else:
                borrow = 0
            result.append(str(s))
        return "".join(reversed(result)).lstrip("0") or "0"

    # ---------- multiplication ----------
    def __mul__(self, other: "int | BigInt") -> "BigInt":
        if isinstance(other, int):
            other = BigInt(other)
        elif not isinstance(other, BigInt):
            return NotImplemented
        return self._mul(other)

    def _mul(self, other: "BigInt") -> "BigInt":
        if self._value == "0" or other._value == "0":
            return BigInt(0)
        a_len = len(self._value)
        b_len = len(other._value)
        # Single digit multiplication (fast path)
        if a_len <= self.SINGLE_DIGIT_THRESHOLD or b_len <= self.SINGLE_DIGIT_THRESHOLD:
            return self._multiply_single(other)
        # School for small numbers
        if a_len < self.KARATSUBA_THRESHOLD and b_len < self.KARATSUBA_THRESHOLD:
            return self._multiply_school(other)
        # FFT for very large numbers
        if a_len + b_len > self.FFT_THRESHOLD:
            return self._multiply_fft(other)
        # Karatsuba for medium numbers
        return self._multiply_karatsuba(other)

    def _multiply_single(self, other: "BigInt") -> "BigInt":
        """Multiply by single digit O(n)."""
        if len(other._value) == 1:
            single_digit = int(other._value)
            multiplier = self
        else:
            single_digit = int(self._value)
            multiplier = other
        if single_digit == 0:
            return BigInt(0)
        if single_digit == 1:
            result = BigInt(multiplier)
            result._sign = "-" if self._sign != other._sign else ""
            return result
        a = multiplier._value
        result = [0] * (len(a) + 1)
        carry = 0
        for i in range(len(a) - 1, -1, -1):
            mul = int(a[i]) * single_digit + carry
            result[i + 1] = mul % 10
            carry = mul // 10
        if carry:
            result[0] = carry
        start = 0
        while start < len(result) - 1 and result[start] == 0:
            start += 1
        value_str = "".join(str(d) for d in result[start:])
        sign = "-" if self._sign != other._sign else ""
        bi = BigInt.__new__(BigInt)
        bi._value = value_str
        bi._sign = sign
        return bi

    def _multiply_school(self, other: "BigInt") -> "BigInt":
        """School multiplication O(n²)."""
        a = self._value
        b = other._value
        result = [0] * (len(a) + len(b))
        for i in range(len(a) - 1, -1, -1):
            for j in range(len(b) - 1, -1, -1):
                mul = int(a[i]) * int(b[j])
                p1 = i + j
                p2 = i + j + 1
                sum_val = mul + result[p2]
                result[p2] = sum_val % 10
                result[p1] += sum_val // 10
        start = 0
        while start < len(result) - 1 and result[start] == 0:
            start += 1
        value_str = "".join(str(d) for d in result[start:])
        sign = "-" if self._sign != other._sign else ""
        bi = BigInt.__new__(BigInt)
        bi._value = value_str
        bi._sign = sign
        return bi

    def _multiply_karatsuba(self, other: "BigInt") -> "BigInt":
        """Karatsuba multiplication O(n^1.585)."""
        if self._value == "0" or other._value == "0":
            return BigInt(0)
        a_len = len(self._value)
        b_len = len(other._value)
        if a_len < self.KARATSUBA_THRESHOLD or b_len < self.KARATSUBA_THRESHOLD:
            return self._multiply_school(other)

        # Pad to same length (even split)
        max_len = max(a_len, b_len)
        if max_len % 2 == 1:
            max_len += 1

        a_padded = self._value.zfill(max_len)
        b_padded = other._value.zfill(max_len)

        m2 = max_len // 2

        # Split at midpoint
        a1_str = a_padded[:m2]
        a0_str = a_padded[m2:]
        b1_str = b_padded[:m2]
        b0_str = b_padded[m2:]

        a1 = BigInt(a1_str.lstrip("0") or "0")
        a0 = BigInt(a0_str.lstrip("0") or "0")
        b1 = BigInt(b1_str.lstrip("0") or "0")
        b0 = BigInt(b0_str.lstrip("0") or "0")

        z0 = a0._multiply_karatsuba(b0)
        z2 = a1._multiply_karatsuba(b1)
        z1 = (a0 + a1)._multiply_karatsuba(b0 + b1) - z0 - z2

        result = z0 + (z1._shift_digits(m2)) + (z2._shift_digits(2 * m2))
        result._sign = "-" if self._sign != other._sign else ""
        return result

    def _shift_digits(self, count: int) -> "BigInt":
        """Shift number left by count decimal digits (multiply by 10^count)."""
        if self._value == "0" or count == 0:
            return BigInt(self)
        result = BigInt.__new__(BigInt)
        result._value = self._value + "0" * count
        result._sign = self._sign
        return result

    @staticmethod
    def _next_power_of_2(n: int) -> int:
        return 1 << (n - 1).bit_length()

    @staticmethod
    def _fft(a: list[complex]) -> list[complex]:
        n = len(a)
        if n == 1:
            return a
        j = 0
        for i in range(1, n):
            bit = n >> 1
            while j & bit:
                j ^= bit
                bit >>= 1
            j ^= bit
            if i < j:
                a[i], a[j] = a[j], a[i]
        m = 2
        while m <= n:
            half_m = m // 2
            angle = -2.0 * math.pi / m
            w_base = complex(math.cos(angle), math.sin(angle))
            for start in range(0, n, m):
                w = complex(1.0)
                for k in range(half_m):
                    u = a[start + k]
                    v = a[start + k + half_m] * w
                    a[start + k] = u + v
                    a[start + k + half_m] = u - v
                    w *= w_base
            m <<= 1
        return a

    @staticmethod
    def _ifft(a: list[complex]) -> list[complex]:
        n = len(a)
        for i in range(n):
            a[i] = complex(a[i].real, -a[i].imag)
        BigInt._fft(a)
        for i in range(n):
            a[i] = complex(a[i].real / n, -a[i].imag / n)
        return a

    def _multiply_fft(self, other: "BigInt") -> "BigInt":
        """FFT multiplication O(n log n)."""
        a_digits = [int(ch) for ch in self._value][::-1]
        b_digits = [int(ch) for ch in other._value][::-1]
        result_size = len(a_digits) + len(b_digits)
        n = BigInt._next_power_of_2(result_size)
        a_digits.extend([0] * (n - len(a_digits)))
        b_digits.extend([0] * (n - len(b_digits)))
        a_complex = [complex(x) for x in a_digits]
        b_complex = [complex(x) for x in b_digits]
        BigInt._fft(a_complex)
        BigInt._fft(b_complex)
        c_complex = [a_complex[i] * b_complex[i] for i in range(n)]
        BigInt._ifft(c_complex)
        coefs = [int(round(c.real)) for c in c_complex]
        for i in range(len(coefs)):
            if coefs[i] >= 10:
                carry = coefs[i] // 10
                coefs[i] %= 10
                if i + 1 < len(coefs):
                    coefs[i + 1] += carry
                else:
                    coefs.append(carry)
        while len(coefs) > 1 and coefs[-1] == 0:
            coefs.pop()
        value_str = "".join(str(d) for d in reversed(coefs))
        sign = "-" if self._sign != other._sign else ""
        bi = BigInt.__new__(BigInt)
        bi._value = value_str
        bi._sign = sign
        return bi

    # ---------- division ----------
    def __floordiv__(self, other: "int | BigInt") -> "BigInt":
        if isinstance(other, int):
            other = BigInt(other)
        elif not isinstance(other, BigInt):
            return NotImplemented
        return self._divmod(other)[0]

    def __truediv__(self, other: "int | BigInt") -> "BigInt":
        if isinstance(other, int):
            other = BigInt(other)
        elif not isinstance(other, BigInt):
            return NotImplemented
        return self._divmod(other)[0]

    def __mod__(self, other: "int | BigInt") -> "BigInt":
        if isinstance(other, int):
            other = BigInt(other)
        elif not isinstance(other, BigInt):
            return NotImplemented
        return self._divmod(other)[1]

    def __divmod__(self, other: "int | BigInt") -> tuple["BigInt", "BigInt"]:
        if isinstance(other, int):
            other = BigInt(other)
        elif not isinstance(other, BigInt):
            return NotImplemented
        return self._divmod(other)

    def _divmod(self, other: "BigInt") -> tuple["BigInt", "BigInt"]:
        """Integer division and modulo: returns (quotient, remainder).
        
        Python floor division semantics:
        - a = b*q + r where 0 <= r < |b|
        - q is truncated toward negative infinity
        - r has same sign as divisor (or is 0)
        """
        if other._value == "0":
            raise ZeroDivisionError("division by zero")

        a_len = len(self._value)
        b_len = len(other._value)

        # Work with absolute values
        a_abs = self._value.lstrip("-")
        b_abs = other._value.lstrip("-")
        a_neg = self._sign == "-"
        b_neg = other._sign == "-"

        # Choose algorithm based on size
        if a_len < 100 or b_len < 10:
            q, r = self._divide_school(a_abs, b_abs)
        elif a_len < 500:
            q, r = self._divide_barrett(a_abs, b_abs)
        else:
            q, r = self._divide_newton(a_abs, b_abs)

        # Apply floor division sign rules
        q_abs = int(q._value)
        r_abs = int(r._value)

        if a_neg == b_neg:
            # Same sign: q positive, r has b's sign
            if b_neg:
                r._sign = "-"
        else:
            # Different signs: q truncated toward -infinity
            if r_abs != 0:
                q_abs = -(q_abs + 1)
                r_abs = int(b_abs) - r_abs
                q._value = str(abs(q_abs))
                q._sign = "-" if q_abs < 0 else ""
            else:
                q._sign = "-"
            r._value = str(r_abs)
            r._sign = "-" if b_neg else ""

        return q, r

    def _divide_school(self, a_str: str, b_str: str) -> tuple["BigInt", "BigInt"]:
        """School division O(n²)."""
        if int(b_str) == 0:
            raise ZeroDivisionError("division by zero")
        if len(a_str) < len(b_str) or (len(a_str) == len(b_str) and a_str < b_str):
            qi = BigInt.__new__(BigInt)
            qi._value = "0"
            qi._sign = ""
            ri = BigInt.__new__(BigInt)
            ri._value = a_str.lstrip("0") or "0"
            ri._sign = ""
            return qi, ri

        a = a_str
        b = b_str
        quotient = []
        current = ""

        for digit in a:
            current += digit
            current_stripped = current.lstrip("0") or "0"
            b_stripped = b.lstrip("0") or "0"
            q = 0
            cur_int = int(current_stripped)
            b_stripped_int = int(b_stripped)
            while len(current_stripped) > len(b_stripped) or (
                len(current_stripped) == len(b_stripped) and current_stripped >= b_stripped
            ):
                cur_int -= b_stripped_int
                q += 1
                current_stripped = str(cur_int).lstrip("0") or "0"
            quotient.append(str(q))
            current = current_stripped

        quotient_str = "".join(quotient).lstrip("0") or "0"
        remainder_str = current.lstrip("0") or "0"
        qi = BigInt.__new__(BigInt)
        qi._value = quotient_str
        qi._sign = ""
        ri = BigInt.__new__(BigInt)
        ri._value = remainder_str
        ri._sign = ""
        return qi, ri

    def _divide_newton(self, a_str: str, b_str: str) -> tuple["BigInt", "BigInt"]:
        """Newton-Raphson division O(n log n)."""
        if int(b_str) == 0:
            raise ZeroDivisionError("division by zero")

        a_int = int(a_str)
        b_int = int(b_str)

        if abs(a_int) < abs(b_int):
            qi = BigInt.__new__(BigInt)
            qi._value = "0"
            qi._sign = ""
            ri = BigInt.__new__(BigInt)
            ri._value = str(abs(a_int))
            ri._sign = ""
            return qi, ri

        k = len(b_str)
        R = 10 ** (2 * k + 4)

        y = R // b_int + 1
        for _ in range(100):
            y_new = y * (2 * R - b_int * y) // R
            if y_new == y:
                break
            y = y_new

        q_approx = a_int * y // R

        q_big = BigInt(q_approx)
        r_big = BigInt(a_int) - q_big * BigInt(b_int)

        while r_big < BigInt(0):
            q_big = q_big - BigInt(1)
            r_big = r_big + BigInt(b_int)

        while r_big >= BigInt(b_int):
            q_big = q_big + BigInt(1)
            r_big = r_big - BigInt(b_int)

        return q_big, r_big

    def _divide_barrett(self, a_str: str, b_str: str) -> tuple["BigInt", "BigInt"]:
        """Barrett division O(n log n)."""
        if int(b_str) == 0:
            raise ZeroDivisionError("division by zero")

        a_int = int(a_str)
        b_int = int(b_str)

        if abs(a_int) < abs(b_int):
            qi = BigInt.__new__(BigInt)
            qi._value = "0"
            qi._sign = ""
            ri = BigInt.__new__(BigInt)
            ri._value = str(abs(a_int))
            ri._sign = ""
            return qi, ri

        BASE = 1000
        k = len(b_str)

        a_digits = [int(a_str[max(0, i):i+3][::-1]) for i in range(0, len(a_str), 3)][::-1]
        b_digits = [int(b_str[max(0, i):i+3][::-1]) for i in range(0, len(b_str), 3)][::-1]

        n = len(b_digits)
        m = len(a_digits) - n + 1

        if m <= 0:
            qi = BigInt.__new__(BigInt)
            qi._value = "0"
            qi._sign = ""
            ri = BigInt.__new__(BigInt)
            ri._value = str(abs(a_int))
            ri._sign = ""
            return qi, ri

        B_mu = BASE ** (2 * n)
        mu_hat = B_mu // b_int

        if len(a_digits) > n:
            a_top = sum(a_digits[i] * (BASE ** (len(a_digits) - i - 1)) for i in range(len(a_digits) - n - 1))
        else:
            a_top = sum(a_digits[i] * (BASE ** (len(a_digits) - i - 1)) for i in range(len(a_digits)))

        q_hat = (a_top * mu_hat) // (BASE ** (n + 1))

        if q_hat > BASE ** (m + 2):
            q_hat = BASE ** (m + 2)

        q_int = q_hat
        for _ in range(5):
            q_b = q_int * b_int
            if q_b > a_int:
                q_int -= 1
            elif q_b < a_int - b_int:
                room = (a_int - q_b) // b_int
                if room > 0:
                    q_int += min(room, BASE - 1)
                else:
                    break
            else:
                break

        r_int = a_int - q_int * b_int

        while r_int < 0:
            q_int -= 1
            r_int += b_int

        while r_int >= abs(b_int):
            q_int += 1
            r_int -= abs(b_int)

        qi = BigInt.__new__(BigInt)
        qi._value = str(q_int)
        qi._sign = ""
        ri = BigInt.__new__(BigInt)
        ri._value = str(abs(r_int)).lstrip("0") or "0"
        ri._sign = ""

        return qi, ri

    # ---------- power and sqrt ----------
    def __pow__(self, exp: int) -> "BigInt":
        if not isinstance(exp, int):
            raise TypeError(f"Expected int, got {type(exp).__name__}")
        if exp < 0:
            raise ValueError("Negative exponent")
        result = BigInt(1)
        base = BigInt(self)
        e = exp
        while e > 0:
            if e & 1:
                result = result * base
            base = base * base
            e >>= 1
        return result

    def sqrt(self) -> "BigInt":
        """Integer square root (floor sqrt)."""
        if self < BigInt(0):
            raise ValueError("sqrt от отрицательного числа")
        if self == BigInt(0):
            return BigInt(0)
        x = self
        y = (x + BigInt(1)) // BigInt(2)
        while y < x:
            x = y
            y = (x + self // x) // BigInt(2)
        return x
