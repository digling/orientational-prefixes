from lingpy import *
import networkx as nx
import unidecode
from itertools import combinations
import matplotlib.pyplot as plt
try:
    from HTMLParser import HTMLParser
    html = HTMLParser()
except ImportError:
    import html

#In [19]: for a, b, c in combinations(G.nodes(), r=3):
#    ...:     idxA, idxB, idxC = [nhead.index(x)+1 for x in [a, b, c]]
#    ...:     print('{0:15} -> {1:15}  :  {2}'.format(a, b, matrix[idxA][idxB]))
#    ...:     print('{0:15} -> {1:15}  :  {2}'.format(b, c, matrix[idxB][idxC]))
#    ...:     print('{0:15} -> {1:15}  :  {2}'.format(a, c, matrix[idxA][idxC]))
#    ...:     print('')

# weight dictionary
dic ={  ("o-", "o-"): 0, 
        ("o-", "kə-"): 2, 
        ("o-", "læ-"): 2, 
        ("o-", "næ-"): 3,
        ("o-", "nə-"): 2, 
        ("o-", "və-"): 2, 
        ("kə-", "o-"): 2, 
        ("kə-", "kə-"): 0, 
        ("kə-", "læ-"): 2, 
        ("kə-", "næ-"): 2, 
        ("kə-", "nə-"): 3, 
        ("kə-", "və-"): 2, 
        ("læ-", "o-"): 2, 
        ("læ-", "kə-"): 2, 
        ("læ-", "læ-"): 0,
        ("læ-", "næ-"): 2, 
        ("læ-", "nə-"): 2, 
        ("læ-", "və-"): 3, 
        ("næ-", "o-"): 3, 
        ("næ-", "kə-"): 2, 
        ("næ-", "læ-"): 2, 
        ("næ-", "næ-"): 0, 
        ("næ-", "nə-"): 2, 
        ("næ-", "və-"): 2, 
        ("nə-", "o-"): 2, 
        ("nə-", "kə-"): 3,
        ("nə-", "læ-"): 2, 
        ("nə-", "næ-"): 2, 
        ("nə-", "nə-"): 0, 
        ("nə-", "və-"): 2, 
        ("və-", "o-"): 2, 
        ("və-", "kə-"): 2, 
        ("və-", "læ-"): 3,
        ("və-", "næ-"): 2, 
        ("və-", "nə-"): 2, 
        ("və-", "və-"): 0}

# make a graph
G = nx.Graph()

# browse the data
matrix = csv2list('data.tsv', strip_lines=False)
header = matrix[0][1:]

pins = {}
for h in header:
    pins[h] = unidecode.unidecode(h).replace(' ', '_').strip('_')
    G.add_node(pins[h], chinese=h)
for a, b in combinations(header, r=2):
    G.add_edge(pins[a], pins[b], weight=0)

nhead = [pins[h] for h in header]

for i, line in enumerate(matrix[1:]):
    row = zip(header, line[1:])
    
    for (hA, cellA), (hB, cellB) in combinations(row, r=2):
        if cellA.strip() and cellB.strip():
            nA, nB = pins[hA], pins[hB]
            weights = []
            cellsA, cellsB = cellA.split('/'), cellB.split('/')
            for cA in cellsA:
                for cB in cellsB:
                    #if cA != cB:
                        weights.append(dic[cA, cB])
            G[nA][nB]['weight'] += sum(weights) / len(weights) if weights else 0

maxw = max([d['weight'] for a, b, d in G.edges(data=True)])



# normalize edge weights
for nA, nB, data in G.edges(data=True):
    G[nA][nB]['nweight'] = maxw + 10 - data['weight']

# export to distance format
with open('matrix.dst', 'w') as f:
    f.write(' '+str(len(header))+'\n')
    for languageA in header:
        pA = pins[languageA]
        f.write('{0:10} '.format(pA[:9].replace(' ', '_')))
        for languageB in header:
            pB = pins[languageB]
            if pA == pB:
                f.write(' 0.00')
            else:

                weight = G[pA][pB]['nweight']
                f.write(' {0:.2f}'.format(weight))
        f.write('\n')


mst = nx.minimum_spanning_tree(G, weight='weight')

with open('graph.gml', 'w') as f:
    f.write('\n'.join(html.unescape(line) for line in nx.generate_gml(mst)))

plt.clf()
#pos = nx.circular_layout(mst)
nx.draw_networkx(mst, node_size=6, font_size=6)

plt.savefig('network.pdf')


# import data
new_locs = csv2list('mst-locations.tsv', strip_lines=False)
nG = nx.Graph()
for s, t in new_locs[1:]:
    if pins[s[1:-1]] not in nG:
        nG.add_node(pins[s[1:-1]], chinese=s[1:-1])
    if pins[t[1:-1]] not in nG:
        nG.add_node(pins[t[1:-1]], chinese=t[1:-1])

    tS, tT = pins[s[1:-1]], pins[t[1:-1]]
    nG.add_edge(tS, tT)

"""
count, all_count = 0, 0
for nA, nB, data in nG.edges(data=True):
    try:
        mst[nA][nB]
        print('[-] {0:10} -- {1:10}'.format(nA, nB))
        count += 1
    except: 
        print('[!] {0:10} -- {1:10}'.format(nA, nB))
    all_count += 1
print(count / all_count)
"""

# make the directed graph
dG = nx.DiGraph()

for node, data in nG.nodes(data=True):
    dG.add_node(node, **data)
# add the edges
for nA, nB, data in nG.edges(data=True):
    # retrieve indices in matrix
    idxA = nhead.index(nA)+1
    idxB = nhead.index(nB)+1

    # get directions from the matrix
    ab = matrix[idxA][idxB]
    ba = matrix[idxB][idxA]

    dG.add_edge(nA, nB, preposition=ab, info='road')
    dG.add_edge(nB, nA, preposition=ba, info='road')

#Summing up the weights of mst and nG
for a, b, data in G.edges(data=True):
   try:
       nG[a][b]['weight'] = data['weight']
   except:
       pass


def weights_of_tree(graph, weights='weights'):
   sums = 0
   for a, b, data in graph.edges(data=True):
       sums += data['weight']
   return sums

print(weights_of_tree(mst))
print(weights_of_tree(nG))


#Comparing the different edges

print ("in nG.edges try mst:")

for nA, nB, data in nG.edges(data=True):
    try:
        mst[nA][nB]
    except:
        print('[!] {0:20} -- {1:20} -- {2}'.format(nA, nB, data['weight']))

print("")

print ("in mst.edges try nG:")
for nA, nB, data in mst.edges(data=True):
    try:
        nG[nA][nB]
    except:
        print('[!] {0:20} -- {1:20} -- {2}'.format(nA, nB, data['weight']))



with open('digraph.gml', 'w') as f:
    f.write('\n'.join(html.unescape(line) for line in nx.generate_gml(dG)))


# combined graph
# add the edges
for nA, nB, data in mst.edges(data=True):
    # retrieve indices in matrix
    idxA = nhead.index(nA)+1
    idxB = nhead.index(nB)+1

    # get directions from the matrix
    ab = matrix[idxA][idxB]
    ba = matrix[idxB][idxA]
    
    if nB in dG[nA]:
        dG[nA][nB]['info'] += '-mst'
    else:
        dG.add_edge(nA, nB, preposition=ab, info='mst')
    if nA in dG[nB]:
        dG[nB][nA]['info'] += '-mst'
    else:
        dG.add_edge(nB, nA, preposition=ba, info='mst')

with open('digraph-combined.gml', 'w') as f:
    f.write('\n'.join(html.unescape(line) for line in nx.generate_gml(dG)))


def has_edge(a, b, graph):
    if b in graph[a]:
        return True
    return False

# start with mst
nodes = [x for x, y in mst.nodes(data=True)]
for a, b, c in combinations(nodes, r=3):
    abw = G[a][b]['weight']
    bcw = G[b][c]['weight']
    acw = G[a][c]['weight']
    
    if len(set([abw, bcw, acw])) < 3:

        if (has_edge(a, b, mst) and has_edge(a, c, mst)) or (
                has_edge(a, c, mst) and has_edge(b, c, mst)) or (
                        has_edge(a, b, mst) and has_edge(b, c, mst)):
                    if not has_edge(a, b, mst):
                        mst.add_edge(a, b, weight=abw)
                    elif not has_edge(b, c, mst):
                        mst.add_edge(b, c, weight=bcw)
                    elif not has_edge(a, c, mst):
                        mst.add_edge(a, c, weight=acw)

with open('msn.gml', 'w') as f:
    f.write('\n'.join(html.unescape(line) for line in nx.generate_gml(mst)))

print('minimum spanning network')
print ("in nG.edges try mst:")

for nA, nB, data in nG.edges(data=True):
    try:
        mst[nA][nB]
    except:
        print('[!] {0:20} -- {1:20} -- {2}'.format(nA, nB, data['weight']))

print("")

