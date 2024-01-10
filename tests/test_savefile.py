from grasim.savefile import parse_text
import numpy as np

def test_minimal():
    graph = parse_text(
        """
A -1- B
START A
END B
        """.split("\n")
    )
    assert (graph.graph_matrix == np.array([[0, 1], [1, 0]])).all()

def test_minimal_directed_left():
    graph = parse_text(
        """
A -1-> B
START A
END B
        """.split("\n")
    )
    assert (graph.graph_matrix == np.array([[0, 1], [0, 0]])).all()

def test_minimal_directed_right():
    graph = parse_text(
        """
A <-1- B
START A
END B
        """.split("\n")
    )
    assert (graph.graph_matrix == np.array([[0, 0], [1, 0]])).all()

def test_minimal_directed_seperate_double():
    graph = parse_text(
        """
A <-2- B
A -1-> B
START A
END B
        """.split("\n")
    )
    assert (graph.graph_matrix == np.array([[0, 2], [1, 0]])).all()