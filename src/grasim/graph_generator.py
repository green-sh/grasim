import igraph as ig
import numpy as np

famous = [
    "Bull",
    "Chvatal",
    "Coxeter",
    "Cubical",
    "Diamond",
    "Dodecahedral",
    "Dodecahedron",
    "Folkman",
    "Franklin",
    "Frucht",
    "Grotzsch",
    "Heawood",
    "Herschel",
    "House",
    "HouseX",
    "Icosahedral",
    "Icosahedron",
    "Krackhardt_Kite",
    "Levi",
    "McGee",
    "Meredith",
    "Noperfectmatching",
    "Nonline",
    "Octahedral",
    "Octahedron",
    "Petersen",
    "Robertson",
    "Smallestcyclicgroup",
    "Tetrahedral",
    "Tetrahedron",
    "Thomassen",
    "Tutte",
    "Uniquely3colorable",
    "Walther",
    "Zachary",
]

for name in famous:
    graph = np.array(ig.Graph.Famous(name).get_adjacency().data)

    pairs = np.column_stack(np.where(graph == 1))

    character = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    def number_to_alphabet(i : int):
        full = ""
        r = -1
        if i == 0: return character[i]
        while i:
            r = i % len(character)
            full += character[r]
            i = i // len(character)
        return full[::-1]

    text = []
    for i in range(pairs.shape[0]//2):
        text.append(f"{number_to_alphabet(pairs[i][0])} -1- {number_to_alphabet(pairs[i][1])}")

    # Choose random start and end
    text.append(f"START {number_to_alphabet(pairs[0, 0])}")
    text.append(f"END {number_to_alphabet(pairs[pairs.shape[0]//2, 0])}")

    with open(f"{name}.graph", "x") as f:
        f.write("\n".join(text))
