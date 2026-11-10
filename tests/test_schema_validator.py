import unittest

from src.schema_validator import ACTIVITY_SCHEMA, SEQUENCE_SCHEMA, validate


class TestSchemaValidator(unittest.TestCase):
    def test_valid_sequence(self):
        data = {'sequence': [{'actor': 'A', 'action': 'B', 'target': 'C'}]}
        self.assertEqual(validate(data, SEQUENCE_SCHEMA), [])

    def test_missing_field(self):
        data = {'sequence': [{'actor': 'A', 'action': 'B'}]}
        errors = validate(data, SEQUENCE_SCHEMA)
        self.assertTrue(any('target' in e for e in errors))

    def test_wrong_type(self):
        data = {'sequence': [{'actor': 'A', 'action': 'B', 'target': 'C',
                              'parameters': 'not array'}]}
        errors = validate(data, SEQUENCE_SCHEMA)
        self.assertTrue(any('array' in e for e in errors))

    def test_empty_array(self):
        data = {'sequence': []}
        errors = validate(data, SEQUENCE_SCHEMA)
        self.assertTrue(any('at least' in e for e in errors))

    def test_valid_activity(self):
        data = {'activity': [{'step': 'A', 'next': 'B'}, {'step': 'B'}]}
        self.assertEqual(validate(data, ACTIVITY_SCHEMA), [])

    def test_activity_bad_step_type(self):
        data = {'activity': [{'step': 42}]}
        errors = validate(data, ACTIVITY_SCHEMA)
        self.assertTrue(any('string' in e for e in errors))


if __name__ == '__main__':
    unittest.main()