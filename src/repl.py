"""REPL с собственным токенизатором (без shlex/argparse)."""

from pathlib import Path

from .activity_diagram import build_nodes, render_activity_diagram
from .graph_analysis import analyze, build_adjacency
from .json_parser import JSONParseError, parse_json
from .markdown_writer import write_activity_report, write_sequence_report
from .plugin_loader import load_plugins
from .schema_validator import ACTIVITY_SCHEMA, SEQUENCE_SCHEMA, validate
from .sequence_diagram import render_sequence_diagram


def tokenize(line):
    tokens = []
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if ch.isspace():
            i += 1
            continue
        if ch in '"\'':
            quote = ch
            j = i + 1
            buf = []
            while j < n and line[j] != quote:
                if line[j] == '\\' and j + 1 < n:
                    buf.append(line[j + 1])
                    j += 2
                else:
                    buf.append(line[j])
                    j += 1
            tokens.append(''.join(buf))
            i = j + 1
            continue
        j = i
        while j < n and not line[j].isspace():
            j += 1
        tokens.append(line[i:j])
        i = j
    return tokens


class REPL:
    def __init__(self, workdir='.'):
        self.workdir = Path(workdir)
        self.history_file = self.workdir / 'history.txt'
        self.data = None
        self.kind = None
        self.registry = {}
        plugins_dir = self.workdir / 'plugins'
        if plugins_dir.exists():
            load_plugins(plugins_dir, self.registry)

    def log_history(self, line):
        with self.history_file.open('a', encoding='utf-8') as f:
            f.write(line + '\n')

    def run(self):
        print("UML Diagram REPL. Type 'help' for commands, 'quit' to exit.")
        while True:
            try:
                line = input("> ")
            except (EOFError, KeyboardInterrupt):
                break
            line = line.strip()
            if not line:
                continue
            self.log_history(line)
            if line in ('quit', 'exit', 'q'):
                break
            try:
                self.handle(line)
            except Exception as e:
                print(f"Error: {e}")

    def handle(self, line):
        tokens = tokenize(line)
        if not tokens:
            return
        cmd, args = tokens[0], tokens[1:]

        if cmd == 'help':
            print("Commands:")
            print("  load <file>      - load JSON file")
            print("  validate         - validate loaded data")
            print("  render sequence  - render sequence diagram")
            print("  render activity  - render activity diagram")
            print("  analyze          - analyze activity graph")
            print("  export <format>  - export (markdown or plugin)")
            print("  plugins          - list loaded plugins")
            print("  quit             - exit")
        elif cmd == 'load':
            if not args:
                print("Usage: load <file>")
                return
            self.do_load(args[0])
        elif cmd == 'validate':
            self.do_validate()
        elif cmd == 'render':
            if not args:
                print("Usage: render <sequence|activity>")
                return
            self.do_render(args[0])
        elif cmd == 'analyze':
            self.do_analyze()
        elif cmd == 'export':
            if not args:
                print("Usage: export <format>")
                return
            self.do_export(args[0])
        elif cmd == 'plugins':
            for name in sorted(self.registry):
                if not name.startswith('_'):
                    print(f"- {name}")
        else:
            print(f"Unknown command: {cmd}")

    def do_load(self, path):
        p = Path(path)
        if not p.is_absolute() and not p.exists():
            p = self.workdir / path
        text = p.read_text(encoding='utf-8')
        self.data = parse_json(text)
        if 'sequence' in self.data:
            self.kind = 'sequence'
        elif 'activity' in self.data:
            self.kind = 'activity'
        else:
            self.kind = None
            print("Warning: unknown data type")
        print(f"Loaded {p}")

    def do_validate(self):
        if self.data is None:
            print("No data loaded")
            return
        schema = SEQUENCE_SCHEMA if self.kind == 'sequence' else ACTIVITY_SCHEMA
        errors = validate(self.data, schema)
        if errors:
            for e in errors:
                print(f"  {e}")
        else:
            print("Validation OK")

    def do_render(self, which):
        if self.data is None:
            print("No data loaded")
            return
        if which == 'sequence':
            print(render_sequence_diagram(self.data['sequence']))
        elif which == 'activity':
            print(render_activity_diagram(self.data['activity']))
        else:
            print(f"Unknown render target: {which}")

    def do_analyze(self):
        if self.kind != 'activity':
            print("Analyze requires activity data")
            return
        nodes = build_nodes(self.data['activity'])
        result = analyze(build_adjacency(nodes))
        for k, v in result.items():
            print(f"{k}: {v}")

    def do_export(self, format_):
        if self.data is None:
            print("No data loaded")
            return
        if format_ == 'markdown':
            if self.kind == 'sequence':
                write_sequence_report(self.data['sequence'],
                                      self.workdir / 'sequence-diagram.md')
                print("Wrote sequence-diagram.md")
            elif self.kind == 'activity':
                nodes = build_nodes(self.data['activity'])
                result = analyze(build_adjacency(nodes))
                write_activity_report(self.data['activity'], result,
                                      self.workdir / 'activity-diagram.md')
                print("Wrote activity-diagram.md")
        else:
            exporter = self.registry.get(format_)
            if exporter:
                print(exporter(self.data))
            else:
                print(f"Unknown format: {format_}")