import ast
import operator
import re


class CalculatorTool:

    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv
    }

    def execute(self, question):

        expression = re.sub(
            r"(?i)what is",
            "",
            question
        )

        expression = expression.replace("?", "").strip()

        try:
            result = self._evaluate(expression)

            return {
                "answer": str(result),
                "sources": []
            }

        except Exception:
            return {
                "answer": "Unable to calculate the expression.",
                "sources": []
            }

    def _evaluate(self, expression):

        tree = ast.parse(
            expression,
            mode="eval"
        )

        return self._evaluate_node(tree.body)

    def _evaluate_node(self, node):

        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, (int, float))
            and not isinstance(node.value, bool)
        ):
            return node.value

        if isinstance(node, ast.BinOp):

            operator_function = self.OPERATORS.get(
                type(node.op)
            )

            if not operator_function:
                raise ValueError("Unsupported operator")

            return operator_function(
                self._evaluate_node(node.left),
                self._evaluate_node(node.right)
            )

        raise ValueError("Unsupported expression")
