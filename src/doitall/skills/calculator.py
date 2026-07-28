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
            return node.value

        if isinstance(node, ast.BinOp):
            return _OPERATORS[type(node.op)](
                self._evaluate(node.left),
                self._evaluate(node.right),
            )

        if isinstance(node, ast.UnaryOp):
            return _OPERATORS[type(node.op)](
                self._evaluate(node.operand),
            )

        raise ValueError("Unsupported expression.")
