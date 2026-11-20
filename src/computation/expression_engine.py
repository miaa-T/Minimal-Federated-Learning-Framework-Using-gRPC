import ast
from dataclasses import dataclass


class ExpressionError(ValueError):
    """Raised when an arithmetic expression is invalid or unsafe."""


@dataclass(frozen=True)
class ExpressionTask:
    expression: str
    position: int
    sign: int


class ExpressionEngine:
    """Parse, validate, decompose, and safely evaluate arithmetic expressions."""

    _binary_operators = (ast.Add, ast.Sub, ast.Mult, ast.Div)
    _unary_operators = (ast.UAdd, ast.USub)

    def parse(self, expression: str) -> ast.Expression:
        if not expression or not expression.strip():
            raise ExpressionError("Expression must not be empty")
        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as exc:
            raise ExpressionError(f"Invalid expression: {exc.msg}") from exc
        self._validate(tree.body)
        return tree

    def evaluate(self, expression: str) -> int | float:
        tree = self.parse(expression)
        return self._evaluate_node(tree.body)

    def decompose(self, expression: str) -> list[ExpressionTask]:
        tree = self.parse(expression)
        terms: list[tuple[ast.AST, int]] = []
        self._collect_additive_terms(tree.body, 1, terms)
        return [
            ExpressionTask(
                expression=ast.unparse(node),
                position=position,
                sign=sign,
            )
            for position, (node, sign) in enumerate(terms, start=1)
        ]

    def _validate(self, node: ast.AST) -> None:
        if isinstance(node, ast.BinOp):
            if not isinstance(node.op, self._binary_operators):
                raise ExpressionError("Only +, -, *, and / are supported")
            self._validate(node.left)
            self._validate(node.right)
            return
        if isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, self._unary_operators):
                raise ExpressionError("Only unary + and - are supported")
            self._validate(node.operand)
            return
        if isinstance(node, ast.Constant) and (
            isinstance(node.value, (int, float)) and not isinstance(node.value, bool)
        ):
            return
        raise ExpressionError("Expression contains an unsupported value or operation")

    def _evaluate_node(self, node: ast.AST) -> int | float:
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.UnaryOp):
            value = self._evaluate_node(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp):
            left = self._evaluate_node(node.left)
            right = self._evaluate_node(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if right == 0:
                raise ZeroDivisionError("Division by zero is not allowed")
            return left / right
        raise ExpressionError("Expression contains an unsupported value or operation")

    def _collect_additive_terms(
        self, node: ast.AST, sign: int, terms: list[tuple[ast.AST, int]]
    ) -> None:
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            self._collect_additive_terms(node.left, sign, terms)
            self._collect_additive_terms(node.right, sign, terms)
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Sub):
            self._collect_additive_terms(node.left, sign, terms)
            self._collect_additive_terms(node.right, -sign, terms)
        else:
            terms.append((node, sign))
