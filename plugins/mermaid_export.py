"""Плагин: экспорт в Mermaid."""

NAME = "mermaid"


def register(registry):
    registry['mermaid'] = export_mermaid


def export_mermaid(data):
    if 'sequence' in data:
        lines = ["sequenceDiagram"]
        for item in data['sequence']:
            params = ', '.join(item.get('parameters', []))
            if params:
                lines.append(
                    f"    {item['actor']}->>{item['target']}: "
                    f"{item['action']}({params})")
            else:
                lines.append(
                    f"    {item['actor']}->>{item['target']}: {item['action']}")
        return '\n'.join(lines)
    if 'activity' in data:
        lines = ["flowchart TD"]
        for item in data['activity']:
            step = item['step']
            if 'next' in item:
                lines.append(f"    {step} --> {item['next']}")
            if 'condition' in item and 'true' in item and 'false' in item:
                lines.append(f"    {step} -->|{item['condition']}| {item['true']}")
                lines.append(f"    {step} -->|NOT ({item['condition']})| {item['false']}")
        return '\n'.join(lines)
    return "% Unknown data"