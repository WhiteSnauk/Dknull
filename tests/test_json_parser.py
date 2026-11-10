import unittest

from src.json_parser import JSONParseError, parse_json


class TestJSONParser(unittest.TestCase):
    def test_scalars(self):
        self.assertEqual(parse_json('42'), 42)
        self.assertEqual(parse_json('"hello"'), 'hello')
        self.assertIs(parse_json('true'), True)
        self.assertIsNone(parse_json('null'))
        self.assertEqual(parse_json('[]'), [])
        self.assertEqual(parse_json('{}'), {})

    def test_object(self):
        self.assertEqual(parse_json('{"a": 1, "b": [2, 3]}'),
                         {'a': 1, 'b': [2, 3]})

    def test_escapes(self):
        self.assertEqual(parse_json(r'"a\nb"'), 'a\nb')
        self.assertEqual(parse_json(r'"a\"b"'), 'a"b')
        self.assertEqual(parse_json(r'"a\\b"'), 'a\\b')
        self.assertEqual(parse_json(r'"\u0041"'), 'A')
        self.assertEqual(parse_json(r'"\t\r"'), '\t\r')

    def test_numbers(self):
        self.assertEqual(parse_json('3.14'), 3.14)
        self.assertEqual(parse_json('-42'), -42)
        self.assertEqual(parse_json('1e10'), 1e10)
        self.assertEqual(parse_json('1.5e-3'), 1.5e-3)
        self.assertIsInstance(parse_json('12345678901234567890'), int)

    def test_errors(self):
        with self.assertRaises(JSONParseError):
            parse_json('{')
        with self.assertRaises(JSONParseError):
            parse_json('"unterminated')
        with self.assertRaises(JSONParseError):
            parse_json('[1, 2,]')
        with self.assertRaises(JSONParseError):
            parse_json('{"a": }')

    def test_error_position(self):
        try:
            parse_json('{"a": }')
        except JSONParseError as e:
            self.assertIn(':', str(e))

    def test_deep_nesting(self):
        deep = '[' * 600 + ']' * 600
        with self.assertRaises(JSONParseError):
            parse_json(deep)


if __name__ == '__main__':
    unittest.main()