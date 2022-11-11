from .salesman import get_salesman_directions


def solve(data):
    game = Game(data)
    dirs = game.let_pacman_collect_all_coins()
    return "".join(dirs)


class Game:
    # +-> col
    # |
    # v row

    def __init__(self, data):
        self.reset(data)

    def reset(self, data):
        self.matrix = data["boardMatrix"]
        self.n = len(self.matrix)

        # number of playing characters
        self.nchars = 1 + len(data["ghosts"])

        # let them all be at movement step 0
        self.movi = [0] * self.nchars
        # let them all be alive
        self.health = [True] * self.nchars

        # transform pacman and ghost positions to 0-based index notation
        self.pos = []
        self.mov = []

        # place pacman position
        pacman = (data["pacmanRow"] - 1, data["pacmanColumn"] - 1)
        self.pos.append(pacman)
        self.mov.append(data["movementPacman"])

        # place ghost position
        for ghost in data["ghosts"]:
            ghost_pos = (ghost["ghostRow"] - 1, ghost["ghostColumn"] - 1)
            self.pos.append(ghost_pos)
            self.mov.append(ghost["movementGhosts"])

        # coins collected
        self.coins = set()

    def play(self):
        tick = 1
        while self.is_char_alive(0) and self.has_char_steps(0):
            tick += 1
            print(f"\n. game tick {tick} .")

            # step all characters
            for ci in range(self.nchars):
                if self.is_char_alive(ci):
                    self.step_char(ci)

            # check for collisions
            self.check_pacman_collisions()

            # possibly collect the coin at this location
            if self.is_char_alive(0):
                self.check_pacman_collected_coin()

    def check_pacman_collected_coin(self):
        row, col = self.pos[0]
        if self.matrix[row][col] == "C":
            self.coins.add((row, col))

    def check_pacman_collisions(self):
        # check if pacman collided with any ghost
        pr, pc = self.pos[0]
        for g in range(1, self.nchars):
            gr, gc = self.pos[g]
            if pr == gr and pc == gc:
                self.health[0] = False
                print(f"pacman at f{(pr, pc)} collided with ghost {g} at {(gr, gc)}")

        # check if pacman ran into a wall
        if self.is_char_in_wall(0):
            self.health[0] = False
            print(f"pacman at {(pr, pc)} ran into a wall")

    def is_char_alive(self, ci):
        return self.health[ci]

    def is_char_in_wall(self, ci):
        row, col = self.pos[ci]
        return self.matrix[row][col] == "W"

    def has_char_steps(self, ci):
        return self.movi[ci] < len(self.mov[ci])

    def step_char(self, ci):
        assert 0 <= ci < len(self.pos)

        if not self.has_char_steps(ci):
            print(f"char {ci} has no more moves")
            return

        next_move = self.mov[ci][self.movi[ci]]
        self._move_char_in_direction(ci, next_move)
        self.movi[ci] += 1

        print(f"stepped {ci:3d} to {str(self.pos[ci]):10s} [{next_move}]")

    def let_pacman_collect_all_coins(self):
        full_cycle = get_salesman_directions(self)
        total_coins = "".join(self.matrix).count("C")

        directions = []
        for d in full_cycle:
            self._move_char_in_direction(0, d)
            directions.append(d)
            self.check_pacman_collected_coin()

            if len(self.coins) == total_coins:
                break

        print(directions)
        return directions

    def _move_char_in_direction(self, ci, direction):
        assert 0 <= ci < len(self.pos)

        row, col = self.pos[ci]
        self.pos[ci] = self._move_row_col(row, col, direction)

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

    def _valid_neighbors_row_col(self, r, c):
        # up, right, down, left neighbors without walls
        neighbors = []
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            # check bounds
            if (
                0 <= r + dr < self.n
                and 0 <= c + dc < self.n
                and self.matrix[r + dr][c + dc] != "W"
            ):
                neighbors.append((r + dr, c + dc))
        return neighbors

    def _diagnostic(self):
        print(f"{self.pos=}")
        print(f"{self.mov=}")
        print(f"{self.movi=}")
        print(f"{self.health=}")
        print(f"{self.coins=} [len={len(self.coins)}]")
