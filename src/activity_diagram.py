"""Построение графа деятельности и текстовый рендер."""

from .condition_parser import parse_condition, render


def build_nodes(activity):
    """Строит словарь step -> {'next': [...], 'edges': [...]}."""
    nodes = {}
    for item in activity:
        nodes.setdefault(item['step'], {'next': [], 'edges': []})
    for item in activity:
        step = item['step']
        if 'next' in item:
            nodes[step]['next'].append(item['next'])
            nodes.setdefault(item['next'], {'next': [], 'edges': []})
        if 'condition' in item and 'true' in item and 'false' in item:
            nodes[step]['next'].extend([item['true'], item['false']])
            nodes.setdefault(item['true'], {'next': [], 'edges': []})
            nodes.setdefault(item['false'], {'next': [], 'edges': []})
    return nodes


def render_activity_diagram(activity):
    lines = ["Activity Diagram:"]
    for item in activity:
        step = item['step']
        if 'next' in item:
            lines.append(f"{step} -> {item['next']}")
        elif 'condition' in item and 'true' in item and 'false' in item:
            ast = parse_condition(item['condition'])
            cond = render(ast)
            lines.append(f"{step} -> {item['true']} (if {cond})")
            lines.append(f"{step} -> {item['false']} (if NOT ({cond}))")
    return '\n'.join(lines)