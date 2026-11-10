"""Рекурсивный спуск для логических условий: NOT > AND > OR, сравнения выше логики."""


class ConditionError(Exception):
    pass


class Node:
    def __init__(self, kind, **kwargs):
        self.kind = kind
        self.__dict__.update(kwargs)

    def __repr__(self):
        return f"Node({self.kind}, {self.__dict__})"


class Token:
    def __init__(self, type_, value, pos):
        self.type = type_
        self.value = value
        self.pos = pos

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


class ConditionParser:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.tokens = []
        self.tok_pos = 0

    def error(self, msg):
        raise ConditionError(f"{msg} at position {self.pos}")

    def tokenize(self):
        tokens = []
        i = 0
        text = self.text
        while i < len(text):
            ch = text[i]
            if ch in ' \t\n\r':
                i += 1
                continue
            if ch == '(':
                tokens.append(Token('LPAREN', ch, i)); i += 1; continue
            if ch == ')':
                tokens.append(Token('RPAREN', ch, i)); i += 1; continue
            if text[i:i+2] in ('==', '!=', '<=', '>='):
                tokens.append(Token('OP', text[i:i+2], i)); i += 2; continue
            if ch in '<>':
                tokens.append(Token('OP', ch, i)); i += 1; continue
            if ch.isalpha() or ch == '_':
                j = i
                while j < len(text) and (text[j].isalnum() or text[j] == '_'):
                    j += 1
                word = text[i:j]
                if word.upper() == 'AND':
                    tokens.append(Token('AND', word, i))
                elif word.upper() == 'OR':
                    tokens.append(Token('OR', word, i))
                elif word.upper() == 'NOT':
                    tokens.append(Token('NOT', word, i))
                else:
                    tokens.append(Token('IDENT', word, i))
                i = j
                continue
            if ch.isdigit():
                j = i
                while j < len(text) and (text[j].isdigit() or text[j] == '.'):
                    j += 1
                tokens.append(Token('NUM', text[i:j], i))
                i = j
                continue
            if ch in '"\'':
                quote = ch
                j = i + 1
                while j < len(text) and text[j] != quote:
                    j += 1
                if j >= len(text):
                    self.pos = i
                    self.error("Unterminated string in condition")
                tokens.append(Token('STR', text[i+1:j], i))
                i = j + 1
                continue
            self.pos = i
            self.error(f"Unexpected character {ch!r}")
        tokens.append(Token('EOF', '', i))
        return tokens

    def parse(self):
        self.tokens = self.tokenize()
        self.tok_pos = 0
        node = self.parse_or()
        if self.peek().type != 'EOF':
            self.pos = self.peek().pos
            self.error(f"Unexpected token {self.peek().value!r}")
        return node

    def peek(self):
        return self.tokens[self.tok_pos]

    def consume(self, type_=None):
        tok = self.tokens[self.tok_pos]
        if type_ and tok.type != type_:
            self.pos = tok.pos
            self.error(f"Expected {type_}, got {tok.type}")
        self.tok_pos += 1
        return tok

    def parse_or(self):
        left = self.parse_and()
        while self.peek().type == 'OR':
            self.consume()
            right = self.parse_and()
            left = Node('or', left=left, right=right)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.peek().type == 'AND':
            self.consume()
            right = self.parse_not()
            left = Node('and', left=left, right=right)
        return left

    def parse_not(self):
        if self.peek().type == 'NOT':
            self.consume()
            operand = self.parse_not()
            return Node('not', operand=operand)
        return self.parse_primary()

    def parse_primary(self):
        tok = self.peek()
        if tok.type == 'LPAREN':
            self.consume()
            node = self.parse_or()
            self.consume('RPAREN')
            return node
        if tok.type in ('IDENT', 'NUM', 'STR'):
            left = self.parse_operand()
            if self.peek().type == 'OP':
                op = self.consume().value
                right = self.parse_operand()
                return Node('compare', op=op, left=left, right=right)
            return left
        self.pos = tok.pos
        self.error(f"Unexpected token {tok.value!r}")

    def parse_operand(self):
        tok = self.peek()
        if tok.type == 'IDENT':
            self.consume()
            return Node('var', name=tok.value)
        if tok.type == 'NUM':
            self.consume()
            v = float(tok.value) if '.' in tok.value else int(tok.value)
            return Node('literal', value=v)
        if tok.type == 'STR':
            self.consume()
            return Node('literal', value=tok.value)
        self.pos = tok.pos
        self.error("Expected operand")


def render(node, parent_prec=0):
    """Разбор AST обратно в строку с расстановкой скобок по приоритетам."""
    if node.kind == 'or':
        s = f"{render(node.left, 1)} OR {render(node.right, 1)}"
        return f"({s})" if parent_prec > 1 else s
    if node.kind == 'and':
        s = f"{render(node.left, 2)} AND {render(node.right, 2)}"
        return f"({s})" if parent_prec > 2 else s
    if node.kind == 'not':
        s = f"NOT {render(node.operand, 3)}"
        return f"({s})" if parent_prec > 3 else s
    if node.kind == 'compare':
        s = f"{render(node.left, 4)} {node.op} {render(node.right, 4)}"
        return f"({s})" if parent_prec > 4 else s
    if node.kind == 'var':
        return node.name
    if node.kind == 'literal':
        return repr(node.value) if isinstance(node.value, str) else str(node.value)
    raise ValueError(f"Unknown node kind: {node.kind}")


def parse_condition(text):
    return ConditionParser(text).parse()