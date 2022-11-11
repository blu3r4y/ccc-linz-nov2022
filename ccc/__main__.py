from pprint import pprint
from pathlib import Path

from loguru import logger as log

from .contest import solve


def load(data):
    n = int(data[0])
    matrix = data[1 : n + 1]

    pacman_pos = tuple(map(int, data[n + 1].split()))
    pacman_seq_len = int(data[n + 2])
    pacman_movement = data[n + 3]

    ghosts_num = int(data[n + 4])
    ghosts = []
    for g in range(ghosts_num):
        ghost_pos = tuple(map(int, data[n + 5 + g * 3].split()))
        ghost_seq_len = int(data[n + 6 + g * 3])
        ghost_movement = data[n + 7 + g * 3]
        ghosts.append(
            {
                "ghostRow": ghost_pos[0],
                "ghostColumn": ghost_pos[1],
                "sequenceLengthGhosts": ghost_seq_len,
                "movementGhosts": ghost_movement,
            }
        )

    return {
        "N": n,
        "boardMatrix": matrix,
        "pacmanRow": pacman_pos[0],
        "pacmanColumn": pacman_pos[1],
        "sequenceLengthPacman": pacman_seq_len,
        "movementPacman": pacman_movement,
        "numberOfGhosts": ghosts_num,
        "ghosts": ghosts,
    }


if __name__ == "__main__":
    level, quests = 3, 7
    for quest in [7]:# range(quests + 1):
        base_path = Path("data")
        input_file = base_path / f"level{level}_{quest}.in"
        output_file = input_file.with_suffix(".out")

        if not input_file.exists():
            log.warning(f"file not found, skip: {input_file}")
            continue

        with open(input_file, "r") as fi:
            data = load(fi.read().splitlines())
            pprint(data)

            print("=== Input {}".format(quest))
            print("======================")

            result = solve(data)
            pprint(result)

            with open(output_file, "w+") as fo:
                fo.write(result)
