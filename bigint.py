"""BigInt - Arbitrary precision integer arithmetic in Python with FFT multiplication."""

import math


class BigInt:
    """Arbitrary precision integer using decimal string representation."""

    # Multiplication thresholds (digit count)
    SINGLE_DIGIT_THRESHOLD = 1
    KARATSUBA_THRESHOLD = 100
    FFT_THRESHOLD = 1000  # Use FFT for numbers > 1000 digits
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
        other = self._ensure_bigint(other)
        return self._mul(other)

    def __rmul__(self, other: "int") -> "BigInt":
        return self.__mul__(other)

    def _split_at(self, pos: int) -> tuple["BigInt", "BigInt"]:
        """Split number at digit position pos from right. Returns (high, low)."""
        if pos <= 0:
            return BigInt(0), BigInt(self._value)
        if pos >= len(self._value):
            return BigInt(self._value), BigInt(0)
        high = self._value[:-pos]
        low = self._value[-pos:]
        hi = BigInt.__new__(BigInt)
        hi._value = high.lstrip("0") or "0"
        hi._sign = ""
        lo = BigInt.__new__(BigInt)
        lo._value = low
        lo._sign = ""
        return hi, lo

    def _split_into_chunks(self, n: int) -> list["BigInt"]:
        """Split number into n equal chunks from least significant digits."""
        if n <= 0:
            raise ValueError("n must be positive")
        value = self._value
        pad_len = (n - len(value) % n) % n
        value = "0" * pad_len + value
        chunk_len = len(value) // n
        chunks = []
        for i in range(n):
            start = i * chunk_len
            chunk_str = value[start:start + chunk_len]
            chunk = BigInt.__new__(BigInt)
            chunk._value = chunk_str
            chunk._sign = ""
            chunks.append(chunk)
        return chunks

    def _multiply_single(self, other: "BigInt") -> "BigInt":
        """Multiply by single digit (O(n))."""
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

    def _mul(self, other: "BigInt") -> "BigInt":
        if self._value == "0" or other._value == "0":
            return BigInt(0)
        a_len = len(self._value)
        b_len = len(other._value)
        # Single digit multiplication (fast path)
        if a_len <= self.SINGLE_DIGIT_THRESHOLD or b_len <= self.SINGLE_DIGIT_THRESHOLD:
            return self._multiply_single(other)
        # School for small numbers (faster than Karatsuba for small n)
        if a_len < self.KARATSUBA_THRESHOLD and b_len < self.KARATSUBA_THRESHOLD:
            return self._multiply_school(other)
        # FFT for very large numbers
        if a_len + b_len > self.FFT_THRESHOLD:
            return self._multiply_fft(other)
        # Karatsuba for medium numbers
        return self._multiply_karatsuba(other)

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
        # Use the larger of dividend/divisor length for complexity
        n = max(a_len, b_len)
        if n < self.DIV_SCHOOL_THRESHOLD:
            return "school"
        elif n <= self.DIV_BURNIKEL_THRESHOLD:
            return "burnikel"
        else:
            return "newton"  # Newton best for very large numbers

    # ----- School division O(n2) -----
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

    # ----- Newton-Raphson division O(n log n) -----
    def _divide_newton(self, a_str: str, b_str: str) -> tuple["BigInt", "BigInt"]:
        """Divide a by b using Newton-Raphson for reciprocal.
        
        Uses the Newton-Raphson method to compute q = a // b and r = a % b.
        The key insight is that 1/b can be computed via Newton iteration on f(y) = 1/y - b.
        
        With proper scaling (R = base^M), y_n converges quadratically to R/b.
        After convergence, q = a * y // R gives the quotient.
        """
        if int(b_str) == 0:
            raise ZeroDivisionError("division by zero")

        # Work with absolute values — sign is handled by _divmod
        a_str_abs = a_str.lstrip("-+")
        b_str_abs = b_str.lstrip("-+")

        a_int = int(a_str_abs)
        b_int = int(b_str_abs)

        # Handle trivial case: |a| < |b|
        if len(a_str_abs) < len(b_str_abs) or (len(a_str_abs) == len(b_str_abs) and a_str_abs < b_str_abs):
            qi = BigInt.__new__(BigInt)
            qi._value = "0"
            qi._sign = ""
            ri = BigInt.__new__(BigInt)
            ri._value = a_str_abs.lstrip("0") or "0"
            ri._sign = ""
            return qi, ri

        # Use Python's native int for Newton-Raphson (fast C implementation)
        # R = 10^(len(b) + len(a)) gives enough precision
        # Actually use R = 10^(2 * len(b)) for safety
        k = len(str(b_int))
        R = 10 ** (2 * k)

        # Initial approximation y0 = R // b + 1 (always an overestimate)
        y = R // b_int + 1

        # Newton iteration: y_{n+1} = y * (2R - b*y) // R
        # This is derived from y_{n+1} = y * (2 - b*y) for finding 1/b,
        # scaled by R to work with integers.
        # Converges quadratically when y is close to R/b.
        prev_y = 0
        iterations = 0
        while y != prev_y and iterations < 50:
            prev_y = y
            # y * (2R - b*y) can be very large, but Python handles big ints
            y = y * (2 * R - b_int * y) // R
            iterations += 1

        # y is now an approximation to R/b
        # q_approx = a * y // R gives an approximation to a/b
        q_approx = a_int * y // R

        # Correct q_approx: compute remainder and adjust
        q_big = BigInt(str(abs(q_approx)))
        r = BigInt(a_str_abs) - q_big * BigInt(b_str_abs)

        # If remainder is negative, q was over-approximated
        while r < BigInt(0):
            q_big = q_big - BigInt(1)
            r = r + BigInt(b_str_abs)

        # If remainder >= b, q was under-approximated
        while r >= BigInt(b_str_abs):
            q_big = q_big + BigInt(1)
            r = r - BigInt(b_str_abs)

        return q_big, r

    # ----- Burnikel-Ziegler O(n log n) -----
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
        while len(digits) > 1 and digits[-1] == 0:
            digits.pop()
        return digits

    def _divide_burnikel(self, a_str: str, b_str: str) -> tuple["BigInt", "BigInt"]:
        """Burnikel-Ziegler division. Base 1000, recursive with school fallback.

        Key guarantee: at most ONE recursive call per level - no branching explosion.
        The algorithm splits a and b into j-word blocks where j = ceil(n_b / 2),
        then recursively divides the top blocks.
        """
        n = max(len(a_str), len(b_str))
        # Base case: use school for small inputs
        if n < 50:
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

        # Burnikel-Ziegler needs |a| >= 2*|b| for efficiency
        if len(a_str) < 2 * len(b_str):
            return self._divide_school(a_str, b_str)

        # Convert to base 1000
        a_base = self._str_to_base(a_str)
        b_base = self._str_to_base(b_str)

        n_a = len(a_base)
        n_b = len(b_base)

        # Burnikel-Ziegler requires n_b >= 2 for the recursive split to work
        # With n_b = 1, we don't have enough words for the 3-way split
        if n_b < 2:
            return self._divide_school(a_str, b_str)

        # j = ceil(n_b / 2) is the block size for the decomposition
        # a = a2*B^(2j) + a1*B^j + a0
        # b = b1*B^j + b0
        j = (n_b + 1) // 2  # ceil(n_b / 2)
        if j < 1:
            j = 1

        # Extract the top 2j words of a (these form a2 and a1)
        # a2 = top j words, a1 = next j words
        # Position from the end since a_base is little-endian
        a2_words = a_base[max(0, n_a - 2*j):n_a - j] if n_a >= j else []
        a1_words = a_base[n_a - j:n_a] if n_a >= j else a_base[:n_a]
        a0_words = a_base[:max(0, n_a - 2*j)] if n_a >= 2*j else []

        # b1 = top j words of b (b2 in standard notation)
        b1_words = b_base[max(0, n_b - j):n_b] if n_b >= j else []
        b0_words = b_base[:max(0, n_b - j)] if n_b >= j else b_base[:n_b]

        # Convert to strings
        a2_str = self._digits_to_base(a2_words).lstrip("0") or "0"
        a1_str = self._digits_to_base(a1_words).lstrip("0") or "0"
        b1_str = self._digits_to_base(b1_words).lstrip("0") or "0"
        b0_str = self._digits_to_base(b0_words).lstrip("0") or "0"

        # Handle empty or zero top word
        if a2_str == "0" or a2_str == "":
            return self._divide_school(a_str, b_str)

        if b1_str == "0" or b1_str == "":
            return self._divide_school(a_str, b_str)

        # The top word of a2 must be larger than top word of b1 for efficient recursion
        # Check: top_word(a2) >= 2 * top_word(b1)
        # In decimal: if len(a2_str) > len(b1_str), then top_word condition likely satisfied
        # If same length, compare values
        a2_len = len(a2_str)
        b1_len = len(b1_str)

        if a2_len < b1_len or (a2_len == b1_len and a2_str < b1_str):
            return self._divide_school(a_str, b_str)

        # Step 1: q1 = floor(a2 / b1), r1 = a2 - q1*b1
        # Use Burnikel recursively for this
        q1_big, _ = self._divide_burnikel(a2_str, b1_str)
        q1_str = q1_big._value.lstrip("0") or "0"

        if q1_str == "0":
            return self._divide_school(a_str, b_str)

        # Compute r1 = a2 - q1*b1 using BigInt
        q1_big_int = BigInt(q1_str)
        b1_big = BigInt(b1_str)
        r1_big = BigInt(a2_str) - q1_big_int * b1_big
        r1_str = r1_big._value.lstrip("0") or "0"
        if r1_str == "":
            r1_str = "0"

        # Step 2: Compute (r1*B^j + a1) / b
        # r1_shifted = r1 * B^j
        r1_shifted = r1_str + "0" * (3 * j)  # Each base-1000 word = 3 decimal digits
        # But we need to add a1 at the correct position
        # r1*B^j + a1 means concatenating a1 at the lower position
        r1_plus_a1 = self._str_to_base(r1_shifted)
        a1_base = self._str_to_base(a1_str)
        # Pad a1 to j words
        while len(a1_base) < j:
            a1_base.append(0)
        # Add a1 to r1_shifted at the lower j positions
        carry = 0
        for idx in range(len(a1_base)):
            pos = idx
            if pos < len(r1_plus_a1):
                sum_val = r1_plus_a1[pos] + a1_base[idx] + carry
            else:
                sum_val = a1_base[idx] + carry
            r1_plus_a1[pos] = sum_val % 1000
            carry = sum_val // 1000
        if carry:
            r1_plus_a1.append(carry)

        # Convert back to string and divide by b using school
        r1_plus_a1_str = self._digits_to_base(r1_plus_a1).lstrip("0") or "0"

        # Step 3: q2 = floor((r1*B^j + a1) / b), r2 = (r1*B^j + a1) - q2*b
        q2_big, r2_big = self._divide_school(r1_plus_a1_str, b_str)

        # Step 4: Final quotient q = q1 * B^j + q2
        B_j = 1000 ** j
        q1_int = int(q1_str)
        q2_int = int(q2_big._value.lstrip("0") or "0")
        q_int = q1_int * B_j + q2_int

        # Remainder from step 2 needs to be converted back
        # r2 is already in the correct form (it's the remainder of (r1*B^j + a1) / b)
        ri_str = r2_big._value.lstrip("0") or "0"

        qi = BigInt.__new__(BigInt)
        qi._value = str(q_int)
        qi._sign = ""
        ri = BigInt.__new__(BigInt)
        ri._value = ri_str
        ri._sign = ""
        return qi, ri

    # ----- Barrett reduction O(n log n) -----
    def _divide_barrett(self, a_str: str, b_str: str) -> tuple["BigInt", "BigInt"]:
        """Barrett division O(n log n).
        
        Algorithm:
        1. mu = B^(2n) / d  (precomputed)
        2. q_hat = floor(a_high * mu / B^(n+1))
        3. q = q_hat
        4. r = a - q * d
        5. Correct q and r
        
        Where B = 10, n = number of base-B digits in d
        """
        if int(b_str) == 0:
            raise ZeroDivisionError("division by zero")

        a_int = int(a_str)
        b_int = int(b_str)

        # Trivial case: |a| < |b|
        if abs(a_int) < abs(b_int):
            qi = BigInt.__new__(BigInt)
            qi._value = "0"
            qi._sign = ""
            ri = BigInt.__new__(BigInt)
            ri._value = str(abs(a_int))
            ri._sign = "-" if a_int < 0 else ""
            return qi, ri

        # Let B = 10, k = number of digits in b
        B = 10
        k = len(b_str)
        
        # mu = B^(2k) / b
        # For large b, this is huge, so we use the approximation:
        # We work in chunks of size 3 (base 1000)
        
        # Split a and b into base-BASE digits
        BASE = 1000
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
            ri._sign = "-" if a_int < 0 else ""
            return qi, ri

        # Compute mu = BASE^(2n) / b
        # Using integer arithmetic
        B_mu = BASE ** (2 * n)
        mu_hat = B_mu // b_int

        # First approximation: use top m+1 digits of a
        if len(a_digits) > n:
            a_top = sum(a_digits[i] * (BASE ** (len(a_digits) - i - 1)) for i in range(len(a_digits) - n - 1))
        else:
            a_top = sum(a_digits[i] * (BASE ** (len(a_digits) - i - 1)) for i in range(len(a_digits)))
        
        # q_hat = floor(a_top * mu_hat / BASE^(n+1))
        q_hat = (a_top * mu_hat) // (BASE ** (n + 1))
        
        # Clamp to reasonable range
        if q_hat > BASE ** (m + 2):
            q_hat = BASE ** (m + 2)
        
        # Correct q using multiplication
        q_int = q_hat
        max_corrections = 5
        
        for _ in range(max_corrections):
            # q * b
            q_b = q_int * b_int
            
            if q_b > a_int:
                q_int -= 1
            elif q_b < a_int - b_int:
                # Can we increase q?
                room = (a_int - q_b) // b_int
                if room > 0:
                    q_int += min(room, BASE - 1)
                else:
                    break
            else:
                break
        
        r_int = a_int - q_int * b_int
        
        # Ensure remainder is in [0, b)
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
        ri._sign = "-" if a_int < 0 else ""
        
        return qi, ri

    def _divmod(self, other: "BigInt") -> tuple["BigInt", "BigInt"]:
        """Integer division and modulo: returns (quotient, remainder).
        
        Python semantics: a = b*(a//b) + (a%b), 0 <= r < |b| for positive b
        """
        if other._value == "0":
            raise ZeroDivisionError("division by zero")

        a_abs = int(self._value.lstrip("-"))
        b_abs = int(other._value.lstrip("-"))
        
        a_neg = self._sign == "-"
        b_neg = other._sign == "-"
        
        # Floor division
        q_abs = a_abs // b_abs
        r_abs = a_abs % b_abs
        
        # Floor rule: when signs differ and r != 0, q is more negative
        if a_neg != b_neg and r_abs != 0:
            q_abs = -(q_abs + 1)
            r_abs = b_abs - r_abs
        
        # Quotient sign
        q_sign = "-" if ((a_neg != b_neg and r_abs != 0) or (a_neg and b_neg)) else ""
        if a_neg and not b_neg:
            q_sign = "-"
        elif not a_neg and b_neg:
            q_sign = "-"
        
        q = BigInt.__new__(BigInt)
        q._value = str(abs(q_abs))
        q._sign = q_sign
        
        # Remainder: sign follows divisor when divisor negative, else positive
        # For floor division: 0 <= r < |b|
        r = BigInt.__new__(BigInt)
        r._value = str(r_abs)
        r._sign = ""  # floor division: remainder always non-negative

        return q, r
    def __neg__(self) -> "BigInt":
        result = BigInt.__new__(BigInt)
        result._value = self._value
        result._sign = "-" if self._sign == "" else ""
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
