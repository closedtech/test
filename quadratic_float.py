#!/usr/bin/env python3
"""Quadratic equation solver using BigFloat.

Solve: ax² + bx + c = 0

Supports high precision floating point roots.
"""

import sys
sys.path.insert(0, '/home/user/.openclaw/workspace')

from bigfloat import BigFloat


def solve_quadratic(a, b, c):
    """Solve quadratic equation ax² + bx + c = 0."""
    a = BigFloat(a)
    b = BigFloat(b)
    c = BigFloat(c)
    
    # Linear case
    if a == BigFloat(0):
        if b == BigFloat(0):
            return "бесконечно много решений" if c == BigFloat(0) else "нет решений"
        x = (-c) / b
        return f"линейное уравнение: x = {x}"
    
    # Discriminant
    D = b * b - BigFloat(4) * a * c
    
    # Two real roots
    if D > BigFloat(0):
        sqrt_D = D.sqrt()
        two_a = BigFloat(2) * a
        x1 = (-b + sqrt_D) / two_a
        x2 = (-b - sqrt_D) / two_a
        if x1 < x2:
            x1, x2 = x2, x1
        return f"два решения: x₁ = {x1}, x₂ = {x2}"
    
    # One double root
    if D == BigFloat(0):
        x = (-b) / (BigFloat(2) * a)
        return f"одно решение (два одинаковых): x = {x}"
    
    # Complex roots: D < 0
    sqrt_D = (-D).sqrt()
    two_a = BigFloat(2) * a
    real_part = (-b) / two_a
    imag_part = sqrt_D / two_a
    return f"комплексные корни: x₁ = {real_part} + {imag_part}i, x₂ = {real_part} - {imag_part}i"


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Solve ax² + bx + c = 0")
    parser.add_argument('a', help='Coefficient a')
    parser.add_argument('b', help='Coefficient b')
    parser.add_argument('c', help='Coefficient c')
    args = parser.parse_args()
    
    result = solve_quadratic(args.a, args.b, args.c)
    print(f"{args.a}x² + {args.b}x + {args.c} = 0")
    print(result)
