import math
import argparse

def solve_quadratic(a, b, c):
    """Решает квадратное уравнение ax² + bx + c = 0"""
    if a == 0:
        if b == 0:
            return "Нет решений" if c != 0 else "Бесконечно много решений"
        return f"Линейное уравнение: x = {-c/b:.4f}"
    
    discriminant = b**2 - 4*a*c
    
    if discriminant < 0:
        return "Нет действительных решений"
    elif discriminant == 0:
        x = -b / (2*a)
        return f"Одно решение: x = {x:.4f}"
    else:
        sqrt_d = math.sqrt(discriminant)
        x1 = (-b + sqrt_d) / (2*a)
        x2 = (-b - sqrt_d) / (2*a)
        return f"Два решения: x1 = {x1:.4f}, x2 = {x2:.4f}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Решение квадратного уравнения")
    parser.add_argument("a", type=float, help="Коэффициент a")
    parser.add_argument("b", type=float, help="Коэффициент b")
    parser.add_argument("c", type=float, help="Коэффициент c")
    args = parser.parse_args()
    
    print(f"Уравнение: {args.a}x² + {args.b}x + {args.c} = 0")
    print(f"Ответ: {solve_quadratic(args.a, args.b, args.c)}")
