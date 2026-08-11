"""Safe AST arithmetic evaluation skill module."""

import ast
import operator
from collections.abc import Callable
from typing import Any

from doitall.models.tool_definition import ToolDefinition
from doitall.skills.base import BaseSkill

Number = int | float
BinaryOperator = Callable[[Number, Number], Number]
UnaryOperator = Callable[[Number], Number]

_BINARY_OPERATORS: dict[type[ast.operator], BinaryOperator] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}

_UNARY_OPERATORS: dict[type[ast.unaryop], UnaryOperator] = {
    ast.USub: operator.neg,
}


class CalculatorSkill(BaseSkill):
    """Safely evaluates simple arithmetic expressions."""

    name = "calculator"
    description = "Evaluate arithmetic expressions."

    @classmethod
    def definition(cls) -> ToolDefinition:
        """Return tool definition schema for calculator skill."""
        return ToolDefinition(
            name=cls.name,
            description=cls.description,
            input_schema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression.",
                    },
                },
                "required": [
                    "expression",
                ],
                "additionalProperties": False,
            },
        )

    async def execute(
        self,
        **kwargs: Any,
    ) -> float:
        """Evaluate an arithmetic expression."""
        expression = kwargs["expression"]

        if not isinstance(expression, str):
            raise ValueError("Expression must be a string.")

        tree = ast.parse(
            expression,
            mode="eval",
        )

        return self._evaluate(tree.body)

    def _evaluate(self, node: ast.expr) -> float:
        """Recursively evaluate a supported arithmetic AST node."""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(
                node.value,
                int | float,
            ):
                raise ValueError("Unsupported expression.")

            return float(node.value)

        if isinstance(node, ast.BinOp):
            binary_operator_type = type(node.op)
            binary_operator = _BINARY_OPERATORS.get(binary_operator_type)

            if binary_operator is None:
                raise ValueError("Unsupported expression.")

            left = self._evaluate(node.left)
            right = self._evaluate(node.right)

            return float(binary_operator(left, right))

        if isinstance(node, ast.UnaryOp):
            unary_operator_type = type(node.op)
            unary_operator = _UNARY_OPERATORS.get(unary_operator_type)

            if unary_operator is None:
                raise ValueError("Unsupported expression.")

            operand = self._evaluate(node.operand)

            return float(unary_operator(operand))

        raise ValueError("Unsupported expression.")
