import unittest

from src.graph_analysis import (analyze, build_adjacency, find_cycles,
                                find_unreachable, topological_sort)


def make_adj(edges):
    nodes = {}
    for a, b in edges:
        nodes.setdefault(a, {'next': [], 'edges': []})
        nodes.setdefault(b, {'next': [], 'edges': []})
        nodes[a]['next'].append(b)
    return build_adjacency(nodes)


class TestGraphAnalysis(unittest.TestCase):
    def test_acyclic(self):
        adj = make_adj([('A', 'B'), ('B', 'C')])
        self.assertEqual(topological_sort(adj), ['A', 'B', 'C'])
        self.assertEqual(find_cycles(adj), [])

    def test_simple_cycle(self):
        adj = make_adj([('A', 'B'), ('B', 'A')])
        cycles = find_cycles(adj)
        self.assertEqual(len(cycles), 1)
        self.assertEqual(set(cycles[0]), {'A', 'B'})
        self.assertIsNone(topological_sort(adj))

    def test_self_loop(self):
        adj = make_adj([('A', 'A')])
        cycles = find_cycles(adj)
        self.assertEqual(len(cycles), 1)
        self.assertEqual(cycles[0], ['A'])

    def test_unreachable(self):
        adj = make_adj([('A', 'B'), ('C', 'D')])
        unreachable = find_unreachable(adj, 'A')
        self.assertIn('C', unreachable)
        self.assertIn('D', unreachable)
        self.assertNotIn('A', unreachable)
        self.assertNotIn('B', unreachable)

    def test_multiple_cycles(self):
        adj = make_adj([('A', 'B'), ('B', 'A'), ('C', 'D'), ('D', 'C')])
        self.assertEqual(len(find_cycles(adj)), 2)

    def test_analysis_hanging_sink(self):
        adj = make_adj([('Start', 'Orphan')])
        result = analyze(adj)
        self.assertIn('Orphan', result['hanging_sinks'])

    def test_analysis_final_sink(self):
        adj = make_adj([('Start', 'EndNode')])
        result = analyze(adj)
        self.assertNotIn('EndNode', result['hanging_sinks'])

    def test_roots(self):
        adj = make_adj([('Root', 'A'), ('A', 'B')])
        result = analyze(adj)
        self.assertEqual(result['roots'], ['Root'])


if __name__ == '__main__':
    unittest.main()