#!/usr/bin/env python3
"""Бенчмарк анализа графа деятельности на 10k узлов и 30k рёбер."""

import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.graph_analysis import analyze, build_adjacency  # noqa: E402


def make_benchmark_activity(n_steps, n_extra_edges):
    """Строит activity-подобные узлы с цепочкой и случайными рёбрами."""
    nodes = {}
    steps = [f"Step{i}" for i in range(n_steps)]
    for s in steps:
        nodes[s] = {'next': [], 'edges': []}
    for i in range(n_steps - 1):
        nodes[steps[i]]['next'].append(steps[i + 1])
    random.seed(42)
    for _ in range(n_extra_edges):
        a = random.randrange(n_steps - 1)
        b = random.randrange(a + 1, n_steps)
        if steps[b] not in nodes[steps[a]]['next']:
            nodes[steps[a]]['next'].append(steps[b])
    return nodes


def main():
    n_steps = 10_000
    n_extra = 30_000
    print(f"Building benchmark: {n_steps} steps, ~{n_extra} extra edges...")
    nodes = make_benchmark_activity(n_steps, n_extra)
    adj = build_adjacency(nodes)
    total_edges = sum(len(v) for v in adj.values())
    print(f"Actual edges: {total_edges}")

    t0 = time.perf_counter()
    result = analyze(adj)
    elapsed = time.perf_counter() - t0

    print(f"Analysis took {elapsed * 1000:.1f} ms")
    print(f"Cycles: {len(result['cycles'])}")
    print(f"Unreachable: {len(result['unreachable'])}")
    print(f"Topological order computed: {result['topological_order'] is not None}")

    if elapsed > 2.0:
        print("WARNING: exceeded 2 second limit")
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())