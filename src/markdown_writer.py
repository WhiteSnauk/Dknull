"""Генерация Markdown-отчётов."""

from .activity_diagram import render_activity_diagram
from .sequence_diagram import render_sequence_diagram


def write_sequence_report(sequence, path):
    lines = ["# Sequence Diagram Report", "", "## Diagram", "", "```"]
    lines.append(render_sequence_diagram(sequence))
    lines.append("```")
    lines.append("")
    path.write_text('\n'.join(lines), encoding='utf-8')


def write_activity_report(activity, analysis, path):
    lines = ["# Activity Diagram Report", "", "## Diagram", "", "```"]
    lines.append(render_activity_diagram(activity))
    lines.append("```")
    lines.append("")
    lines.append("## Analysis")
    lines.append("")

    roots = analysis.get('roots', [])
    if roots:
        lines.append(f"- Start node(s): {', '.join(roots)}")
    else:
        lines.append("- Warning: no start node (no node without incoming edges)")
    if len(roots) > 1:
        lines.append(f"- Warning: multiple start nodes: {', '.join(roots)}")

    lines.append("")
    lines.append("### Cycles")
    cycles = analysis.get('cycles', [])
    if cycles:
        for c in cycles:
            lines.append(f"- Cycle: {' -> '.join(c)}")
    else:
        lines.append("- No cycles detected")

    lines.append("")
    lines.append("### Unreachable Steps")
    unr = analysis.get('unreachable', [])
    if unr:
        for u in unr:
            lines.append(f"- {u}")
    else:
        lines.append("- None")

    lines.append("")
    lines.append("### Sinks (no outgoing edges)")
    hanging = analysis.get('hanging_sinks', [])
    if hanging:
        for h in hanging:
            lines.append(f"- Warning: '{h}' has no outgoing edges and does not look final")
    else:
        lines.append("- All sinks look final (start with 'End')")

    lines.append("")
    lines.append("### Topological Order")
    lines.append("")
    order = analysis.get('topological_order')
    if order:
        lines.append(" -> ".join(order))
    else:
        lines.append("- Cannot compute (graph has cycles)")
    lines.append("")

    path.write_text('\n'.join(lines), encoding='utf-8')