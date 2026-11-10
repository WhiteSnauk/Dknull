"""Рендер диаграммы последовательности в текстовом виде."""


def render_sequence_diagram(sequence):
    lines = ["Sequence Diagram:"]
    for item in sequence:
        params = item.get('parameters', [])
        params_str = f"({', '.join(params)})" if params else ""
        lines.append(f"{item['actor']} -> {item['target']}: {item['action']}{params_str}")
    return '\n'.join(lines)