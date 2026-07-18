from langchain_core.tools import tool
from sympy import pi, E
from sympy.parsing.sympy_parser import parse_expr


@tool
def calculator(expression: str) -> str:
    """
    Safely evaluate mathematical expressions.
    Supports:
    + - * / ^ ** sqrt log sin cos tan factorial pi
    """

    expression = expression.strip()

    try:
        expression = expression.replace("^", "**")

        result = parse_expr(
            expression,
            local_dict={
                "pi": pi,
                "E": E,
            },
            evaluate=True,
        )

        return str(result)

    except Exception:
        return "Error: Please provide a valid mathematical expression."