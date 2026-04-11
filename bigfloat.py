"""BigFloat - Arbitrary precision floating point arithmetic."""

import math

BASE = 10**9
BASE_DIGITS = 9


class BigFloat:
    __slots__ = ('digits', 'exp', 'sign')

    SCHOOL_THRESHOLD = 100
    KARATSUBA_THRESHOLD = 1000
    TOOM3_THRESHOLD = 2000
    DIV_SCHOOL_THRESHOLD = 100

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
            self.exp = len(self.digits) - 1

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
        
        s = f"{value:.15g}"
        self._from_str(s)

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
            exp_offset = int(exp_part)
            if '.' in base_part:
                int_part, frac_part = base_part.split('.')
                frac_part = frac_part.rstrip('0')
                exp_offset -= len(frac_part)
                value = int_part + frac_part
            else:
                value = base_part
        elif '.' in value:
            int_part, frac_part = value.split('.')
            frac_part = frac_part.rstrip('0')
            exp_offset = -len(frac_part)
            value = int_part + frac_part
        else:
            exp_offset = 0
        
        value = value.lstrip('0') or '0'
        
        # Parse digits in chunks of BASE_DIGITS from right to left
        # No reversal needed - we read chunks left-to-right as we go rightward
        self.digits = []
        for i in range(0, len(value), BASE_DIGITS):
            end_idx = len(value) - i
            start_idx = max(0, end_idx - BASE_DIGITS)
            chunk = value[start_idx:end_idx]
            if chunk:
                self.digits.append(int(chunk))
        
        if not self.digits:
            self.digits = [0]
            self.exp = 0
        else:
            # exp is the index of most significant digit (0 = one's place)
            self.exp = len(self.digits) - 1 + exp_offset

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
        if self.exp != other.exp:
            return -1 if self.exp < other.exp else 1
        for i in range(len(self.digits) - 1, -1, -1):
            j = len(other.digits) - 1 - i
            if j < 0 or j >= len(other.digits):
                return 1 if i < len(self.digits) else -1
            if self.digits[i] != other.digits[j]:
                return -1 if self.digits[i] < other.digits[j] else 1
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

    def _align_exp(self, other: "BigFloat"):
        """Align exponents for addition/subtraction.
        
        Returns two BigFloats with equal exponents, ready for digit-by-digit
        addition or subtraction. Handles fractional numbers correctly by
        scaling to common precision.
        """
        if self.exp == other.exp:
            return self._copy(), other._copy()
        
        a = self._copy()
        b = other._copy()
        
        # Handle fractional alignment: when exponents differ and one is negative
        # Use scaled integer representation to align properly
        
        if a.exp < 0 or b.exp < 0:
            # At least one has fractional part
            # Find the common exponent (minimum of the two)
            min_exp = min(a.exp, b.exp)
            
            # Determine how many decimal digits we need to preserve
            # This ensures we don't lose fractional precision
            scale_a = 1 - a.exp if a.exp < 0 else 1
            scale_b = 1 - b.exp if b.exp < 0 else 1
            max_scale = max(scale_a, scale_b)
            
            # Convert both to scaled integers
            def to_scaled_int(bf, target_scale):
                # Build full digit string
                all_digits = ''.join(f"{d:09d}" for d in reversed(bf.digits))
                decimal_pos = len(all_digits) + bf.exp
                
                if decimal_pos <= 0:
                    # Number < 1
                    frac_len = -decimal_pos
                    int_part = '0'
                    frac_part = ('0' * frac_len + all_digits.lstrip('0'))[:target_scale]
                elif decimal_pos >= len(all_digits):
                    # Number is integer with possible trailing zeros
                    int_part = all_digits + '0' * (decimal_pos - len(all_digits))
                    frac_part = ''
                else:
                    # Number has both integer and fractional parts
                    int_part = all_digits[:decimal_pos]
                    frac_part = all_digits[decimal_pos:].ljust(target_scale, '0')[:target_scale]
                
                return int(int_part + frac_part.ljust(target_scale, '0'))
            
            a_scaled = to_scaled_int(a, max_scale)
            b_scaled = to_scaled_int(b, max_scale)
            
            # Create result BigFloats with aligned exponents
            new_a = BigFloat.__new__(BigFloat)
            new_b = BigFloat.__new__(BigFloat)
            
            # Store scaled values with exp = len(scaled_str) - max_scale - 1
            # This puts the decimal at the right place
            a_str = str(a_scaled)
            b_str = str(b_scaled)
            
            new_a.digits = []
            for i in range(0, len(a_str), 9):
                chunk = a_str[max(0, len(a_str) - i - 9):len(a_str) - i]
                if chunk:
                    new_a.digits.append(int(chunk))
            new_a.exp = len(new_a.digits) - 1 - max_scale
            new_a.sign = a.sign
            
            new_b.digits = []
            for i in range(0, len(b_str), 9):
                chunk = b_str[max(0, len(b_str) - i - 9):len(b_str) - i]
                if chunk:
                    new_b.digits.append(int(chunk))
            new_b.exp = len(new_b.digits) - 1 - max_scale
            new_b.sign = b.sign
            
            new_a._normalize()
            new_b._normalize()
            return new_a, new_b
        
        # Original logic for non-fractional numbers
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

    def _mul_karatsuba(self, other: "BigFloat") -> "BigFloat":
        if self._is_zero() or other._is_zero():
            return BigFloat(0)
        n = max(len(self.digits), len(other.digits))
        if n < self.KARATSUBA_THRESHOLD // BASE_DIGITS:
            return self._mul_school(other)
        half = n // 2
        a1 = self.digits[half:] if len(self.digits) > half else [0]
        a0 = self.digits[:half] if len(self.digits) > half else self.digits
        b1 = other.digits[half:] if len(other.digits) > half else [0]
        b0 = other.digits[:half] if len(other.digits) > half else other.digits
        max_len = max(len(a0), len(b0))
        a0.extend([0] * (max_len - len(a0)))
        b0.extend([0] * (max_len - len(b0)))
        z0 = self._mul_digits(a0, b0)
        z2 = self._mul_digits(a1, b1)
        a_sum = [(a0[i] + (a1[i] if i < len(a1) else 0)) for i in range(max_len)]
        b_sum = [(b0[i] + (b1[i] if i < len(b1) else 0)) for i in range(max_len)]
        z1 = self._mul_digits(a_sum, b_sum)
        z1 = [z1[i] - z0[i] - (z2[i] if i < len(z2) else 0) for i in range(len(z1))]
        result = [0] * (n * 2)
        for i, v in enumerate(z0):
            if i < len(result):
                result[i] += v
        for i, v in enumerate(z1):
            if i + half < len(result):
                result[i + half] += v
        for i, v in enumerate(z2):
            if i + half * 2 < len(result):
                result[i + half * 2] += v
        out = BigFloat.__new__(BigFloat)
        out.digits = result
        out.exp = self.exp + other.exp
        out.sign = self.sign * other.sign
        out._normalize()
        return out

    def _mul_digits(self, a: list, b: list) -> list:
        n, m = len(a), len(b)
        result = [0] * (n + m)
        for i in range(n):
            for j in range(m):
                result[i + j] += a[i] * b[j]
        for i in range(len(result) - 1, -1, -1):
            if result[i] >= BASE:
                carry = result[i] // BASE
                result[i] %= BASE
                if i + 1 < len(result):
                    result[i + 1] += carry
        while len(result) > 1 and result[-1] == 0:
            result.pop()
        return result

    def _mul_fft(self, other: "BigFloat") -> "BigFloat":
        import math
        if self._is_zero() or other._is_zero():
            return BigFloat(0)
        a_digits = []
        for d in self.digits:
            for _ in range(BASE_DIGITS // 4):
                a_digits.append(d % 32768)
                d //= 32768
        b_digits = []
        for d in other.digits:
            for _ in range(BASE_DIGITS // 4):
                b_digits.append(d % 32768)
                d //= 32768
        n = 1
        while n < len(a_digits) + len(b_digits):
            n *= 2
        a_digits.extend([0] * (n - len(a_digits)))
        b_digits.extend([0] * (n - len(b_digits)))
        def fft(a, invert):
            n = len(a)
            j = 0
            for i in range(1, n):
                bit = n >> 1
                while j & bit:
                    j ^= bit
                    bit >>= 1
                j ^= bit
                if i < j:
                    a[i], a[j] = a[j], a[i]
            length = 2
            while length <= n:
                angle = -2 * math.pi / length * (-1 if invert else 1)
                wlen = complex(math.cos(angle), math.sin(angle))
                for i in range(0, n, length):
                    w = 1
                    for j in range(i, i + length // 2):
                        u = a[j]
                        v = a[j + length // 2] * w
                        a[j] = u + v
                        a[j + length // 2] = u - v
                        w *= wlen
                length *= 2
            if invert:
                for i in range(n):
                    a[i] /= n
            return a
        af = [complex(x, 0) for x in a_digits]
        bf = [complex(x, 0) for x in b_digits]
        fft(af, False)
        fft(bf, False)
        cf = [af[i] * bf[i] for i in range(n)]
        fft(cf, True)
        result = [0] * (n + 1)
        carry = 0
        for i in range(n):
            val = int(cf[i].real + 0.5) + carry
            result[i] = val % 32768
            carry = val // 32768
        result[n] = carry
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
        if total < self.SCHOOL_THRESHOLD // BASE_DIGITS:
            return self._mul_school(other)
        elif total < self.KARATSUBA_THRESHOLD // BASE_DIGITS:
            return self._mul_karatsuba(other)
        else:
            return self._mul_fft(other)

    def _div_school(self, other: "BigFloat") -> "BigFloat":
        if other._is_zero():
            raise ZeroDivisionError("division by zero")
        if self._is_zero():
            return BigFloat(0)
        
        # Use string representation to get correct value including fractional part
        # This avoids issues with exponent reconstruction
        a_str = str(self)
        b_str = str(other)
        
        # Parse both to scaled integers (15 decimal places)
        num_frac = 15
        
        def parse_to_scaled(s):
            s = s.strip()
            negative = s.startswith('-')
            if negative:
                s = s[1:]
            
            if '.' in s:
                int_part, frac_part = s.split('.')
                frac_part = (frac_part + '0' * num_frac)[:num_frac]
            else:
                int_part = s
                frac_part = '0' * num_frac
            
            return int(int_part + frac_part), negative
        
        a_scaled, a_neg = parse_to_scaled(a_str)
        b_scaled, b_neg = parse_to_scaled(b_str)
        
        if b_scaled == 0:
            raise ZeroDivisionError("division by zero")
        
        # Perform division: a_scaled / b_scaled
        result_scaled = (a_scaled * (10 ** num_frac)) // b_scaled
        
        # Determine sign
        result_sign = -1 if a_neg != b_neg else 1
        
        # Convert result_scaled back to BigFloat
        result_str = str(result_scaled)
        
        # Split into int and frac parts
        if len(result_str) > num_frac:
            int_str = result_str[:-num_frac]
            frac_str = result_str[-num_frac:].rstrip('0')
        else:
            int_str = "0"
            frac_str = result_str.rjust(num_frac, '0').rstrip('0')
        
        # Combine
        combined = int_str + frac_str
        
        # Build BASE digits
        digits = []
        for i in range(0, len(combined), 9):
            end_idx = len(combined) - i
            start_idx = max(0, end_idx - 9)
            chunk = combined[start_idx:end_idx]
            if chunk:
                digits.append(int(chunk))
        
        if not digits:
            digits = [0]
        
        # Calculate exponent
        exp = len(int_str) - len(combined)
        
        result = BigFloat.__new__(BigFloat)
        result.digits = digits
        result.exp = exp
        result.sign = result_sign
        result._normalize()
        
        return result

    def __truediv__(self, other) -> "BigFloat":
        if not isinstance(other, BigFloat):
            other = BigFloat(other)
        if other._is_zero():
            raise ZeroDivisionError("division by zero")
        if self._is_zero():
            return BigFloat(0)
        return self._div_school(other)

    def sqrt(self) -> "BigFloat":
        """Square root using Newton-Raphson."""
        if self.sign < 0:
            raise ValueError("sqrt of negative number")
        if self._is_zero():
            return BigFloat(0)
        # Use high precision float for initial approximation
        approx = float(str(self))
        x = BigFloat(str(math.sqrt(approx)))
        # Newton-Raphson: x_{n+1} = (x + n/x) / 2
        for _ in range(100):
            x2 = x * x
            diff = x2 - self
            # Check if x^2 is close enough to self
            if abs(diff) < abs(self) * BigFloat("1e-100"):
                break
            x = (x + self / x) / BigFloat(2)
        return x

    def __repr__(self) -> str:
        return f"BigFloat(digits={self.digits}, exp={self.exp}, sign={self.sign})"

    def __str__(self) -> str:
        if self._is_zero():
            return "0"
        # Build all digits
        all_digits = ''.join(f"{d:09d}" for d in reversed(self.digits)).lstrip('0')
        if not all_digits:
            all_digits = '0'
        # Position decimal point
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
    
    # Core
    print("\n--- Core ---")
    assert BigFloat(123).digits == [123]
    assert str(BigFloat(-456)) == "-456"
    print("Core: OK")
    
    # Float parsing
    print("\n--- Float parsing ---")
    assert str(BigFloat("1.5")) == "1.5", f"got {BigFloat('1.5')}"
    assert str(BigFloat("0.001")) == "0.001", f"got {BigFloat('0.001')}"
    print("Float parsing: OK")
    
    # Operations
    print("\n--- Operations ---")
    assert str(BigFloat(5) + BigFloat(3)) == "8"
    assert str(BigFloat(5) - BigFloat(3)) == "2"
    assert str(BigFloat(5) * BigFloat(3)) == "15"
    assert str(BigFloat(15) / BigFloat(3)) == "5"
    print("Operations: OK")
    
    # Square root
    print("\n--- Square Root ---")
    assert str(BigFloat(4).sqrt()) == "2"
    assert str(BigFloat(16).sqrt()) == "4"
    assert str(BigFloat(100).sqrt()) == "10"
    print("Square root: OK")
    
    # Quadratic
    print("\n--- Quadratic ---")
    a, b, c = BigFloat(1), BigFloat(-5), BigFloat(6)
    D = b * b - BigFloat(4) * a * c
    sqrt_D = D.sqrt()
    two_a = BigFloat(2) * a
    x1 = (-b + sqrt_D) / two_a
    x2 = (-b - sqrt_D) / two_a
    assert str(x1) == "3", f"x1 = {x1}"
    assert str(x2) == "2", f"x2 = {x2}"
    print("Quadratic (x²-5x+6=0): x1=3, x2=2 OK")
    
    print("\n=== All tests passed! ===")
