"""
Interpreter Pattern - Expression Calculator
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Union


class Context:
    """Stores variables for expression evaluation."""

    def __init__(self):
        self._variables: dict[str, int | float] = {}

    def set_variable(self, name: str, value: Union[int, float]) -> None:
        self._variables[name] = value

    def get_variable(self, name: str) -> Union[int, float]:
        if name not in self._variables:
            raise ValueError(f"Undefined variable: {name}")
        return self._variables[name]


class Expression(ABC):
    """Base class for all expressions."""

    @abstractmethod
    def interpret(self, context: Context) -> Union[int, float]:
        pass


class NumberExpression(Expression):
    """Represents a numeric literal."""

    def __init__(self, value: Union[int, float]):
        self.value = value

    def interpret(self, context: Context) -> Union[int, float]:
        return self.value


class VariableExpression(Expression):
    """Represents a variable reference."""

    def __init__(self, name: str):
        self.name = name

    def interpret(self, context: Context) -> Union[int, float]:
        return context.get_variable(self.name)


class AddExpression(Expression):
    """Addition expression: left + right."""

    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def interpret(self, context: Context) -> Union[int, float]:
        return self.left.interpret(context) + self.right.interpret(context)


class SubtractExpression(Expression):
    """Subtraction expression: left - right."""

    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def interpret(self, context: Context) -> Union[int, float]:
        return self.left.interpret(context) - self.right.interpret(context)


class MultiplyExpression(Expression):
    """Multiplication expression: left * right."""

    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def interpret(self, context: Context) -> Union[int, float]:
        return self.left.interpret(context) * self.right.interpret(context)


class DivideExpression(Expression):
    """Division expression: left / right."""

    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def interpret(self, context: Context) -> Union[int, float]:
        right_val = self.right.interpret(context)
        if right_val == 0:
            raise ZeroDivisionError("Division by zero")
        return self.left.interpret(context) / right_val


# Shorthand constructors
def Number(value: Union[int, float]) -> NumberExpression:
    return NumberExpression(value)


def Variable(name: str) -> VariableExpression:
    return VariableExpression(name)


def Add(left: Expression, right: Expression) -> AddExpression:
    return AddExpression(left, right)


def Subtract(left: Expression, right: Expression) -> SubtractExpression:
    return SubtractExpression(left, right)


def Multiply(left: Expression, right: Expression) -> MultiplyExpression:
    return MultiplyExpression(left, right)


def Divide(left: Expression, right: Expression) -> DivideExpression:
    return DivideExpression(left, right)


if __name__ == "__main__":
    # Example: Add(Number(3), Multiply(Number(2), Number(5))) → 13
    expression = Add(Number(3), Multiply(Number(2), Number(5)))
    context = Context()
    result = expression.interpret(context)
    print(f"Add(Number(3), Multiply(Number(2), Number(5))) = {result}")  # 13

    # Example with variables
    ctx = Context()
    ctx.set_variable("x", 10)
    ctx.set_variable("y", 5)

    expr = Multiply(Variable("x"), Add(Variable("y"), Number(3)))  # 10 * (5 + 3)
    print(f"x * (y + 3) = {expr.interpret(ctx)}")  # 80

    # Example with parentheses priority: (2 + 3) * (4 + 5)
    expr2 = Multiply(
        Add(Number(2), Number(3)),
        Add(Number(4), Number(5))
    )
    print(f"(2 + 3) * (4 + 5) = {expr2.interpret(Context())}")  # 45

    # Division example: 20 / (4 + 0) - handled, but 4 / 0 would raise
    expr3 = Divide(Number(20), Add(Number(4), Number(0)))
    try:
        print(f"20 / (4 + 0) = {expr3.interpret(Context())}")  # 5.0
    except ZeroDivisionError as e:
        print(f"Error: {e}")
