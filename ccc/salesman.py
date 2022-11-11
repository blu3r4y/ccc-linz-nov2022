import networkx as nx
import matplotlib.pyplot as plt
from collections import deque


def get_salesman_directions(game):
    # build game graph
    G = nx.Graph()

    valid_cells = ("C", "P")
    for r in range(game.n):
        for c in range(game.n):
            if game.matrix[r][c] in valid_cells:
                G.add_node((r, c))
                for (nr, nc) in game._valid_neighbors_row_col(r, c):
                    if game.matrix[nr][nc] in valid_cells:
                        G.add_edge((r, c), (nr, nc))

    # position of pacman
    pacman = game.pos[0]

    # solve traveling salesman problem
    tsp = nx.approximation.traveling_salesman_problem
    cycle = tsp(G, cycle=True)

    # rotate cycle to start at pacman position
    cycle = deque(cycle)
    cycle.rotate(-cycle.index(pacman))
    # print(list(cycle))

    # convert list of nodes to directional moves
    directions = _node_list_to_directions(cycle)
    return directions

    # check that directions are valid
    #
    # checksum = [pacman]
    # for d in directions:
    #     r, c = checksum[-1]
    #     checksum.append(_debug_move_row_col(r, c, d))
    # print(checksum)

    # nx.draw_spring(G, with_labels=True)
    # plt.show()


def _node_list_to_directions(nodes):
    result = []

    cur = nodes[0]
    for i in range(1, len(nodes)):
        nxt = nodes[i]

        # check for nop
        if cur[0] == nxt[0] and cur[1] == nxt[1]:
            continue

        if cur[0] == nxt[0]:
            if cur[1] < nxt[1]:
                result.append("R")
            else:
                result.append("L")
        elif cur[1] == nxt[1]:
            if cur[0] < nxt[0]:
                result.append("D")
            else:
                result.append("U")
        else:
            raise ValueError(f"invalid diagonal move")

        cur = nxt

    return result


# def _debug_move_row_col(row, col, direction):
#     if direction == "L":
#         col -= 1
#     elif direction == "R":
#         col += 1
#     elif direction == "U":
#         row -= 1
#     elif direction == "D":
#         row += 1
#     else:
#         raise ValueError(f"invalid direction: {direction}")
#     return row, col
