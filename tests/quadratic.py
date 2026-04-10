import math
import cmath
import argparse
from bigint import BigInt

def solve_quadratic(a: str, b: str, c: str):
    """
    Решает квадратное уравнение ax² + bx + c = 0
    Все параметры — строки (для работы с BigInt произвольной точности).
    
    Returns:
        str: описание решения
    """
    a = BigInt(a)
    b = BigInt(b)
    c = BigInt(c)
    
    # Случай: линейное уравнение (a = 0)
    if a == BigInt(0):
        if b == BigInt(0):
            if c == BigInt(0):
                return "Бесконечно много решений"
            return "Нет решений"
        # bx + c = 0  →  x = -c/b
        x = c / b * BigInt(-1)
        return f"Линейное уравнение: x = {x.to_string()}"
    
    # discriminant = b² - 4ac
    b_squared = b * b
    four_ac = BigInt(4) * a * c
    discriminant = b_squared - four_ac
    
    # Проверяем знак дискриминанта
    zero = BigInt(0)
    
    if discriminant < zero:
        # Отрицательный дискриминант → комплексные корни
        discriminant_abs = zero - discriminant
        
        # √|D| = √(4ac - b²)
        sqrt_abs = discriminant_abs.sqrt()
        
        # x = (-b ± i√|D|) / 2a
        two_a = a * BigInt(2)
        real_part = b * BigInt(-1) / two_a
        imag_part = sqrt_abs / two_a
        
        return (f"Комплексные корни: "
                f"x₁ = {real_part.to_string()} + {imag_part.to_string()}i, "
                f"x₂ = {real_part.to_string()} - {imag_part.to_string()}i")
    
    elif discriminant == zero:
        # Один корень: x = -b / 2a
        x = b * BigInt(-1) / (a * BigInt(2))
        return f"Одно решение: x = {x.to_string()}"
    
    else:
        # Два вещественных корня
        sqrt_d = discriminant.sqrt()
        two_a = a * BigInt(2)
        
        x1 = (b * BigInt(-1) + sqrt_d) / two_a
        x2 = (b * BigInt(-1) - sqrt_d) / two_a
        
        return f"Два решения: x₁ = {x1.to_string()}, x₂ = {x2.to_string()}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Решение квадратного уравнения (BigInt)")
    parser.add_argument("a", help="Коэффициент a")
    parser.add_argument("b", help="Коэффициент b")
    parser.add_argument("c", help="Коэффициент c")
    args = parser.parse_args()
    
    print(f"Уравнение: ({args.a})x² + ({args.b})x + ({args.c}) = 0")
    print(f"Ответ: {solve_quadratic(args.a, args.b, args.c)}")
