"""Анализ графа: Tarjan SCC, недостижимые узлы, топосортировка. O(V + E)."""


def build_adjacency(nodes):
    return {n: list(data['next']) for n, data in nodes.items()}


def find_in_degree(adj):
    indeg = {n: 0 for n in adj}
    for n, neighbors in adj.items():
        for m in neighbors:
            indeg.setdefault(m, 0)
            indeg[m] += 1
    return indeg


def find_roots(adj):
    indeg = find_in_degree(adj)
    return [n for n, d in indeg.items() if d == 0]


def find_sinks(adj):
    return [n for n, neighbors in adj.items() if not neighbors]


def tarjan_scc(adj):
    """Итеративный Тарьян (SCC)."""
    index_counter = [0]
    stack = []
    lowlink = {}
    index = {}
    on_stack = {}
    result = []

    for v in adj:
        if v in index:
            continue
        work = [(v, iter(adj.get(v, [])))]
        index[v] = lowlink[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack[v] = True
        while work:
            node, it = work[-1]
            advanced = False
            for w in it:
                if w not in index:
                    index[w] = lowlink[w] = index_counter[0]
                    index_counter[0] += 1
                    stack.append(w)
                    on_stack[w] = True
                    work.append((w, iter(adj.get(w, []))))
                    advanced = True
                    break
                elif on_stack.get(w):
                    if index[w] < lowlink[node]:
                        lowlink[node] = index[w]
            if not advanced:
                work.pop()
                if work:
                    parent = work[-1][0]
                    if lowlink[node] < lowlink[parent]:
                        lowlink[parent] = lowlink[node]
                if lowlink[node] == index[node]:
                    scc = []
                    while True:
                        w = stack.pop()
                        on_stack[w] = False
                        scc.append(w)
                        if w == node:
                            break
                    result.append(scc)
    return result


def find_cycles(adj):
    sccs = tarjan_scc(adj)
    cycles = []
    for scc in sccs:
        if len(scc) > 1:
            cycles.append(scc)
        elif len(scc) == 1 and scc[0] in adj.get(scc[0], []):
            cycles.append(scc)
    return cycles


def find_reachable(adj, start):
    visited = set()
    stack = [start]
    while stack:
        n = stack.pop()
        if n in visited:
            continue
        visited.add(n)
        for m in adj.get(n, []):
            if m not in visited:
                stack.append(m)
    return visited


def find_unreachable(adj, start):
    reachable = find_reachable(adj, start)
    return [n for n in adj if n not in reachable]


def topological_sort(adj):
    indeg = find_in_degree(adj)
    queue = [n for n, d in indeg.items() if d == 0]
    order = []
    idx = 0
    while idx < len(queue):
        n = queue[idx]
        idx += 1
        order.append(n)
        for m in adj.get(n, []):
            indeg[m] -= 1
            if indeg[m] == 0:
                queue.append(m)
    if len(order) != len(adj):
        return None
    return order


def analyze(adj):
    result = {}
    roots = find_roots(adj)
    result['roots'] = roots
    if roots:
        start = roots[0]
        result['start'] = start
        result['unreachable'] = find_unreachable(adj, start)
    else:
        result['start'] = None
        result['unreachable'] = []
    result['sinks'] = find_sinks(adj)
    result['hanging_sinks'] = [n for n in result['sinks'] if not n.startswith('End')]
    result['cycles'] = find_cycles(adj)
    result['topological_order'] = topological_sort(adj)
    return result