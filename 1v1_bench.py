import importlib
import os
import pkgutil
import random
import re
from dataclasses import dataclass
from typing import Optional

import numpy as np

from Bots.ChessBotList import CHESS_BOT_LIST
from ChessRules import move_is_valid

T_BUDGET = 0.2
BOT1_NAME = "TigreBot"
BOT2_NAME = "ChaiseBotV5"
NUM_DUELS = 10
MAX_PLIES = 200
REPETITION_WINDOW = 8
RESULTS_PATH = os.path.join("Logs", f"1v1_{BOT1_NAME}_{BOT2_NAME}.txt")
BOARD_PATH = os.path.join("Data", "maps", "default.brd")

# CHESS rules variants:
# - capture the king (wins when opp king is captured)
# - no double move from pawns at start square
# - queen auto promotion
# - no castle

# BOARD orientation:
# - always in the orientation of the playing bot
# - the moves are always in the board orientation (which means the playing bot orientation)


@dataclass
class SimplePiece:
    type: str
    color: str

    def string(self) -> str:
        return f"{self.type}{self.color}"

    def __getitem__(self, idx):
        return self.string()[idx]

    def __len__(self):
        return len(self.string())

    def __eq__(self, value):
        if isinstance(value, str):
            return self.string() == value
        return False

    def __ne__(self, value):
        if isinstance(value, str):
            return self.string() != value
        return not self.__eq__(value)


def load_all_bots():
    import Bots
    for _, module_name, _ in pkgutil.iter_modules(Bots.__path__):
        importlib.import_module(f"Bots.{module_name}")


def load_board(path: str) -> tuple[np.ndarray, str]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Board file '{path}' not found")

    ext = os.path.splitext(path)[1].lower()
    with open(path, "r", encoding="utf-8") as handle:
        data = handle.read().strip()

    if ext == ".brd":
        lines = [line.strip() for line in data.split("\n") if line.strip()]
        player_order = lines[0]
        rows = [line.replace("--", "").split(",") for line in lines[1:]]
        height = len(rows)
        width = len(rows[0]) if rows else 0
        board = np.empty((height, width), dtype=object)
        for y, row in enumerate(rows):
            for x, cell in enumerate(row):
                cell = cell.strip()
                if cell == "":
                    board[y, x] = ""
                elif cell == "XX":
                    board[y, x] = "XX"
                else:
                    board[y, x] = SimplePiece(cell[0], cell[1])
        return board, player_order

    if ext == ".fen":
        parts = data.split(" ")
        board_desc = parts[0]
        rows_desc = board_desc.split("/")
        rows = []
        regexp = r"^|(?=\\D)|(?<=\\D)(?=\\d)|$"
        for row_desc in rows_desc:
            matches = list(re.finditer(regexp, row_desc))
            row = []
            for i in range(len(matches) - 1):
                m1 = matches[i]
                m2 = matches[i + 1]
                part = row_desc[m1.start():m2.start()]
                if part.isnumeric():
                    row += [""] * int(part)
                else:
                    color = "w" if part.isupper() else "b"
                    piece = part.lower()
                    row.append(SimplePiece(piece, color))
            rows.append(row)
        board = np.array(rows, dtype=object)
        next_player = parts[1] if len(parts) > 1 else "w"
        player_order = "0w01b2" if next_player == "w" else "0b01w2"
        if next_player == "w":
            board = np.rot90(board, 2)
        return board, player_order

    raise ValueError(f"Unsupported board extension '{ext}'")


def board_to_string(board: np.ndarray) -> np.ndarray:
    res = []
    for r in board:
        line = []
        for c in r:
            if isinstance(c, SimplePiece):
                line.append(c.string())
            else:
                line.append(c)
        res.append(line)
    return np.array(res, dtype=object)


def get_sequence(player_order: str, turn: int, full: bool = False) -> str:
    if full:
        start = player_order[: 3 * turn]
        end = player_order[3 * turn :]
        return end + start
    return player_order[3 * turn : 3 * turn + 3]


def is_king_captured(board: np.ndarray, color: str) -> bool:
    for y in range(board.shape[0]):
        for x in range(board.shape[1]):
            piece = board[y, x]
            if isinstance(piece, SimplePiece) and piece.type == "k" and piece.color == color:
                return False
    return True


def pat_with_repetitive_moves(moves_buffer, window: int) -> bool:
    if len(moves_buffer) < window:
        return False
    tail = moves_buffer[-window:]
    half = window // 2
    return tail[:half] == tail[half:]


def apply_move(board: np.ndarray, move, player_sequence_full: str) -> bool:
    if not move_is_valid(player_sequence_full, move, board):
        return False

    start, end = move
    moving_piece = board[start[0], start[1]]
    board[end[0], end[1]] = moving_piece
    board[start[0], start[1]] = ""

    if (
        isinstance(moving_piece, SimplePiece)
        and moving_piece.type == "p"
        and end[0] == board.shape[0] - 1
    ):
        moving_piece.type = "q"
    return True


def play_single_game(
    bot_names,
    time_budget: float,
    board_path: str,
    max_plies: int,
    repetition_window: int,
) -> tuple[Optional[str], Optional[str]]:
    board, player_order = load_board(board_path)
    turn = 0
    moves_buffer = []

    for _ in range(max_plies):
        sequence = get_sequence(player_order, turn)
        sequence_full = get_sequence(player_order, turn, full=True)
        rot = int(sequence[2])
        oriented_board = np.rot90(board, rot)
        bot_name = bot_names[turn]
        bot_fn = CHESS_BOT_LIST[bot_name]

        move = bot_fn(sequence, board_to_string(oriented_board), time_budget)
        if (
            not isinstance(move, tuple)
            or len(move) != 2
            or not all(isinstance(p, tuple) and len(p) == 2 for p in move)
        ):
            return bot_names[(turn + 1) % len(bot_names)], None

        if not apply_move(oriented_board, move, sequence_full):
            return bot_names[(turn + 1) % len(bot_names)], None

        moves_buffer.append((turn, move))
        if pat_with_repetitive_moves(moves_buffer, repetition_window):
            return None, "repetition"

        opponent_color = get_sequence(player_order, (turn + 1) % len(bot_names))[1]
        if is_king_captured(board, opponent_color):
            return bot_name, None

        turn = (turn + 1) % len(bot_names)

    return None, "max_plies"


def main(
    time_budget: float = T_BUDGET,
    bot1_name: str = BOT1_NAME,
    bot2_name: str = BOT2_NAME,
    num_duels: int = NUM_DUELS,
    results_path: str = RESULTS_PATH,
    board_path: str = BOARD_PATH,
    max_plies: int = MAX_PLIES,
    repetition_window: int = REPETITION_WINDOW,
):
    load_all_bots()
    for bot_name in (bot1_name, bot2_name):
        if bot_name not in CHESS_BOT_LIST:
            available = ", ".join(sorted(CHESS_BOT_LIST.keys()))
            raise ValueError(f"Bot '{bot_name}' not found. Available: {available}")

    results = {
        bot1_name: {
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "wins_first": 0,
            "wins_second": 0,
            "losses_first": 0,
            "losses_second": 0,
            "draws_first": 0,
            "draws_second": 0,
            "draws_repetition": 0,
            "draws_max_plies": 0,
            "draws_repetition_first": 0,
            "draws_repetition_second": 0,
            "draws_max_plies_first": 0,
            "draws_max_plies_second": 0,
        },
        bot2_name: {
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "wins_first": 0,
            "wins_second": 0,
            "losses_first": 0,
            "losses_second": 0,
            "draws_first": 0,
            "draws_second": 0,
            "draws_repetition": 0,
            "draws_max_plies": 0,
            "draws_repetition_first": 0,
            "draws_repetition_second": 0,
            "draws_max_plies_first": 0,
            "draws_max_plies_second": 0,
        },
    }
    draw_reasons = {"repetition": 0, "max_plies": 0}

    for _ in range(num_duels):
        if random.choice([True, False]):
            duel_bots = [bot1_name, bot2_name]
        else:
            duel_bots = [bot2_name, bot1_name]

        starting_bot = duel_bots[0]
        winner, draw_reason = play_single_game(
            duel_bots, time_budget, board_path, max_plies, repetition_window
        )

        if winner is None:
            results[bot1_name]["draws"] += 1
            results[bot2_name]["draws"] += 1
            if starting_bot == bot1_name:
                results[bot1_name]["draws_first"] += 1
                results[bot2_name]["draws_second"] += 1
            else:
                results[bot2_name]["draws_first"] += 1
                results[bot1_name]["draws_second"] += 1
            if draw_reason in draw_reasons:
                draw_reasons[draw_reason] += 1
                for bot_name in (bot1_name, bot2_name):
                    results[bot_name][f"draws_{draw_reason}"] += 1
                if starting_bot == bot1_name:
                    results[bot1_name][f"draws_{draw_reason}_first"] += 1
                    results[bot2_name][f"draws_{draw_reason}_second"] += 1
                else:
                    results[bot2_name][f"draws_{draw_reason}_first"] += 1
                    results[bot1_name][f"draws_{draw_reason}_second"] += 1
        else:
            loser = bot1_name if winner == bot2_name else bot2_name
            results[winner]["wins"] += 1
            results[loser]["losses"] += 1
            if winner == starting_bot:
                results[winner]["wins_first"] += 1
                results[loser]["losses_second"] += 1
            else:
                results[winner]["wins_second"] += 1
                results[loser]["losses_first"] += 1

    lines = [
        f"//////////////////////////////////////////////////////////////////////",
        f"1v1 benchmark: {bot1_name} vs {bot2_name}",
        (
            f"duels={num_duels}, time_budget={time_budget}s, max_plies={max_plies}, "
            f"draws: repetition={draw_reasons['repetition']}, max_plies={draw_reasons['max_plies']}"
        ),
        (
            f"{bot1_name}: wins={results[bot1_name]['wins']} "
            f"(1st: {results[bot1_name]['wins_first']}, 2nd: {results[bot1_name]['wins_second']}), "
            f"losses={results[bot1_name]['losses']} "
            f"(1st: {results[bot1_name]['losses_first']}, 2nd: {results[bot1_name]['losses_second']}), "
            f"draws={results[bot1_name]['draws']} "
            f"(1st: {results[bot1_name]['draws_first']}, 2nd: {results[bot1_name]['draws_second']}), "
            f"draws_repetition={results[bot1_name]['draws_repetition']} "
            f"(1st: {results[bot1_name]['draws_repetition_first']}, "
            f"2nd: {results[bot1_name]['draws_repetition_second']}), "
            f"draws_max_plies={results[bot1_name]['draws_max_plies']} "
            f"(1st: {results[bot1_name]['draws_max_plies_first']}, "
            f"2nd: {results[bot1_name]['draws_max_plies_second']})"
        ),
        (
            f"{bot2_name}: wins={results[bot2_name]['wins']} "
            f"(1st: {results[bot2_name]['wins_first']}, 2nd: {results[bot2_name]['wins_second']}), "
            f"losses={results[bot2_name]['losses']} "
            f"(1st: {results[bot2_name]['losses_first']}, 2nd: {results[bot2_name]['losses_second']}), "
            f"draws={results[bot2_name]['draws']} "
            f"(1st: {results[bot2_name]['draws_first']}, 2nd: {results[bot2_name]['draws_second']}), "
            f"draws_repetition={results[bot2_name]['draws_repetition']} "
            f"(1st: {results[bot2_name]['draws_repetition_first']}, "
            f"2nd: {results[bot2_name]['draws_repetition_second']}), "
            f"draws_max_plies={results[bot2_name]['draws_max_plies']} "
            f"(1st: {results[bot2_name]['draws_max_plies_first']}, "
            f"2nd: {results[bot2_name]['draws_max_plies_second']})"
        ),
        "",
    ]

    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    with open(results_path, "a", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    print("\n".join(lines[:-1]))


if __name__ == "__main__":
    main()
