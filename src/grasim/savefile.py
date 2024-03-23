from typing import Any
import numpy as np
from dataclasses import dataclass
import re
import numpy.typing as nptype
from grasim.errors import ParseError

# list of (node1, distance, node2)
NodeDistance = tuple[str, int, str]

@dataclass
class WaypointGraph:
    graph_matrix : nptype.NDArray[Any] # Adjancy with distances, -1 means not connected
    start_idx : int
    end_idx : int
    node_lookup : dict[str, int] # NodeName => index in graph_matrix
    heuristics : list[float] # NodeIndex => heuristic

def parse_text(unparsed_text : list[str]) -> WaypointGraph:
    # TODO function: parse_graph
    nodes : set = set()
    heuristics_dict : dict[str, int] = {} # NodeName => heuristic
    distances : list[NodeDistance] = []
    start : str | None = None
    end : str | None = None 

    node_node_connection_regex = re.compile(r"(\w+) -([0-9.]+)- (\w+)")
    node_node_connection_both_regex = re.compile(r"(\w+) <-([0-9.]+)-> (\w+)")
    node_node_connection_left_regex = re.compile(r"(\w+) <-([0-9.]+)- (\w+)")
    node_node_connection_right_regex = re.compile(r"(\w+) -([0-9.]+)-> (\w+)")
    node_heuristic_regex = re.compile(r"(\w+)\(([0-9.]+)\)")
    node_start_regex = re.compile(r"START (\w+)")
    node_end_regex = re.compile(r"END (\w+)")

    for line_idx, line in enumerate(unparsed_text):        
        if match := node_node_connection_regex.match(line) or node_node_connection_both_regex.match(line):
            node1, estimated_total, node2 = match.groups()
            nodes.add(node1)
            nodes.add(node2)
            distances.append((node1, float(estimated_total), node2))
            distances.append((node2, float(estimated_total), node1))
        elif match := node_node_connection_left_regex.match(line):
            node1, estimated_total, node2 = match.groups()
            nodes.add(node1)
            nodes.add(node2)
            distances.append((node2, float(estimated_total), node1))
        elif match := node_node_connection_right_regex.match(line):
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

    # Create Graph matrix with -1 as not connected
    graph_matrix = np.full((len(nodes), len(nodes)), -1, dtype=np.float64)
    
    # Lookuptable for variables 'A' -> 0, 'B' -> 1
    node_lookup = dict(zip(list(nodes), range(len(nodes)))) 
    # Write distance into graph
    for node1, estimated_total, node2 in distances:
        idx1 = node_lookup[node1]
        idx2 = node_lookup[node2]
        if graph_matrix[idx1, idx2] != -1 and graph_matrix[idx1, idx2] != estimated_total:
            raise ParseError(f"Ambiguous edges with different values: {node1} {node2}")
        graph_matrix[idx1, idx2] = estimated_total

    if start == None or end == None:
        raise ParseError("File did not contain 'START <NAME>' and 'END <NAME>'")
    
    start_idx = node_lookup[start]
    end_idx = node_lookup[end]

    replaced_node_lookup = {}
    for k,v in node_lookup.items():
        if k == start:
            replaced_node_lookup["START " + start] = v
        elif k == end:
            replaced_node_lookup["END " + end] = v
        else:
            replaced_node_lookup[k] = v

    # prefix start and end idx

    heuristics = [heuristics_dict.get(x, 0) for x in node_lookup.keys()]

    return WaypointGraph(graph_matrix, start_idx, end_idx, replaced_node_lookup, heuristics)