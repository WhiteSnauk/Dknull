"""Собственный JSON-парсер с глубиной, escape-последовательностями и позициями ошибок."""

import sys

MAX_DEPTH = 512

# Каждый уровень вложенности (объект/массив) добавляет ~2 кадра стека:
# parse_array() → parse_value() → parse_array() → ...
# Дефолтный лимит рекурсии Python (1000) меньше, чем нужно даже для
# MAX_DEPTH=512 (~1026 кадров). Поднимаем лимит с запасом, чтобы наша
# проверка глубины срабатывала раньше, чем переполнение стека.
_REQUIRED_LIMIT = MAX_DEPTH * 4 + 500
if sys.getrecursionlimit() < _REQUIRED_LIMIT:
    sys.setrecursionlimit(_REQUIRED_LIMIT)


class JSONParseError(Exception):
    pass


class JSONParser:
    def __init__(self, text, max_depth=MAX_DEPTH):
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1
        self.max_depth = max_depth
        self.depth = 0

    def error(self, msg):
        raise JSONParseError(f"{msg} at {self.line}:{self.col}")

    def peek(self):
        return self.text[self.pos] if self.pos < len(self.text) else ''

    def advance(self):
        ch = self.text[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def skip_ws(self):
        while self.pos < len(self.text) and self.text[self.pos] in ' \t\n\r':
            self.advance()

    def parse(self):
        self.skip_ws()
        value = self.parse_value()
        self.skip_ws()
        if self.pos < len(self.text):
            self.error("Unexpected trailing characters")
        return value

    def parse_value(self):
        if self.depth > self.max_depth:
            self.error(f"Maximum depth {self.max_depth} exceeded")
        self.skip_ws()
        ch = self.peek()
        if ch == '':
            self.error("Unexpected end of input")
        if ch == '{':
            return self.parse_object()
        if ch == '[':
            return self.parse_array()
        if ch == '"':
            return self.parse_string()
        if ch == 't':
            return self.parse_literal('true', True)
        if ch == 'f':
            return self.parse_literal('false', False)
        if ch == 'n':
            return self.parse_literal('null', None)
        if ch == '-' or ch.isdigit():
            return self.parse_number()
        self.error(f"Unexpected character {ch!r}")

    def parse_literal(self, lit, value):
        for c in lit:
            if self.peek() != c:
                self.error(f"Invalid literal, expected {lit!r}")
            self.advance()
        return value

    def parse_object(self):
        self.advance()
        self.depth += 1
        obj = {}
        self.skip_ws()
        if self.peek() == '}':
            self.advance()
            self.depth -= 1
            return obj
        while True:
            self.skip_ws()
            if self.peek() != '"':
                self.error("Expected string key in object")
            key = self.parse_string()
            self.skip_ws()
            if self.peek() != ':':
                self.error("Expected ':' after key")
            self.advance()
            obj[key] = self.parse_value()
            self.skip_ws()
            ch = self.peek()
            if ch == ',':
                self.advance()
                continue
            if ch == '}':
                self.advance()
                self.depth -= 1
                return obj
            self.error("Expected ',' or '}' in object")

    def parse_array(self):
        self.advance()
        self.depth += 1
        arr = []
        self.skip_ws()
        if self.peek() == ']':
            self.advance()
            self.depth -= 1
            return arr
        while True:
            arr.append(self.parse_value())
            self.skip_ws()
            ch = self.peek()
            if ch == ',':
                self.advance()
                continue
            if ch == ']':
                self.advance()
                self.depth -= 1
                return arr
            self.error("Expected ',' or ']' in array")

    def parse_string(self):
        self.advance()
        buf = []
        while True:
            if self.pos >= len(self.text):
                self.error("Unterminated string")
            ch = self.peek()
            if ch == '"':
                self.advance()
                return ''.join(buf)
            if ch == '\\':
                self.advance()
                if self.pos >= len(self.text):
                    self.error("Unterminated escape sequence")
                esc = self.advance()
                mapping = {'"': '"', '\\': '\\', '/': '/', 'n': '\n',
                           't': '\t', 'r': '\r', 'b': '\b', 'f': '\f'}
                if esc in mapping:
                    buf.append(mapping[esc])
                elif esc == 'u':
                    hx = ''
                    for _ in range(4):
                        if self.pos >= len(self.text):
                            self.error("Unterminated \\u escape")
                        h = self.advance()
                        if h not in '0123456789abcdefABCDEF':
                            self.error(f"Invalid hex digit in \\u escape: {h!r}")
                        hx += h
                    buf.append(chr(int(hx, 16)))
                else:
                    self.error(f"Invalid escape character: \\{esc}")
            elif ord(ch) < 0x20:
                self.error(f"Unescaped control character: {ch!r}")
            else:
                buf.append(self.advance())

    def parse_number(self):
        start = self.pos
        if self.peek() == '-':
            self.advance()
        if self.peek() == '0':
            self.advance()
        elif self.peek().isdigit():
            while self.peek().isdigit():
                self.advance()
        else:
            self.error("Invalid number")
        is_float = False
        if self.peek() == '.':
            is_float = True
            self.advance()
            if not self.peek().isdigit():
                self.error("Expected digit after decimal point")
            while self.peek().isdigit():
                self.advance()
        if self.peek() in ('e', 'E'):
            is_float = True
            self.advance()
            if self.peek() in ('+', '-'):
                self.advance()
            if not self.peek().isdigit():
                self.error("Invalid exponent")
            while self.peek().isdigit():
                self.advance()
        s = self.text[start:self.pos]
        try:
            return float(s) if is_float else int(s)
        except ValueError:
            self.error(f"Invalid number: {s}")


def parse_json(text, max_depth=MAX_DEPTH):
    return JSONParser(text, max_depth).parse()