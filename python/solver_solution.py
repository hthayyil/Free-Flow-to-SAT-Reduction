from z3 import *
import os
import re

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(THIS_FOLDER, 'input.txt')

f = open(file)
size = int(f.readline()) #get the first line with the size variables
numVertices = size * size
graph = [None] * numVertices
#print(numVertices)

#this set contains how many distinct colors there are in the graph
colorset = set()
terminal_node = set()
terminal_vertices = set()

cnt = 0;
for x in range (0, numVertices) :
    char = f.read(1)

        #skip empty lines
    while (char is '' or char.isspace() or char is '\n') :
        char = f.read(1)

    if (char == '.') :
        graph[x] = "NONE"

    else :
        graph[x] = char
        terminal_node.add( (x, char))
        terminal_vertices.add(str(x))
        if (char not in colorset) :
            colorset.add(char)
    #print(char)

#for x in range (0, numVertices):
    #print (x, graph[x])

#print (terminal_node)


# generates a two-level dictionary:
#           vars[<vertex-name>][<color>] -> z3-variable
# example:  vars["u"]["G"] is the "green" indicator variable
#           for vertex "u"
def variables(graph):
    vars = {}
    for u in range (len(graph)):
        vars[str(u)] = {}
        #print (graph[u])
    #    if graph[u] != 'NONE' :
    #        vars[str(u)][graph[u]] = Bool(str(u) + graph[u])

    #    elif graph[u] == 'NONE' :
        for v in colorset:
            vars[str(u)][v] = Bool(str(u) + v)
    #print(vars)
    return vars

#Obtains every distinct edge
def distinct_edges(graph):
    d_edges= set()

    for u in range(0, numVertices-1):
        #print(u)
        if (u+1 < numVertices and u+1 > 0 and u+1 > u and (u+1) %size != 0  ) : d_edges.add((u, u+1))
        if (u-1 < numVertices and u-1 > 0 and u-1 > u ) : d_edges.add((u, u-1))
        if (u-size < numVertices and u-size > 0 and u-size > u ): d_edges.add((u, u - size))
        if (u+size < numVertices and u+size > 0 and u+size > u ): d_edges.add((u, u + size))

    #print(len(edges))
    return d_edges

#obtains ever edge forward and backward
def edges(graph):
    edge = set()

    for u in range(0, numVertices):
        #print (u)
        if (u+1 < numVertices and u+1 > 0  and (u+1) % size != 0 ) : edge.add((u, u+1))
        if (u-1 < numVertices and u-1 >= 0 and (u) % size != 0  ) : edge.add((u, u-1))
        if (u-size < numVertices and u-size >= 0): edge.add((u, u - size))
        if (u+size < numVertices and u+size > 0 ): edge.add((u, u + size))

    #print(len(edges))
    return edge

#
# takes a list of z3 bool variables and generates a list of
#   clauses (for CNF) which are all true iff exactly one of the
#   variables is set to true
# (handy little utility!)
def exactly_one(vars):
    #print (vars)
    clauses = [vars]        # at least one of the literals is true
    # Now encode no more than one literal is true.
    # Hint: there is no pair of literals such that both are true.
    for i in range(len(vars)):
        for j in range(i+1, len(vars)):
    # xi->!xj
            clauses += [[Not(vars[i]), Not(vars[j])]]
    return clauses

def exactly_one_(vars):
    #print (vars)
    clauses = []        # at least one of the literals is true
    # Now encode no more than one literal is true.
    # Hint: there is no pair of literals such that both are true.
    for i in range(len(vars)):
        for j in range(i+1, len(vars)):
    # xi->!xj
            clauses += [[Not(vars[i]), Not(vars[j])]]
    return clauses


def exactly_two_true(vars):
    #clauses = [vars] #at least one of the literals is true
    ret = [];
    clauses = []
    #enumerate every pair of literals
    for i in range(len(vars)):
        for j in range(i+1, len(vars)):
            clauses += [ And([vars[i], vars[j] ] ) ]

    #print(clauses)
    #this will return the list of clauses where exactly one pair is true
    ret_list = exactly_one_(clauses)
    #print(ret_list)
    for c in ret_list:
        #print("CL")
        #print(c)
        ret += [Or(c)]
    #print(ret)
    ret= [And(Or(clauses), And(ret))]
    return ret

#returns two lists of clauses ANDED with eachother
#the first list asserts that exactly two neighbors must be the color
#the second list asserts that exaclty two neighbors must not be the color
def create_neighbor_clauses(connector, vars):

    v1 = exactly_two_true(vars)
    return And( [connector, Or(v1)] )

def formula(graph):
    counter = 0
    f =  Solver()
    vars = variables(graph)
    edges_ = edges(graph)
    #print (vars)
    # for each vertex u, generate clauses enforcing that
    #   in any satisfying truth assignment, exactly one of
    #   the three associated indicator variables (RGB) is
    #   true (indicating the color assigned to u)
    for u in vars:
        #print(u)
        list = []
        if u not in terminal_vertices:
            list+= [Bool(u + "white")]
        #if u in terminal_vertices:
    
        for color in colorset:
            try:
             #print(vars[u][color])
             list += [vars[u][color]]
            except KeyError:
                continue


        uclauses = exactly_one(list)
        for c in uclauses:
            print(c)
            f.add(Or(c))
            counter = counter+1



    #terminal vertices must have exactly one edge that is the same color as it
    for [u,v] in terminal_node:
        index = u
        color = v
        clauses = []
        #Add the statement that the terminal node must be the color it was assigned
        f.add(Bool(str(index) + v))
        #counter = counter+1

        #print (u,v)
        for x in edges_:
            #if an edge is connected to a terminal node add it's truth assignment to clauses
            if (x[0] == index):
                clauses+= [Bool(str(x[1]) + color)]

        uclauses = exactly_one(clauses)
        for c in uclauses:
            f.add(Or(c))
            #counter =counter+1

    #every non terminal node u "connecting node" must have at least two colored edges of the same color
    for u in vars:
        if u in terminal_vertices:
            continue

        elif u not in terminal_vertices :
            for c in colorset:
                neighbors = []
                for [x,y] in edges_:
                    if str(x) == u:
                    #print(x, y)
                        neighbors += [Bool(str(y) + c)]

                #adds the clause for every connecting node if it is a color y then exactly exactly two of it's neighbors must be the same color y

                f.add(Or((create_neighbor_clauses(Bool(u + c), neighbors)), Not(Bool(u+c))))
                #counter = counter+1


    #print(counter)
    return f

f = formula(graph)
#print(f)
print(f.check())

if (f.check() == sat) :

    model = f.model()
    #for u in model:
    for x in range (0, numVertices):
        isColor = 0;
        for c in colorset:
            if (model.evaluate(Bool(str(x) + str(c)))):
                print(str(c)),
                isColor = 1
        if (isColor == 0): print("."),
        if ( (x+1) % size == 0): print ('\n')
        isColor = 0
