import math
import cmath

def solve_quadratic(a, b, c):
    """Решает квадратное уравнение ax² + bx + c = 0"""
    if a == 0:
        if b == 0:
            return "Нет решений" if c != 0 else "Бесконечно много решений"
        return f"Линейное уравнение: x = {-c/b:.4f}"
    
    discriminant = b**2 - 4*a*c
    
    if discriminant < 0:
        # Комплексные корни
        z1 = (-b + cmath.sqrt(discriminant)) / (2*a)
        z2 = (-b - cmath.sqrt(discriminant)) / (2*a)
        return f"Комплексные корни: x1 = {z1:.4f}, x2 = {z2:.4f}"
    elif discriminant == 0:
        x = -b / (2*a)
        return f"Одно решение: x = {x:.4f}"
    else:
        sqrt_d = math.sqrt(discriminant)
        x1 = (-b + sqrt_d) / (2*a)
        x2 = (-b - sqrt_d) / (2*a)
        return f"Два решения: x1 = {x1:.4f}, x2 = {x2:.4f}"

if __name__ == "__main__":
    print("=== Решение квадратного уравнения ===")
    print("Введите коэффициенты a, b, c:")
    
    a = float(input("a = "))
    b = float(input("b = "))
    c = float(input("c = "))
    
    print(f"\nУравнение: {a}x² + {b}x + {c} = 0")
    print(f"Ответ: {solve_quadratic(a, b, c)}")
