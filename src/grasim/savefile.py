from typing import Any
import numpy as np
from dataclasses import dataclass
import re
import numpy.typing as nptype

# list of (node1, distance, node2)
NodeDistance = tuple[str, int, str]

@dataclass
class WaypointGraph:
    graph_matrix : nptype.NDArray[Any] # Adjancy with distances
    start_idx : int
    end_idx : int
    node_lookup : dict[str, int] # NodeName => index in graph_matrix
    heuristics : list[float] # NodeIndex => heuristic

def parse_text(unparsed_text : list[str]):
    # TODO function: parse_graph
    nodes : set = set()
    heuristics_dict : dict[str, float] = {} # NodeName => heuristic
    distances : list[NodeDistance] = []
    start : str | None = None
    end : str | None = None 

    node_node_connection_regex = re.compile(r"(\w+) -(\d+)- (\w+)")
    node_heuristic_regex = re.compile(r"(\w+)\((\d+)\)")
    node_start_regex = re.compile(r"START (\w+)")
    node_end_regex = re.compile(r"END (\w+)")

    for line_idx, line in enumerate(unparsed_text):        
        if match := node_node_connection_regex.match(line):
            node1, estimated_total, node2 = match.groups()
            nodes.add(node1)
            nodes.add(node2)
            distances.append((node1, float(estimated_total), node2))
        elif match := node_heuristic_regex.match(line):
            node, heuristic = match.groups()
            heuristics_dict[node] = float(heuristic)
        elif match := node_start_regex.match(line):
            start = str(match.group(1))
        elif match := node_end_regex.match(line):
            end = str(match.group(1))

    # Create Graph matrix
    graph_matrix = np.full((len(nodes), len(nodes)), -1, dtype=np.int16)
    
    # Lookuptable for variables 'A' -> 0, 'B' -> 1
    node_lookup = dict(zip(list(nodes), range(len(nodes)))) 
    # Write distance into graph
    for node1, estimated_total, node2 in distances:
        idx1 = node_lookup[node1]
        idx2 = node_lookup[node2]
        graph_matrix[idx1, idx2] = estimated_total
        graph_matrix[idx2, idx1] = estimated_total

    if start == None or end == None:
        raise SyntaxError("File did not contain 'START <NAME>' and 'END <NAME>'")

    start_idx = node_lookup[start]
    end_idx = node_lookup[end]

    if len(heuristics_dict) == 0:
        heuristics = [0] * len(node_lookup) # if no heuristics, fill with 0
    else:
        heuristics = [heuristics_dict[x] for x in node_lookup.keys()]

    return WaypointGraph(graph_matrix, start_idx, end_idx, node_lookup, heuristics)