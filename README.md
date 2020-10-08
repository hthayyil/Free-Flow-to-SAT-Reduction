# Free-Flow-to-SAT-Reduction

##Built using z3 solver in Python

Run Code from Inside Python Folder
Instatiate puzzle inside input.txt file

##Constraints

1. Terminal nodes must be exactly one color and are given in the problem instance
2. Every node must have exactly one color
2. Terminal nodes must have exactly one matching neighbor. 
3. A non-terminal node must be exactly one of the colors specified in the input or blank (“white”)
4. If a non-terminal node is not white/blank, it must have exactly 2 adjacent nodes that are the same color

