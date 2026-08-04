"""Safe AST arithmetic evaluation skill module."""

import ast
import operator

from doitall.models.tool_definition import ToolDefinition
from doitall.skills.base import BaseSkill

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
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
        *,
        expression: str,
    ) -> float:
        """Evaluate an arithmetic expression."""

        tree = ast.parse(
            expression,
            mode="eval",
        )

        return self._evaluate(tree.body)

    def _evaluate(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, int | float):
                raise ValueError("Unsupported expression.")

            return node.value

        if isinstance(node, ast.BinOp):
            operator_type = type(node.op)
            if operator_type not in _OPERATORS:
                raise ValueError("Unsupported expression.")

            return _OPERATORS[operator_type](
                self._evaluate(node.left),
                self._evaluate(node.right),
            )

        if isinstance(node, ast.UnaryOp):
            operator_type = type(node.op)
            if operator_type not in _OPERATORS:
                raise ValueError("Unsupported expression.")

            return _OPERATORS[operator_type](
                self._evaluate(node.operand),
            )

        raise ValueError("Unsupported expression.")
