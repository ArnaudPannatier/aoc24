from functools import cache
from pathlib import Path
from random import randint

import aocd
import networkx as nx

puzzle = aocd.get_puzzle(day=24, year=2024)
text = puzzle.input_data
lines = Path("results.txt").read_text().splitlines()


def make_graph_tuple(graph_lines):
    g = nx.DiGraph()
    ops = {}
    for line in graph_lines:
        a, op, b, _, c = line.split()
        g.add_edge(a, c)
        g.add_edge(b, c)
        ops[c] = op

    return g, ops, list(nx.topological_sort(g))


def solve(g, val, ops, order):
    for n in order:
        if n in val:
            continue
        p1, p2 = g.predecessors(n)
        op = ops[n]
        if op == "XOR":
            val[n] = val[p1] ^ val[p2]
        if op == "AND":
            val[n] = val[p1] & val[p2]
        if op == "OR":
            val[n] = val[p1] | val[p2]


def add(x, y, g, ops, order):
    assert len(x) == len(y)

    val = {}
    for i, (xx, yy) in enumerate(zip(reversed(x), reversed(y))):
        val[f"x{i:02}"], val[f"y{i:02}"] = int(xx), int(yy)

    solve(g, val, ops, order)
    zs = sorted([(k, v) for k, v in val.items() if k.startswith("z")], reverse=True)
    return "".join(str(v) for _, v in zs)


def all_lines_leading_to(h, node, graph_lines):
    ancestors = nx.ancestors(h, node)
    ancestors.add(node)
    return [line for line in graph_lines if line.split()[-1] in ancestors]


def switch(graph_lines, a, b):
    i1, i2 = graph_lines.index(a), graph_lines.index(b)
    h_lines = list(graph_lines)
    a1, a2 = a.split("->")
    b1, b2 = b.split("->")
    n1 = f"{a1}->{b2}"
    n2 = f"{b1}->{a2}"
    h_lines[i1], h_lines[i2] = n1, n2
    return h_lines


def apply_switches(graph_lines, switches):
    h_lines = list(graph_lines)
    try:
        for a, b in switches:
            h_lines = switch(h_lines, a, b)
    except ValueError:
        print(switches)
        raise ValueError
    return h_lines


@cache
def _nb_errors(lines):
    errors = 0
    try:
        graph_tuple = make_graph_tuple(lines)
    except nx.NetworkXUnfeasible:
        return 1000

    xs, ys = f"{0:045b}", f"{0:045b}"
    if int(add(xs, ys, *graph_tuple), 2) != 0:
        errors += 1

    for i in range(N):
        possibilites = [
            (0, 2**i),
            (2**i, 0),
            (2**i - 1, 2**i - 1),
            (2**i, 2**i),
        ]
        for x, y in possibilites:
            xs, ys = f"{x:045b}", f"{y:045b}"
            if int(add(xs, ys, *graph_tuple), 2) != x + y:
                errors += 1

    return errors


def nb_errors(lines):
    return _nb_errors(tuple(lines))


def switch_to_sol(switches):
    ts = [ss for s in switches for ss in s]
    return ",".join(sorted([t.split(" -> ")[-1] for t in ts]))


g = nx.DiGraph()
init, graph_lines = map(lambda t: t.splitlines(), text.split("\n\n"))
N = 45


zeros = [l for l in lines if l.startswith("0")]
for z in zeros:
    switches = eval("[" + z.split("[")[-1])

    new_lines = apply_switches(graph_lines, switches)

    print(switch_to_sol(switches), nb_errors(new_lines))

    graph_tuple = make_graph_tuple(new_lines)

    errors = 0
    for _ in range(100):
        x = randint(0, int("1" * 45, 2))
        y = randint(0, int("1" * 45, 2))
        xs, ys = f"{x:045b}", f"{y:045b}"
        if int(add(xs, ys, *graph_tuple), 2) != x + y:
            errors += 1
    print(errors)
