import pytest

from src.computation.expression_engine import ExpressionEngine, ExpressionError


@pytest.mark.parametrize(
    ("expression", "expected"),
    [("2 + 3", 5), ("2 * 3", 6), ("10 - 4", 6), ("20 / 5", 4), ("(2 + 3) * 4", 20)],
)
def test_evaluate(expression, expected):
    assert ExpressionEngine().evaluate(expression) == expected


def test_rejects_unsafe_expression():
    with pytest.raises(ExpressionError):
        ExpressionEngine().evaluate("__import__('os').system('echo unsafe')")


def test_decomposition_preserves_subtraction():
    tasks = ExpressionEngine().decompose("(12 * 5) + (30 / 6) - (8 * 4)")
    assert [(task.expression, task.sign) for task in tasks] == [
        ("12 * 5", 1),
        ("30 / 6", 1),
        ("8 * 4", -1),
    ]


def test_division_by_zero_is_explicit():
    with pytest.raises(ZeroDivisionError, match="Division by zero"):
        ExpressionEngine().evaluate("4 / 0")
