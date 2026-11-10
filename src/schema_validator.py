"""Мини-движок валидации схемы: декларативные правила в виде словарей."""


class ValidationError(Exception):
    pass


def _type_name(value):
    if value is None:
        return 'null'
    if isinstance(value, bool):
        return 'boolean'
    if isinstance(value, int):
        return 'integer'
    if isinstance(value, float):
        return 'number'
    if isinstance(value, str):
        return 'string'
    if isinstance(value, list):
        return 'array'
    if isinstance(value, dict):
        return 'object'
    return type(value).__name__


def validate(value, schema, path='$'):
    errors = []
    _validate(value, schema, path, errors)
    return errors


def _validate(value, schema, path, errors):
    if schema is None:
        return

    expected_type = schema.get('type')
    if expected_type:
        actual = _type_name(value)
        ok = False
        if expected_type == 'integer' and isinstance(value, int) and not isinstance(value, bool):
            ok = True
        elif expected_type == 'number' and isinstance(value, (int, float)) and not isinstance(value, bool):
            ok = True
        elif expected_type == 'boolean' and isinstance(value, bool):
            ok = True
        elif expected_type == 'string' and isinstance(value, str):
            ok = True
        elif expected_type == 'array' and isinstance(value, list):
            ok = True
        elif expected_type == 'object' and isinstance(value, dict):
            ok = True
        elif expected_type == 'null' and value is None:
            ok = True
        if not ok:
            errors.append(f"{path}: expected {expected_type}, got {actual}")
            return

    if 'enum' in schema and value not in schema['enum']:
        errors.append(f"{path}: value must be one of {schema['enum']}")

    if isinstance(value, dict):
        for req in schema.get('required', []):
            if req not in value:
                errors.append(f"{path}: missing required field '{req}'")
        props = schema.get('properties', {})
        for k, v in value.items():
            if k in props:
                _validate(v, props[k], f"{path}.{k}", errors)
            elif schema.get('additionalProperties', True) is False:
                errors.append(f"{path}: unexpected field '{k}'")

    if isinstance(value, list):
        items_schema = schema.get('items')
        if items_schema is not None:
            for i, item in enumerate(value):
                _validate(item, items_schema, f"{path}[{i}]", errors)
        min_items = schema.get('minItems')
        if min_items is not None and len(value) < min_items:
            errors.append(f"{path}: expected at least {min_items} items, got {len(value)}")

    if isinstance(value, str):
        min_len = schema.get('minLength')
        if min_len is not None and len(value) < min_len:
            errors.append(f"{path}: string too short, expected at least {min_len}")


SEQUENCE_SCHEMA = {
    'type': 'object',
    'required': ['sequence'],
    'properties': {
        'sequence': {
            'type': 'array',
            'minItems': 1,
            'items': {
                'type': 'object',
                'required': ['actor', 'action', 'target'],
                'properties': {
                    'actor': {'type': 'string', 'minLength': 1},
                    'action': {'type': 'string', 'minLength': 1},
                    'target': {'type': 'string', 'minLength': 1},
                    'parameters': {
                        'type': 'array',
                        'items': {'type': 'string'},
                    },
                },
            },
        },
    },
}


ACTIVITY_SCHEMA = {
    'type': 'object',
    'required': ['activity'],
    'properties': {
        'activity': {
            'type': 'array',
            'minItems': 1,
            'items': {
                'type': 'object',
                'required': ['step'],
                'properties': {
                    'step': {'type': 'string', 'minLength': 1},
                    'next': {'type': 'string', 'minLength': 1},
                    'condition': {'type': 'string'},
                    'true': {'type': 'string'},
                    'false': {'type': 'string'},
                },
            },
        },
    },
}