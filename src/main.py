"""CLI-точка входа (используется через run.py)."""

import argparse
from pathlib import Path

from .activity_diagram import build_nodes, render_activity_diagram
from .graph_analysis import analyze, build_adjacency
from .json_parser import JSONParseError, parse_json
from .markdown_writer import write_activity_report, write_sequence_report
from .plugin_loader import load_plugins
from .repl import REPL
from .schema_validator import ACTIVITY_SCHEMA, SEQUENCE_SCHEMA, validate
from .sequence_diagram import render_sequence_diagram


def main(argv=None):
    parser = argparse.ArgumentParser(description="UML diagram generator")
    parser.add_argument('--repl', action='store_true')
    parser.add_argument('--file', type=str)
    parser.add_argument('--render', choices=['sequence', 'activity', 'both'])
    parser.add_argument('--export', type=str)
    parser.add_argument('--analyze', action='store_true')
    parser.add_argument('--workdir', type=str, default='.')
    args = parser.parse_args(argv)

    workdir = Path(args.workdir)

    if args.repl or not args.file:
        REPL(workdir).run()
        return 0

    text = Path(args.file).read_text(encoding='utf-8')
    try:
        data = parse_json(text)
    except JSONParseError as e:
        print(f"JSON error: {e}")
        return 1

    if 'sequence' in data:
        kind = 'sequence'
        schema = SEQUENCE_SCHEMA
    elif 'activity' in data:
        kind = 'activity'
        schema = ACTIVITY_SCHEMA
    else:
        print("Unknown data format: expected 'sequence' or 'activity' key")
        return 1

    errors = validate(data, schema)
    if errors:
        print("Validation errors:")
        for e in errors:
            print(f"  {e}")
        return 1

    if args.render in (kind, 'both'):
        if kind == 'sequence':
            print(render_sequence_diagram(data['sequence']))
        else:
            print(render_activity_diagram(data['activity']))

    if args.analyze and kind == 'activity':
        nodes = build_nodes(data['activity'])
        result = analyze(build_adjacency(nodes))
        print("\nAnalysis:")
        for k, v in result.items():
            print(f"  {k}: {v}")

    if args.export:
        if args.export == 'markdown':
            if kind == 'sequence':
                write_sequence_report(data['sequence'], workdir / 'sequence-diagram.md')
                print("Wrote sequence-diagram.md")
            else:
                nodes = build_nodes(data['activity'])
                result = analyze(build_adjacency(nodes))
                write_activity_report(data['activity'], result,
                                      workdir / 'activity-diagram.md')
                print("Wrote activity-diagram.md")
        else:
            registry = {}
            load_plugins(workdir / 'plugins', registry)
            exporter = registry.get(args.export)
            if exporter:
                print(exporter(data))
            else:
                print(f"Unknown export format: {args.export}")
                return 1

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())