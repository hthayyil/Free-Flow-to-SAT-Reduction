
# functions for constructing a z3 cnf formula (a "solver") for
#  the 3-colorability problem.

from z3 import *
import random
from timeit import default_timer as timer


colors = ["R", "G", "B"]

# two graphs g1 (3-colorable) and g2 (not 3-colorable)
# Note:  "edge-list" representation used

g1 = [["a", "b"],
        ["a", "c"],
        ["a", "d"],
        ["a", "e"],
        ["b", "c"],
        ["c", "d"],
        ["d", "e"],
        ["e", "b"]
        ]

g2 = [["a", "b"],
        ["a", "c"],
        ["a", "d"],
        ["a", "e"],
        ["a", "f"],
        ["b", "c"],
        ["c", "d"],
        ["d", "e"],
        ["e", "f"],
        ["f", "b"]
        ]

def gen_graph(nnodes, nedges):
    edges = []

    eset = set()

    while nedges >= 0:
        v = random.randint(1,nnodes)
        if v > 1:
            u = random.randint(1,v-1);
            ustr = "v" + str(u)
            vstr = "v" + str(v)
            estr = ustr + vstr
            if estr not in eset:
                edges += [[ustr, vstr]]
                nedges -= 1
                eset.add(estr)
    return edges

# takes a list of z3 bool variables and generates a list of
#   clauses (for CNF) which are all true iff exactly one of the
#   variables is set to true
# (handy little utility!)
def exactly_one(vars):
    #print(vars)
    clauses = [vars]       # at least one of the literals is true
    # Now encode no more than one literal is true.
    # Hint: there is no pair of literals such that both are true.
    for i in range(len(vars)):
        for j in range(i+1, len(vars)):
            # xi->!xj
            #print (vars[i])
            clauses += [And(  [Not(vars[i]), Not(vars[j])] )]
    #print (clauses)
    return clauses


# takes an edge-list representation of a graph and
#   returns a list of distinct vertices
def nodes(graph):
    nset = set()
    nlist = []

    for [u, v] in graph:
        if u not in nset:
            nlist += [u]
            nset.add(u)
        if v not in nset:
            nlist += [v]
            nset.add(v)
    # could have just returned the set...
    return nlist


# generates a two-level dictionary:
#           vars[<vertex-name>][<color>] -> z3-variable
# example:  vars["u"]["G"] is the "green" indicator variable
#           for vertex "u"
def variables(nodes):
    vars = {}
    for u in nodes:
        vars[u] = {}
        vars[u]["R"] = Bool(u + "R")
        vars[u]["G"] = Bool(u + "G")
        vars[u]["B"] = Bool(u + "B")

    #print(vars)
    return vars

# generates the formula ("solver") which is satisfiable iff the
#   given graph is 3-colorable
def formula(graph):
    f =  Solver()
    vars = variables(nodes(graph))

    # for each vertex u, generate clauses enforcing that
    #   in any satisfying truth assignment, exactly one of
    #   the three associated indicator variables (RGB) is
    #   true (indicating the color assigned to u)
    for u in vars:
        for c in colors:
            uclauses = exactly_one([vars[u]["R"], vars[u]["G"], vars[u]["B"] ])
        for c in uclauses:
            print("CL")
            print (c)
            f.add(Or(c))

    for [u, v] in graph:
        for c in colors:
            f.add(Or( [ Not(vars[u][c]), Not(vars[v][c])] ) )
    return f

def run_exp(nnodes, nedges):
    g = gen_graph(nnodes, nedges)

    start = timer()

    f = formula(g)
    ans = f.check()

    f = formula(g)
    ans = f.check()

    f = formula(g)
    ans = f.check()

    f = formula(g)
    ans = f.check()

    f = formula(g)
    ans = f.check()

    end = timer()

    print("|V|=" + str(nnodes) + "; |E|=" + str(nedges) +
            "; ans=" + str(ans) + "; time=" + str((end-start)/5.0))

formula(g1)
