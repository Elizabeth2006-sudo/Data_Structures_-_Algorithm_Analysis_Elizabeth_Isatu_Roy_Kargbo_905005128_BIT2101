"""
DCOMP320 - Data Structures and Algorithms
Assignment: Stacks Implementation (Version 3 - single-pass "term stack" method)

Idea:
  * A stack holds the TERMS that will be added together at the end.
  * '*' and '/' are applied immediately to the term on top of the stack,
    which gives them higher precedence than '+' and '-'.
  * '+' and '-' just push a new term (a '-' pushes the negated number).
  * When '(' is met, the current state is saved on a second stack, and a
    fresh term stack is started. At ')' the bracket is summed up and
    treated like a single number.
"""

import sys
from collections import deque


class Stack:
    """LIFO stack with push, pop and peek, backed by a deque."""

    def __init__(self):
        self._data = deque()

    def push(self, item):
        self._data.append(item)

    def pop(self):
        if not self._data:
            raise IndexError("pop from empty stack")
        return self._data.pop()

    def peek(self):
        if not self._data:
            raise IndexError("peek at empty stack")
        return self._data[-1]

    def is_empty(self):
        return len(self._data) == 0

    def size(self):
        return len(self._data)

    def total(self):
        """Empty the stack and return the sum of everything on it."""
        result = 0.0
        while not self.is_empty():
            result += self.pop()
        return result


class ExpressionEvaluator:
    """Evaluates one expression with a term stack and a bracket stack."""

    OPERATORS = "+-*/"

    def __init__(self, text):
        self.text = text
        self.pos = 0

    # ---- reading the text -------------------------------------------
    def _next_token(self):
        """Return the next token (float, operator char, bracket) or None."""
        t = self.text
        while self.pos < len(t) and t[self.pos].isspace():
            self.pos += 1
        if self.pos >= len(t):
            return None
        ch = t[self.pos]
        if ch.isdigit() or ch == ".":
            start = self.pos
            while self.pos < len(t) and (t[self.pos].isdigit() or t[self.pos] == "."):
                self.pos += 1
            piece = t[start:self.pos]
            if piece.count(".") > 1 or piece == ".":
                raise ValueError(f"invalid number '{piece}'")
            return float(piece)
        if ch in self.OPERATORS or ch in "()":
            self.pos += 1
            return ch
        raise ValueError(f"invalid character '{ch}'")

    # ---- applying an operator to a value ----------------------------
    @staticmethod
    def _apply(terms, op, value):
        if op == "+":
            terms.push(value)
        elif op == "-":
            terms.push(-value)
        elif op == "*":
            terms.push(terms.pop() * value)
        elif op == "/":
            if value == 0:
                raise ZeroDivisionError("division by zero")
            terms.push(terms.pop() / value)

    # ---- main algorithm ---------------------------------------------
    def evaluate(self):
        terms = Stack()          # terms of the bracket level we are in
        frames = Stack()         # saved (terms, operator, negative?) for '('
        op = "+"                 # operator waiting for its right-hand operand
        negative = False         # unary minus waiting for its operand
        need_operand = True      # True when a number or '(' must come next

        while True:
            tok = self._next_token()
            if tok is None:
                break
            if need_operand:
                if tok == "-":
                    negative = not negative
                elif tok == "+":
                    pass
                elif tok == "(":
                    frames.push((terms, op, negative))
                    terms, op, negative = Stack(), "+", False
                elif isinstance(tok, float):
                    self._apply(terms, op, -tok if negative else tok)
                    negative = False
                    need_operand = False
                else:
                    raise ValueError("invalid expression")
            else:
                if tok in self.OPERATORS:
                    op = tok
                    need_operand = True
                elif tok == ")":
                    if frames.is_empty():
                        raise ValueError("mismatched parentheses")
                    value = terms.total()
                    terms, op, negative = frames.pop()
                    self._apply(terms, op, -value if negative else value)
                    negative = False
                else:
                    raise ValueError("invalid expression")

        if need_operand:
            raise ValueError("invalid expression")
        if not frames.is_empty():
            raise ValueError("mismatched parentheses")
        return terms.total()


def evaluate(expression):
    return ExpressionEvaluator(expression).evaluate()


def format_result(value):
    if value == int(value):
        return str(int(value))
    return ("%.6f" % value).rstrip("0").rstrip(".")


def is_separator(line):
    s = line.strip()
    return len(s) >= 3 and set(s) == {"-"}


def process_file(input_path, output_path):
    """Evaluate every expression in input_path; keep separators as they are."""
    try:
        with open(input_path, "r") as src:
            lines = src.read().splitlines()
    except FileNotFoundError:
        print(f"Error: cannot find '{input_path}'")
        return None

    results = []
    for line in lines:
        if is_separator(line):
            results.append(line.strip())
        elif line.strip():
            try:
                results.append(format_result(evaluate(line)))
            except (ValueError, ZeroDivisionError) as err:
                results.append(f"Error: {err}")

    with open(output_path, "w") as dst:
        dst.write("\n".join(results) + "\n")
    return results


def main():
    in_file = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "output.txt"
    if process_file(in_file, out_file) is not None:
        print(f"Results written to {out_file}")


if __name__ == "__main__":
    main()
