def solve(data):
    game = Game(data)
    ncoins = game.collect_coins(data["movement"])
    return str(ncoins)


class Game:
    # --> col
    # |
    # v
    # row

    def __init__(self, data):
        self.matrix = data["boardMatrix"]
        self.pacman = (data["pacmanRow"] - 1, data["pacmanColumn"] - 1)

    def move(self, direction):
        row, col = self.pacman
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
        print(f"got {direction} - moving to {row}, {col}")
        self.pacman = (row, col)

    def collect_coins(self, movement):
        collected = set()
        for m in movement:
            self.move(m)
            if self.matrix[self.pacman[0]][self.pacman[1]] == "C":
                print(f"coint at {self.pacman}")
                collected.add(self.pacman)

        return len(collected)
