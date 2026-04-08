"""BigInt - Arbitrary precision integer arithmetic in Python."""


class BigInt:
    """Arbitrary precision integer using decimal string representation."""

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

    def _abs(self) -> "BigInt":
        """Return absolute value."""
        result = BigInt(self)
        result._sign = ""
        return result

    def _ensure_bigint(self, other: "int | BigInt") -> "BigInt":
        """Convert int to BigInt."""
        if isinstance(other, BigInt):
            return other
        if isinstance(other, int):
            return BigInt(other)
        raise TypeError(f"Cannot operate with {type(other).__name__}")

    def __repr__(self) -> str:
        return f"BigInt('{self._sign}{self._value}')"

    def to_string(self) -> str:
        """Convert BigInt back to string."""
        return f"{self._sign}{self._value}"

    # Comparison operators
    def _compare(self, other: "BigInt") -> int:
        """Compare two BigInts. Returns -1, 0, 1."""
        if self._sign != other._sign:
            return -1 if self._sign == "-" else 1

        cmp = 0
        if len(self._value) != len(other._value):
            cmp = -1 if len(self._value) < len(other._value) else 1
        else:
            cmp = -1 if self._value < other._value else (1 if self._value > other._value else 0)

        if self._sign == "-":
            cmp = -cmp
        return cmp

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

    # Arithmetic operations
    def __add__(self, other: "int | BigInt") -> "BigInt":
        other = self._ensure_bigint(other)
        return self._add(other)

    def __radd__(self, other: "int") -> "BigInt":
        return self.__add__(other)

    def _add(self, other: "BigInt") -> "BigInt":
        """Internal addition."""
        if self._sign == other._sign:
            result = BigInt(self)
            result._value = self._add_abs(other._value)
            return result

        # Different signs - subtract
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
        """Add two positive digit strings (big-endian)."""
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
        """Compare absolute values. Returns -1, 0, 1."""
        if len(self._value) != len(other._value):
            return -1 if len(self._value) < len(other._value) else 1
        if self._value < other._value:
            return -1
        if self._value > other._value:
            return 1
        return 0

    def __sub__(self, other: "int | BigInt") -> "BigInt":
        other = self._ensure_bigint(other)
        return self._sub(other)

    def __rsub__(self, other: "int") -> "BigInt":
        other = BigInt(other)
        return other._sub(self)

    def _sub(self, other: "BigInt") -> "BigInt":
        """Internal subtraction: self - other."""
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
        """Subtract digit strings: self._value - b (assumes self >= b in absolute value)."""
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

    def __mul__(self, other: "int | BigInt") -> "BigInt":
        other = self._ensure_bigint(other)
        return self._mul(other)

    def __rmul__(self, other: "int") -> "BigInt":
        return self.__mul__(other)

    def _mul(self, other: "BigInt") -> "BigInt":
        """Multiply two BigInts using grade-school algorithm."""
        if self._value == "0" or other._value == "0":
            return BigInt(0)

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

        # Convert to string, skip leading zeros
        start = 0
        while start < len(result) - 1 and result[start] == 0:
            start += 1

        value_str = "".join(str(d) for d in result[start:])
        sign = "-" if self._sign != other._sign else ""
        bi = BigInt.__new__(BigInt)
        bi._value = value_str
        bi._sign = sign
        return bi

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

    def _divmod(self, other: "BigInt") -> tuple["BigInt", "BigInt"]:
        """Integer division and modulo: returns (quotient, remainder)."""
        if other._value == "0":
            raise ZeroDivisionError("division by zero")

        if self._compare_abs(other) < 0:
            return (BigInt(0), BigInt(self))

        a = self._value
        b = other._value
        quotient = []
        current = ""

        for digit in a:
            current += digit
            current_stripped = current.lstrip("0") or "0"
            b_stripped = b.lstrip("0") or "0"

            # Count how many times b fits in current
            q = 0
            while len(current_stripped) > len(b_stripped) or (
                len(current_stripped) == len(b_stripped) and current_stripped >= b_stripped
            ):
                current = str(int(current) - int(b))
                q += 1
                current_stripped = current.lstrip("0") or "0"
                b_stripped = b.lstrip("0") or "0"

            quotient.append(str(q))

        quotient_str = "".join(quotient).lstrip("0") or "0"
        remainder_str = current.lstrip("0") or "0"

        sign_q = "-" if self._sign != other._sign else ""
        sign_r = self._sign if self._sign else ""

        qi = BigInt.__new__(BigInt)
        qi._value = quotient_str
        qi._sign = sign_q

        ri = BigInt.__new__(BigInt)
        ri._value = remainder_str
        ri._sign = sign_r

        return (qi, ri)

    def __neg__(self) -> "BigInt":
        result = BigInt(self)
        if result._value != "0":
            result._sign = "-" if result._sign == "" else ""
        return result

    def __pos__(self) -> "BigInt":
        return BigInt(self)
