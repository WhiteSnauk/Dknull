import tempfile
import unittest
from pathlib import Path

from src.activity_diagram import build_nodes, render_activity_diagram
from src.graph_analysis import analyze, build_adjacency
from src.json_parser import parse_json
from src.markdown_writer import write_activity_report, write_sequence_report
from src.sequence_diagram import render_sequence_diagram


class TestIntegration(unittest.TestCase):
    def test_sequence_end_to_end(self):
        text = ('{"sequence": [{"actor": "A", "action": "Do", "target": "B", '
                '"parameters": ["x: 1"]}]}')
        data = parse_json(text)
        out = render_sequence_diagram(data['sequence'])
        self.assertIn("A -> B: Do(x: 1)", out)

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'sequence-diagram.md'
            write_sequence_report(data['sequence'], path)
            content = path.read_text(encoding='utf-8')
            self.assertIn("# Sequence Diagram Report", content)
            self.assertIn("A -> B: Do(x: 1)", content)

    def test_activity_end_to_end(self):
        text = '''{"activity": [
            {"step": "Start", "next": "End"},
            {"step": "End"}
        ]}'''
        data = parse_json(text)
        out = render_activity_diagram(data['activity'])
        self.assertIn("Start -> End", out)

        nodes = build_nodes(data['activity'])
        result = analyze(build_adjacency(nodes))
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'activity-diagram.md'
            write_activity_report(data['activity'], result, path)
            content = path.read_text(encoding='utf-8')
            self.assertIn("# Activity Diagram Report", content)
            self.assertIn("## Analysis", content)

    def test_activity_full_sample(self):
        text = '''{"activity": [
            {"step": "StartOrderProcessing", "next": "CheckInventory"},
            {"step": "CheckInventory", "condition": "inventoryAvailable AND NOT blacklisted",
             "true": "ProcessPayment", "false": "NotifyCustomer"},
            {"step": "ProcessPayment", "next": "CompleteOrder"},
            {"step": "NotifyCustomer", "next": "EndOrderProcessing"}
        ]}'''
        data = parse_json(text)
        out = render_activity_diagram(data['activity'])
        self.assertIn(
            "CheckInventory -> ProcessPayment (if inventoryAvailable AND NOT blacklisted)",
            out)
        self.assertIn(
            "CheckInventory -> NotifyCustomer (if NOT (inventoryAvailable AND NOT blacklisted))",
            out)
        nodes = build_nodes(data['activity'])
        result = analyze(build_adjacency(nodes))
        self.assertEqual(result['roots'], ['StartOrderProcessing'])
        self.assertEqual(len(result['cycles']), 0)
        self.assertIn('CompleteOrder', result['hanging_sinks'])
        self.assertNotIn('EndOrderProcessing', result['hanging_sinks'])


if __name__ == '__main__':
    unittest.main()