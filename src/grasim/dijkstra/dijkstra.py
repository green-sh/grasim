import numpy as np
from grasim.savefile import WaypointGraph


def init_dijkstra_table(num_nodes, start_idx):
    """
    The Data table hols the folling values:
    [distance, last_idx, done, estimated_total]
    """
    dijkstra_table = np.ones((num_nodes, 4)) * [np.inf, 0, 0, np.inf] 
    dijkstra_table[start_idx] = [0, start_idx, 0, 0]
    return dijkstra_table

def dijkstra_step(dijkstra_table, graph : WaypointGraph):
    # find minimal node
    valid_idx = np.where((dijkstra_table[:, 2] == 0) & (dijkstra_table[:, 3] != np.inf))[0]

    # if there is a valid node left to explore
    if (len(valid_idx) != 0):

        next_idx = valid_idx[dijkstra_table[valid_idx, 3].argmin()]

        dijkstra_table[next_idx][2] = 1

        for idx_expand in np.where(graph.graph_matrix[next_idx] != -1)[0]:
            distance = graph.graph_matrix[next_idx, idx_expand] + dijkstra_table[next_idx, 0]
            estimated_total = distance \
                + graph.heuristics[idx_expand]
            # if is not done and distance is smaller than already there
            if dijkstra_table[idx_expand][2] == 0 \
                and dijkstra_table[idx_expand][0] > estimated_total:
                dijkstra_table[idx_expand] = [distance, next_idx, 0, estimated_total]


def check_admissablity(djakstrar_table, heuristics):
    # Every distance should be bigger than the heuristic
    # TODO: FIX
    return np.all(heuristics <= djakstrar_table[:, 0])