from .salesman import get_salesman_directions

from queue import PriorityQueue
from copy import deepcopy
from tqdm.auto import tqdm


def solve(data):
    game = Game(data)
    game.play()
    # dirs = game.let_pacman_collect_all_coins()
    return "0"


class Game:
    # +-> col
    # |
    # v row

    def __init__(self, data):
        self.state = {
            "pos": None,  # character positions
            "movi": None,  # movement index
            "movr": None,  # movement direction
            "health": None,  # character health
            "coins": None,  # collected coins
        }

        self.reset(data)

    def reset(self, data):
        self.matrix = data["boardMatrix"]
        self.n = len(self.matrix)
        self.total_coins = "".join(self.matrix).count("C")

        # number of playing characters
        self.nchars = 1 + len(data["ghosts"])

        # let them all be at movement step 0
        # facing in the positive direction ("not reverse")
        self.state["movi"] = [0] * self.nchars
        self.state["movr"] = [True] * self.nchars
        # let them all be alive
        self.state["health"] = [True] * self.nchars

        # transform pacman and ghost positions to 0-based index notation
        self.state["pos"] = []
        self.mov = []

        # place pacman position
        pacman = (data["pacmanRow"] - 1, data["pacmanColumn"] - 1)
        self.state["pos"].append(pacman)
        self.mov.append(data["movementPacman"])

        # place ghost position
        for ghost in data["ghosts"]:
            ghost_pos = (ghost["ghostRow"] - 1, ghost["ghostColumn"] - 1)
            self.state["pos"].append(ghost_pos)
            self.mov.append(ghost["movementGhosts"])

        # coins collected
        self.state["coins"] = set()

    def play(self):
        tick = 1
        while tick < 100:
            tick += 1
            print(f"\n. game tick {tick} .")

            # step all ghost characters
            for ci in range(1, self.nchars):
                if self.is_char_alive(ci):
                    self.step_char(ci)

            # check for collisions
            self.check_pacman_collisions()

            # possibly collect the coin at this location
            if self.is_char_alive(0):
                self.check_pacman_collected_coin()

    def single_tick(self, pacman_move):
        # step all ghost characters
        for ci in range(1, self.nchars):
            if self.is_char_alive(ci):
                self.step_char(ci)

        # step pacman
        self._move_char_in_direction(0, pacman_move)

        # check for collisions
        self.check_pacman_collisions()

        # possibly collect the coin at this location
        if self.is_char_alive(0):
            self.check_pacman_collected_coin()

    def check_pacman_collected_coin(self):
        row, col = self.state["pos"][0]
        if self.matrix[row][col] == "C":
            self.state["coins"].add((row, col))

    def check_pacman_collisions(self):
        # check if pacman collided with any ghost
        pr, pc = self.state["pos"][0]
        for g in range(1, self.nchars):
            gr, gc = self.state["pos"][g]
            if pr == gr and pc == gc:
                self.state["health"][0] = False
                print(f"pacman at f{(pr, pc)} collided with ghost {g} at {(gr, gc)}")

        # check if pacman ran into a wall
        if self.is_char_in_wall(0):
            self.state["health"][0] = False
            print(f"pacman at {(pr, pc)} ran into a wall")

    def is_char_alive(self, ci):
        return self.state["health"][ci]

    def is_char_in_wall(self, ci):
        row, col = self.state["pos"][ci]
        return self.matrix[row][col] == "W"

    def has_char_steps(self, ci):
        if self.state["movr"][ci]:
            return self.state["movi"][ci] < len(self.mov[ci])
        else:
            return self.state["movi"][ci] >= 0

    def step_char(self, ci):
        assert 0 <= ci < len(self.state["pos"])

        # possibly turn around
        if not self.has_char_steps(ci):
            self.state["movr"][ci] = not self.state["movr"][ci]
            self.state["movi"][ci] += 1 if self.state["movr"][ci] else -1

        next_move = self.mov[ci][self.state["movi"][ci]]

        # possibly invert direction
        if not self.state["movr"][ci]:
            next_move = self._invert_direction(next_move)

        self._move_char_in_direction(ci, next_move)
        self.state["movi"][ci] += 1 if self.state["movr"][ci] else -1

        print(f"stepped {ci:3d} to {str(self.state['pos'][ci]):10s} [{next_move}]")

    def solve_optimal_route(self):
        (total_coins, goal), parents = self.astar_search(deepcopy(self.state))
        print(total_coins)

    def astar_search(self, start):
        openpq = PriorityQueue()
        openpq.put((0, start))
        closed = {start: 0}

        # remember parents for backtracking
        parents = {start: None}
        total_coins, goal = None, None

        with tqdm(unit="states") as pbar:
            while not openpq.empty():
                total_coins, current = openpq.get()
                if self.is_goal_state(current):
                    goal = current
                    break

                pbar.set_postfix(total_coins=total_coins, refresh=False)
                pbar.update()

                for coins, succ in self.get_valid_pacman_moves(current):
                    new_coins = closed[current] + coins
                    if succ not in closed or new_coins > closed[succ]:
                        parents[succ] = current
                        closed[succ] = new_coins
                        estimate = new_coins + self.estimate_remaining_coins(succ)
                        openpq.put((estimate, succ))

        return (total_coins, goal), parents

    def is_goal_state(self, state):
        return len(state["coins"]) == self.total_coins

    def get_valid_pacman_moves(self, state):
        oldcoins = len(state["coins"])
        valid_moves = []

        # backup state and overwrite it for now
        backup = deepcopy(self.state)
        self.state = deepcopy(state)

        for d in "UDLR":
            if self._is_valid_pacman_move(d):
                self.single_tick(d)
                if self.is_char_alive(0):
                    newcoins = len(self.state["coins"])
                    valid_moves.append((newcoins - oldcoins, deepcopy(self.state)))

        # recover original state
        self.state = backup

        return valid_moves

    def estimate_remaining_coins(self, state):
        return len(state["coins"])

    def let_pacman_collect_all_coins(self):
        full_cycle = get_salesman_directions(self)
        total_coins = "".join(self.matrix).count("C")

        directions = []
        for d in full_cycle:
            self._move_char_in_direction(0, d)
            directions.append(d)
            self.check_pacman_collected_coin()

            if len(self.state["coins"]) == total_coins:
                break

        print(directions)
        return directions

    def _move_char_in_direction(self, ci, direction):
        assert 0 <= ci < len(self.state["pos"])

        row, col = self.state["pos"][ci]
        self.state["pos"][ci] = self._move_row_col(row, col, direction)

    def _move_row_col(self, row, col, direction):
        if direction == "L":
            col -= 1
        elif direction == "R":
            col += 1
        elif direction == "U":
            row -= 1
        elif direction == "D":
            row += 1
        else:
            raise ValueError(f"invalid direction: {direction}")
        return row, col

    def _invert_direction(self, direction):
        if direction == "L":
            return "R"
        elif direction == "R":
            return "L"
        elif direction == "U":
            return "D"
        elif direction == "D":
            return "U"
        else:
            raise ValueError(f"invalid direction: {direction}")

    def _valid_neighbors_row_col(self, r, c):
        # up, right, down, left neighbors without walls or ghosts
        avoid = {"W", "G"}
        neighbors = []
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            # check bounds
            if (
                0 <= r + dr < self.n
                and 0 <= c + dc < self.n
                and self.matrix[r + dr][c + dc] not in avoid
            ):
                neighbors.append((r + dr, c + dc))
        return neighbors

    def _is_valid_pacman_move(self, direction):
        row, col = self.state["pos"][0]
        row, col = self._move_row_col(row, col, direction)
        return self.matrix[row][col] not in {"W", "G"}

    def _diagnostic(self):
        print(f"{self.state['pos']=}")
        print(f"{self.mov=}")
        print(f"{self.state['movi']=}")
        print(f"{self.state['health']=}")
        print(f"{self.state['coins']=} [len={len(self.state['coins'])}]")
