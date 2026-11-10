import unittest

from src.condition_parser import ConditionError, parse_condition, render


class TestConditionParser(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(render(parse_condition('a')), 'a')

    def test_and(self):
        self.assertEqual(render(parse_condition('a AND b')), 'a AND b')

    def test_precedence(self):
        self.assertEqual(render(parse_condition('a OR b AND c')),
                         'a OR b AND c')
        self.assertEqual(render(parse_condition('a AND b OR c')),
                         'a AND b OR c')

    def test_parens(self):
        self.assertEqual(render(parse_condition('(a OR b) AND c')),
                         '(a OR b) AND c')

    def test_not(self):
        self.assertEqual(render(parse_condition('NOT a AND b')),
                         'NOT a AND b')
        self.assertEqual(render(parse_condition('NOT (a AND b)')),
                         'NOT (a AND b)')

    def test_compare(self):
        self.assertEqual(render(parse_condition('x > 5')), 'x > 5')
        self.assertEqual(render(parse_condition('x == "yes"')),
                         "x == 'yes'")

    def test_example(self):
        text = 'inventoryAvailable AND NOT blacklisted'
        self.assertEqual(render(parse_condition(text)), text)

    def test_error(self):
        with self.assertRaises(ConditionError):
            parse_condition('a AND')
        with self.assertRaises(ConditionError):
            parse_condition('(a')


if __name__ == '__main__':
    unittest.main()