"""BigInt - Arbitrary precision integer arithmetic in Python with FFT multiplication."""

import math


class BigInt:
    """Arbitrary precision integer using decimal string representation."""

    FFT_THRESHOLD = 100  # Use FFT for numbers > 100 digits
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

    def abs(self) -> "BigInt":
        result = BigInt(self)
        result._sign = ""
        return result

    def _abs(self) -> "BigInt":
        return self.abs()

    def _ensure_bigint(self, other: "int | BigInt") -> "BigInt":
        if isinstance(other, BigInt):
            return other
        if isinstance(other, int):
            return BigInt(other)
        raise TypeError(f"Cannot operate with {type(other).__name__}")

    def __repr__(self) -> str:
        return f"BigInt('{self._sign}{self._value}')"

    def to_string(self) -> str:
        return f"{self._sign}{self._value}"

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

    def __eq__(self, other: "int | BigInt") -> bool:
        other = self._ensure_bigint(other)
        return self._compare(other) == 0

    def __lt__(self, other: "int | BigInt") -> bool:
        other = self._ensure_bigint(other)
        return self._compare(other) < 0

    def __le__(self, other: "int | BigInt") -> bool:
        other = self._ensure_bigint(other)
        return self._compare(other) <= 0

    def __gt__(self, other: "int | BigInt") -> bool:
        other = self._ensure_bigint(other)
        return self._compare(other) > 0

    def __ge__(self, other: "int | BigInt") -> bool:
        other = self._ensure_bigint(other)
        return self._compare(other) >= 0

    def __bool__(self) -> bool:
        return self._value != "0"

    # ---------- addition ----------
    def __add__(self, other: "int | BigInt") -> "BigInt":
        other = self._ensure_bigint(other)
        return self._add(other)

    def __radd__(self, other: "int") -> "BigInt":
        return self.__add__(other)

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
            result._sign = ""
            result._value = self._sub_abs(other._value)
        else:
            result = BigInt(other)
            result._sign = ""
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

    def _compare_abs(self, other: "BigInt") -> int:
        if len(self._value) != len(other._value):
            return -1 if len(self._value) < len(other._value) else 1
        if self._value < other._value:
            return -1
        if self._value > other._value:
            return 1
        return 0

    # ---------- subtraction ----------
    def __sub__(self, other: "int | BigInt") -> "BigInt":
        other = self._ensure_bigint(other)
        return self._sub(other)

    def __rsub__(self, other: "int") -> "BigInt":
        other = BigInt(other)
        return other._sub(self)

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
            result._value = self._sub_abs(other._value)
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
        other = self._ensure_bigint(other)
        return self._mul(other)

    def __rmul__(self, other: "int") -> "BigInt":
        return self.__mul__(other)

    def _mul(self, other: "BigInt") -> "BigInt":
        if self._value == "0" or other._value == "0":
            return BigInt(0)
        a_len = len(self._value)
        b_len = len(other._value)
        if a_len + b_len > self.FFT_THRESHOLD:
            return self._multiply_fft(other)
        return self._multiply_school(other)

    def _multiply_school(self, other: "BigInt") -> "BigInt":
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

    # ========== DIVISION ==========
    def __floordiv__(self, other: "int | BigInt") -> "BigInt":
        other = self._ensure_bigint(other)
        return self._divmod(other)[0]

    def __truediv__(self, other: "int | BigInt") -> "BigInt":
        other = self._ensure_bigint(other)
        return self._divmod(other)[0]

    def __rtruediv__(self, other: "int") -> "BigInt":
        other = BigInt(other)
        return other._divmod(self)[0]

    def __mod__(self, other: "int | BigInt") -> "BigInt":
        other = self._ensure_bigint(other)
        return self._divmod(other)[1]

    def __rmod__(self, other: "int") -> "BigInt":
        other = BigInt(other)
        return other._divmod(self)[1]

    def _choose_division(self, a_len: int, b_len: int) -> str:
        n = max(a_len, b_len)
        if n < self.DIV_SCHOOL_THRESHOLD:
            return "school"
        elif n <= self.DIV_BURNIKEL_THRESHOLD:
            return "burnikel"
        else:
            return "barrett"

    # ----- School division O(n²) -----
    def _divide_school(self, a_str: str, b_str: str) -> tuple["BigInt", "BigInt"]:
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
        b_int = int(b)

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

    # ----- Burnikel-Ziegler O(n log n) -----
    # Base = 1000 (3 decimal digits per word)

    @staticmethod
    def _digits_to_base(digits: list[int], base: int = 1000) -> str:
        """Convert little-endian base-{base} digits to decimal string."""
        if not digits:
            return "0"
        if not any(d != 0 for d in digits):
            return "0"
        result = []
        most_sig = True
        for d in reversed(digits):
            if most_sig:
                result.append(str(d))
                most_sig = False
            else:
                result.append(f"{d:0{len(str(base - 1))}d}")
        return "".join(result).lstrip("0") or "0"

    @staticmethod
    def _str_to_base(s: str, base: int = 1000) -> list[int]:
        """Convert decimal string to little-endian base-{base} digits."""
        if not s or s == "0":
            return []
        digits = []
        for i in range(0, len(s), 3):
            chunk = s[max(0, i) : i + 3]
            digits.append(int(chunk))
        # Remove trailing zeros (little-endian, so at the end of list)
        while len(digits) > 1 and digits[-1] == 0:
            digits.pop()
        return digits

    def _divide_burnikel(self, a_str: str, b_str: str) -> tuple["BigInt", "BigInt"]:
        """Burnikel-Ziegler division O(n log n).
        Splits numbers into base-1000 blocks and recurses with fallbacks.
        """
        n = max(len(a_str), len(b_str))
        if n < 40:
            return self._divide_school(a_str, b_str)

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

        # For Burnikel-Ziegler to work efficiently, we need |a| >= 2*|b|.
        # If not, fall back to school division.
        if len(a_str) < 2 * len(b_str):
            return self._divide_school(a_str, b_str)

        # Convert to base 1000 (3 decimal digits per word)
        a_base = self._str_to_base(a_str)
        b_base = self._str_to_base(b_str)

        n_a = len(a_base)
        n_b = len(b_base)

        # m = ceil(max(n_a, n_b) / 3)
        m = (max(n_a, n_b) + 2) // 3
        if m < 1:
            m = 1

        # Pad to 3*m words
        while len(a_base) < 3 * m:
            a_base.append(0)
        while len(b_base) < 3 * m:
            b_base.append(0)

        # Split a = a2*B^(2m) + a1*B^m + a0
        a0 = a_base[0:m]
        a1 = a_base[m:2*m]
        a2 = a_base[2*m:3*m]

        # Split b = b2*B^m + b1 (b2 is most significant, may be 0)
        b0 = b_base[0:m]
        b1 = b_base[m:2*m]
        b2 = b_base[2*m:3*m]

        a2_str = self._digits_to_base(a2).lstrip("0") or "0"
        b2_str = self._digits_to_base(b2).lstrip("0") or "0"
        b1_str = self._digits_to_base(b1).lstrip("0") or "0"

        # If b's leading word is 0, shift
        if b2_str == "0":
            b2_str = b1_str.lstrip("0") or "0"
            if b2_str == "0":
                return self._divide_school(a_str, b_str)

        # Step 1: q1 = floor(a2 / b2), r1 = a - q1*b
        cmp_a2_b2 = (len(a2_str) > len(b2_str)) or (len(a2_str) == len(b2_str) and a2_str >= b2_str)
        if not cmp_a2_b2:
            # q1 = 0, r1 = a
            q1_str = "0"
            r1_big = BigInt(a_str)
        else:
            q1_big, _ = self._divide_burnikel(a2_str, b2_str)
            q1_str = q1_big._value.lstrip("0") or "0"
            if q1_str == "0":
                r1_big = BigInt(a_str)
            else:
                a_big = BigInt(a_str)
                b_big = BigInt(b_str)
                q1_big_int = BigInt(q1_str)
                r1_big = a_big - q1_big_int * b_big

        r1_str = r1_big._value.lstrip("0") or "0"
        if r1_str == "":
            r1_str = "0"

        # If r1 didn't shrink enough, fall back to school division for the remainder
        if len(r1_str) >= len(a_str):
            return self._divide_school(a_str, b_str)

        # Step 2: q2 = floor(r1 / b), r = r1 - q2*b
        q2_big, r2_big = self._divide_burnikel(r1_str, b_str)
        q2_str = q2_big._value.lstrip("0") or "0"

        # Final quotient: q = q1*B^m + q2
        B_m = 1000 ** m
        q1_int = int(q1_str) if q1_str != "0" else 0
        q2_int = int(q2_str) if q2_str != "0" else 0
        q_int = q1_int * B_m + q2_int

        qi = BigInt.__new__(BigInt)
        qi._value = str(q_int)
        qi._sign = ""
        ri = BigInt.__new__(BigInt)
        ri._value = r2_big._value.lstrip("0") or "0"
        ri._sign = ""
        return qi, ri

    # ----- Barrett reduction O(n log n) -----
    def _divide_barrett(self, a_str: str, b_str: str) -> tuple["BigInt", "BigInt"]:
        """Barrett reduction division using FFT multiplication.
        mu = floor(B^(2k) / d), qhat = floor(a_high * mu / B^(k+1)).
        """
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

        B = 1000
        k = (len(b_str) + 2) // 3  # base-B words in divisor
        if k < 1:
            k = 1

        # mu = floor(B^(2k) / d) -- precompute
        # B^(2k) = 1000^(2k), compute via Python int
        B_2k = B ** (2 * k)

        # Convert to Python ints for mu calculation and division
        a_int = int(a_str)
        b_int = int(b_str)
        mu_int = B_2k // b_int

        # a_high: top k+1 base-B digits of a
        # Number of base-B digits in a
        a_base = self._str_to_base(a_str)
        na = len(a_base)

        if na <= k + 1:
            a_high_int = a_int // (B ** (max(0, na - k - 1) * 3))
        else:
            # a_high = floor(a / B^(na - k - 1))
            shift = (na - k - 1)
            a_high_int = a_int // (B ** (shift * 3))

        # qhat = floor(a_high * mu / B^(k+1))
        qhat_int = (a_high_int * mu_int) // (B ** ((k + 1) * 3))

        # Clamp qhat to valid range
        # q < B^m where m = number of base-B digits in a
        m = na
        max_q = B ** m - 1
        if qhat_int > max_q:
            qhat_int = max_q

        # Refine qhat via correction loop
        q_int = qhat_int
        for _ in range(3):
            qb = q_int * b_int
            if qb > a_int:
                q_int -= 1
            else:
                # Check if we can increment
                while (q_int + 1) * b_int <= a_int:
                    q_int += 1
                break

        r_int = a_int - q_int * b_int

        qi = BigInt.__new__(BigInt)
        qi._value = str(q_int)
        qi._sign = ""
        ri = BigInt.__new__(BigInt)
        ri._value = str(r_int).lstrip("0") or "0"
        ri._sign = ""
        return qi, ri

    def _divmod(self, other: "BigInt") -> tuple["BigInt", "BigInt"]:
        """Integer division and modulo: returns (quotient, remainder).
        Chooses algorithm based on input size.
        """
        if other._value == "0":
            raise ZeroDivisionError("division by zero")

        a_len = len(self._value)
        b_len = len(other._value)
        algo = self._choose_division(a_len, b_len)

        if algo == "school":
            return self._divide_school(self._value, other._value)
        elif algo == "burnikel":
            return self._divide_burnikel(self._value, other._value)
        else:
            return self._divide_barrett(self._value, other._value)

    def __neg__(self) -> "BigInt":
        result = BigInt(self)
        if result._value != "0":
            result._sign = "-" if result._sign == "" else ""
        return result

    def __pos__(self) -> "BigInt":
        return BigInt(self)

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
        """Целочисленный квадратный корень (floor sqrt)"""
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
