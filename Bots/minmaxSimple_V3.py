from Bots.ChessBotList import register_chess_bot

import time
import math

def minMaxBot(player_sequence, board, time_budget, **kwargs):
    startTime = time.time()
    # player_squence => [teamid|color|boardorientation]

    # board          => 2x2 array containing either: 
    #                   "" => no pieces
    #                   "pc" => piece/color (rw = rook white)
    #                   "X" => not accessible

    # Told us not to worry about the orientation, so I our case:
    # the x axis is the vertical one
    # the y axis is the horizontal one
    # both starting at (0, 0) in the bottom right of our board.

    our_color = player_sequence[1]
    enemy_color = "w" if our_color != "w" else "b"

    basePieceValues = {
        "p" : 1,
        "n" : 3.2,
        "r" : 5.1,
        "b" : 3.33,
        "q" : 8.8,
        "k" : 100
    }
    baseMoveValues = {
        # Simple moves
        "mp": 0.1,
        "mn": 0.2,
        "mb": 0.2,
        "mr": 0.2,
        "mq": 0.15,
        "mk": 0.05,

        # Specials
        "pup" : 10.0
    }

    # Tables indexees en [x][y] avec (0,0) en bas a droite.
    # x monte vers le haut, y va vers la gauche.
    position_bonus = {
        "n": {
            "start": [
                [ -5, -4, -3, -3, -3, -3, -4, -5],
                [ -4, -2,  0,  0.5, 0.5,  0, -2, -4],
                [ -3,  0,  1,  1.5, 1.5, 1,  0, -3],
                [ -3,  0.5, 1.5, 2,   2,   1.5, 0.5, -3],
                [ -3,  0.5, 1.5, 2,   2,   1.5, 0.5, -3],
                [ -3,  0,  1,  1.5, 1.5, 1,  0, -3],
                [ -4, -2,  0,  0.5, 0.5, 0, -2, -4],
                [ -5, -4, -3, -3, -3, -3, -4, -5]
            ],
            "end": [
                [ -4, -3, -2, -2, -2, -2, -3, -4],
                [ -3, -1,  0,  0.5, 0.5, 0, -1, -3],
                [ -2,  0,  1.5, 2,   2,   1.5, 0, -2],
                [ -2,  0.5, 2,  2.5, 2.5, 2,  0.5, -2],
                [ -2,  0.5, 2,  2.5, 2.5, 2,  0.5, -2],
                [ -2,  0,  1.5, 2,   2,   1.5, 0, -2],
                [ -3, -1,  0,  0.5, 0.5, 0, -1, -3],
                [ -4, -3, -2, -2, -2, -2, -3, -4]
            ]
        },
        "k": {
            "start": [
                [ 2, 3, 1, 0, 0, 1, 3, 2],
                [ 2, 2, -0.5, -0.5, -0.5, -0.5, 2, 2],
                [ -1, -2, -2, -2, -2, -2, -2, -1],
                [ -2, -3, -3, -4, -4, -3, -3, -2],
                [ -3, -4, -4, -5, -5, -4, -4, -3],
                [ -4, -5, -5, -6, -6, -5, -5, -4],
                [ -6, -6, -6, -6, -6, -6, -6, -6],
                [ -8, -7, -7, -7, -7, -7, -7, -8]
            ],
            "end": [
                [ -3, -2, -1, -1, -1, -1, -2, -3],
                [ -2,  0,  0.5, 0.5, 0.5, 0.5, 0, -2],
                [ -1,  0.5, 1.5, 2,  2,  1.5, 0.5, -1],
                [ -1,  0.5, 2,  2.5, 2.5, 2,  0.5, -1],
                [ -1,  0.5, 2,  2.5, 2.5, 2,  0.5, -1],
                [ -1,  0.5, 1.5, 2,  2,  1.5, 0.5, -1],
                [ -2,  0,  0.5, 0.5, 0.5, 0.5, 0, -2],
                [ -3, -2, -1, -1, -1, -1, -2, -3]
            ]
        },
        "p": {
            "start": [
                [ 0, 0, 0, 0, 0, 0, 0, 0],
                [ 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
                [ 1, 1, 1.5, 2, 2, 1.5, 1, 1],
                [ 1.5, 1.5, 2, 2.5, 2.5, 2, 1.5, 1.5],
                [ 2, 2, 2.5, 3, 3, 2.5, 2, 2],
                [ 2.5, 2.5, 3, 3.5, 3.5, 3, 2.5, 2.5],
                [ 3, 3, 3, 3, 3, 3, 3, 3],
                [ 0, 0, 0, 0, 0, 0, 0, 0]
            ],
            "end": [
                [ 0, 0, 0, 0, 0, 0, 0, 0],
                [ 1, 1, 1, 1, 1, 1, 1, 1],
                [ 2, 2.5, 3, 3.5, 3.5, 3, 2.5, 2],
                [ 3, 3.5, 4, 4.5, 4.5, 4, 3.5, 3],
                [ 4, 4.5, 5, 5.5, 5.5, 5, 4.5, 4],
                [ 5, 5.5, 6, 6.5, 6.5, 6, 5.5, 5],
                [ 7, 7, 7, 7, 7, 7, 7, 7],
                [ 0, 0, 0, 0, 0, 0, 0, 0]
            ]
        },
        "b": {
            "start": [
                [ -2, -1, -1, -1, -1, -1, -1, -2],
                [ -1,  0,  0.5, 0.5, 0.5, 0.5, 0, -1],
                [ -1,  0.5, 1,  1.5, 1.5, 1,  0.5, -1],
                [ -1,  0.5, 1.5, 2,  2,  1.5, 0.5, -1],
                [ -1,  0.5, 1.5, 2,  2,  1.5, 0.5, -1],
                [ -1,  0.5, 1,  1.5, 1.5, 1,  0.5, -1],
                [ -1,  0,  0.5, 0.5, 0.5, 0.5, 0, -1],
                [ -2, -1, -1, -1, -1, -1, -1, -2]
            ],
            "end": [
                [ -1, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -1],
                [ -0.5,  0,  0.5,  1,  1,  0.5,  0, -0.5],
                [ -0.5,  0.5,  1.5, 2,  2,  1.5, 0.5, -0.5],
                [ -0.5,  1,  2,  2.5, 2.5, 2,  1, -0.5],
                [ -0.5,  1,  2,  2.5, 2.5, 2,  1, -0.5],
                [ -0.5,  0.5,  1.5, 2,  2,  1.5, 0.5, -0.5],
                [ -0.5,  0,  0.5,  1,  1,  0.5,  0, -0.5],
                [ -1, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -1]
            ]
        },
        "r": {
            "start": [
                [ 0, 0, 0, 0, 0, 0, 0, 0],
                [ 0, 0.5, 0.5, 1, 1, 0.5, 0.5, 0],
                [ 0, 1, 1.5, 2, 2, 1.5, 1, 0],
                [ 0, 1, 1.5, 2, 2, 1.5, 1, 0],
                [ 0, 1, 1.5, 2, 2, 1.5, 1, 0],
                [ 0, 1, 1.5, 2, 2, 1.5, 1, 0],
                [ 0, 1, 1, 1.5, 1.5, 1, 1, 0],
                [ 0, 0, 0, 0, 0, 0, 0, 0]
            ],
            "end": [
                [ 0, 0.5, 0.5, 1, 1, 0.5, 0.5, 0],
                [ 0, 1, 1.5, 2, 2, 1.5, 1, 0],
                [ 0, 1.5, 2.5, 3, 3, 2.5, 1.5, 0],
                [ 0, 1.5, 2.5, 3, 3, 2.5, 1.5, 0],
                [ 0, 1.5, 2.5, 3, 3, 2.5, 1.5, 0],
                [ 0, 1.5, 2.5, 3, 3, 2.5, 1.5, 0],
                [ 0.5, 2, 2.5, 3, 3, 2.5, 2, 0.5],
                [ 0, 0.5, 0.5, 1, 1, 0.5, 0.5, 0]
            ]
        },
        "q": {
            "start": [
                [ -2, -1, -1, -1, -1, -1, -1, -2],
                [ -1,  0,  0,  0,  0,  0,  0, -1],
                [ -1,  0,  0.5, 0.5, 0.5, 0.5, 0, -1],
                [ -1,  0,  0.5, 1,  1,  0.5, 0, -1],
                [ -1,  0,  0.5, 1,  1,  0.5, 0, -1],
                [ -1,  0,  0.5, 0.5, 0.5, 0.5, 0, -1],
                [ -1,  0,  0,  0,  0,  0,  0, -1],
                [ -2, -1, -1, -1, -1, -1, -1, -2]
            ],
            "end": [
                [ -1, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -1],
                [ -0.5,  0,  0.5,  1,  1,  0.5,  0, -0.5],
                [ -0.5,  0.5,  1.5, 2,  2,  1.5, 0.5, -0.5],
                [ -0.5,  1,  2,  2.5, 2.5, 2,  1, -0.5],
                [ -0.5,  1,  2,  2.5, 2.5, 2,  1, -0.5],
                [ -0.5,  0.5,  1.5, 2,  2,  1.5, 0.5, -0.5],
                [ -0.5,  0,  0.5,  1,  1,  0.5,  0, -0.5],
                [ -1, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -1]
            ]
        }
    }

    def piece_pos_bonus(pieceType, pos, enemies_remaining):
        if pieceType not in position_bonus:
            return 0
        max_enemies = 16
        enemies_remaining = max(0, min(max_enemies, enemies_remaining))
        t = 1.0 - (enemies_remaining / max_enemies)
        x, y = pos
        start_val = position_bonus[pieceType]["start"][x][y]
        end_val = position_bonus[pieceType]["end"][x][y]
        return start_val + (end_val - start_val) * t
    
    def double_pawn_penalty(board, pos, color):
        x, y = pos
        if board[x, y] == "p":
            # Check if there's another pawn of the same color in the same column
            for i in range(8):
                if board[i, y] == "p" and i != x:
                    return - 0.5  # Penalty for double pawns
        return 0

    def move_pos_delta(pieceType, from_pos, to_pos, enemies_remaining):
        return (
            piece_pos_bonus(pieceType, to_pos, enemies_remaining)
            - piece_pos_bonus(pieceType, from_pos, enemies_remaining)
        )

    def count_enemies(board, color):
        count = 0
        for i in range(board.shape[0]):
            for j in range(board.shape[1]):
                cell = board[i, j]
                if cell == "" or cell == "X":
                    continue
                if cell[1] != color:
                    count += 1
        return count

    def getAttackedSquares(board, attacker_color):
        attacked = set()

        def isInBounds(x, y):
            return 0 <= x <= 7 and 0 <= y <= 7

        def add_square(x, y):
            if board[x, y] != "X":
                attacked.add((x, y))

        for x in range(board.shape[0]):
            for y in range(board.shape[1]):
                cell = board[x, y]
                if cell == "" or cell == "X":
                    continue
                if cell[1] != attacker_color:
                    continue
                piece = cell[0]
                if piece == "p":
                    dx = 1 if attacker_color == our_color else -1
                    for dy in (-1, 1):
                        nx, ny = x + dx, y + dy
                        if isInBounds(nx, ny):
                            add_square(nx, ny)
                elif piece == "n":
                    for dx, dy in (
                        (2, 1), (2, -1), (-2, 1), (-2, -1),
                        (1, 2), (1, -2), (-1, 2), (-1, -2)
                    ):
                        nx, ny = x + dx, y + dy
                        if isInBounds(nx, ny):
                            add_square(nx, ny)
                elif piece == "k":
                    for dx, dy in (
                        (1, 0), (-1, 0), (0, 1), (0, -1),
                        (1, 1), (1, -1), (-1, 1), (-1, -1)
                    ):
                        nx, ny = x + dx, y + dy
                        if isInBounds(nx, ny):
                            add_square(nx, ny)
                else:
                    if piece in ("b", "q"):
                        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
                    else:
                        directions = []
                    if piece in ("r", "q"):
                        directions += [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        while isInBounds(nx, ny):
                            if board[nx, ny] == "X":
                                break
                            add_square(nx, ny)
                            if board[nx, ny] != "":
                                break
                            nx += dx
                            ny += dy
        return attacked

    def getEnemyThreatBonus(board, enemy_color, friendly_color):
        def isInBounds(x, y):
            return 0 <= x <= 7 and 0 <= y <= 7

        def piece_attacks(pos, piece, color):
            x, y = pos
            attacks = []
            if piece == "p":
                dx = 1 if color == our_color else -1
                for dy in (-1, 1):
                    nx, ny = x + dx, y + dy
                    if isInBounds(nx, ny):
                        attacks.append((nx, ny))
            elif piece == "n":
                for dx, dy in (
                    (2, 1), (2, -1), (-2, 1), (-2, -1),
                    (1, 2), (1, -2), (-1, 2), (-1, -2)
                ):
                    nx, ny = x + dx, y + dy
                    if isInBounds(nx, ny):
                        attacks.append((nx, ny))
            elif piece == "k":
                for dx, dy in (
                    (1, 0), (-1, 0), (0, 1), (0, -1),
                    (1, 1), (1, -1), (-1, 1), (-1, -1)
                ):
                    nx, ny = x + dx, y + dy
                    if isInBounds(nx, ny):
                        attacks.append((nx, ny))
            else:
                directions = []
                if piece in ("b", "q"):
                    directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
                if piece in ("r", "q"):
                    directions.extend([(1, 0), (-1, 0), (0, 1), (0, -1)])
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    while isInBounds(nx, ny):
                        if board[nx, ny] == "X":
                            break
                        attacks.append((nx, ny))
                        if board[nx, ny] != "":
                            break
                        nx += dx
                        ny += dy
            return attacks

        king_pos = None
        for i in range(board.shape[0]):
            for j in range(board.shape[1]):
                cell = board[i, j]
                if cell == "" or cell == "X":
                    continue
                if cell[0] == "k" and cell[1] == friendly_color:
                    king_pos = (i, j)
                    break
            if king_pos is not None:
                break

        king_threat_weight = 0.2
        sensitive_threat_weight = 0.3
        sensitive_types = {"q", "r", "b", "n"}
        threat_bonus = {}

        for i in range(board.shape[0]):
            for j in range(board.shape[1]):
                cell = board[i, j]
                if cell == "" or cell == "X":
                    continue
                if cell[1] != enemy_color:
                    continue
                piece = cell[0]
                bonus = 0
                attacks = piece_attacks((i, j), piece, enemy_color)
                if king_pos is not None and king_pos in attacks:
                    bonus += basePieceValues["k"] * king_threat_weight
                for ax, ay in attacks:
                    target = board[ax, ay]
                    if target == "" or target == "X":
                        continue
                    if target[1] == friendly_color and target[0] in sensitive_types:
                        bonus += basePieceValues[target[0]] * sensitive_threat_weight
                if bonus != 0:
                    threat_bonus[(i, j)] = bonus
        return threat_bonus

    def getAllMoves(board, color):
        enemies_remaining = count_enemies(board, color)
        moveValues = dict(baseMoveValues)
        everyPossibleMove = []
        opponent_color = "w" if color != "w" else "b"
        attacked_squares = getAttackedSquares(board, opponent_color)
        enemy_threat_bonus = getEnemyThreatBonus(board, opponent_color, color)

        def isInBounds(x, y):
            if x < 0 or x > 7:
                return False
            if y < 0 or y > 7:
                return False
            return True

        def attacked_malus(pieceType, dest):
            if dest not in attacked_squares:
                return 0
            return -basePieceValues.get(pieceType, 0)

        def apply_attack_malus(moves, pieceType):
            for move in moves:
                move[0] += attacked_malus(pieceType, move[2])
            return moves

        def getPawnMoves(x, y):
            mp_val = moveValues["mp"]
            pawnMoves = []
            if color == our_color:
                if x + 1 > 7:
                    return pawnMoves
                # Queen upgrade ?
                if x + 1 == 7 and board[x + 1, y] == "":
                    promo_bonus = (
                        piece_pos_bonus("q", (x + 1, y), enemies_remaining)
                        - piece_pos_bonus("p", (x, y), enemies_remaining)
                    )
                    promo_bonus += double_pawn_penalty(board, (x + 1, y), color)
                    pawnMoves.append([moveValues["pup"] + promo_bonus, (x, y), (x + 1, y)])
                # Move forwards ?
                elif board[x + 1, y] == "":
                    bonus = move_pos_delta("p", (x, y), (x + 1, y), enemies_remaining)
                    bonus += double_pawn_penalty(board, (x + 1, y), color)
                    pawnMoves.append([mp_val + bonus, (x, y), (x + 1, y)])
                # Diag attacks ?
                if y + 1 <= 7:
                    if board[x + 1, y + 1] != "" and board[x + 1, y + 1] != "X":
                        if board[x + 1, y + 1][1] != color:
                            bonus = move_pos_delta("p", (x, y), (x + 1, y + 1), enemies_remaining)
                            bonus += double_pawn_penalty(board, (x + 1, y + 1), color)
                            capture_bonus = enemy_threat_bonus.get((x + 1, y + 1), 0)
                            pawnMoves.append([
                                basePieceValues[board[x + 1, y + 1][0]] + capture_bonus + mp_val + bonus,
                                (x, y),
                                (x + 1, y + 1)
                            ])
                if y - 1 >= 0:
                    if board[x + 1, y - 1] != "" and board[x + 1, y - 1] != "X":
                        if board[x + 1, y - 1][1] != color:
                            bonus = move_pos_delta("p", (x, y), (x + 1, y - 1), enemies_remaining)
                            bonus += double_pawn_penalty(board, (x + 1, y - 1), color)
                            capture_bonus = enemy_threat_bonus.get((x + 1, y - 1), 0)
                            pawnMoves.append([
                                basePieceValues[board[x + 1, y - 1][0]] + capture_bonus + mp_val + bonus,
                                (x, y),
                                (x + 1, y - 1)
                            ])
            else:
                if x - 1 < 0:
                    return pawnMoves
                # Queen upgrade ?
                if x - 1 == 0 and board[x - 1, y] == "":
                    promo_bonus = (
                        piece_pos_bonus("q", (x - 1, y), enemies_remaining)
                        - piece_pos_bonus("p", (x, y), enemies_remaining)
                    )
                    promo_bonus += double_pawn_penalty(board, (x - 1, y), color)
                    pawnMoves.append([moveValues["pup"] + promo_bonus, (x, y), (x - 1, y)])
                # Move forwards ?
                elif board[x - 1, y] == "":
                    bonus = move_pos_delta("p", (x, y), (x - 1, y), enemies_remaining)
                    bonus += double_pawn_penalty(board, (x - 1, y), color)
                    pawnMoves.append([mp_val + bonus, (x, y), (x - 1, y)])
                # Diag attacks ?
                if y + 1 <= 7:
                    if board[x - 1, y + 1] != "" and board[x - 1, y + 1] != "X":
                        if board[x - 1, y + 1][1] != color:
                            bonus = move_pos_delta("p", (x, y), (x - 1, y + 1), enemies_remaining)
                            bonus += double_pawn_penalty(board, (x - 1, y + 1), color)
                            capture_bonus = enemy_threat_bonus.get((x - 1, y + 1), 0)
                            pawnMoves.append([
                                basePieceValues[board[x - 1, y + 1][0]] + capture_bonus + mp_val + bonus,
                                (x, y),
                                (x - 1, y + 1)
                            ])
                if y - 1 >= 0:
                    if board[x - 1, y - 1] != "" and board[x - 1, y - 1] != "X":
                        if board[x - 1, y - 1][1] != color:
                            bonus = move_pos_delta("p", (x, y), (x - 1, y - 1), enemies_remaining)
                            bonus += double_pawn_penalty(board, (x - 1, y - 1), color)
                            capture_bonus = enemy_threat_bonus.get((x - 1, y - 1), 0)
                            pawnMoves.append([
                                basePieceValues[board[x - 1, y - 1][0]] + capture_bonus + mp_val + bonus,
                                (x, y),
                                (x - 1, y - 1)
                            ])

            return pawnMoves

        def getKnightMoves(x, y):
            mn_val = moveValues["mn"]
            knightMoves = []
            potentialMoves = [
                (x + 2, y + 1),
                (x + 2, y - 1),
                (x - 2, y + 1),
                (x - 2, y - 1),
                (x + 1, y + 2),
                (x + 1, y - 2),
                (x - 1, y + 2),
                (x - 1, y - 2)
            ]
            for move in potentialMoves:
                if isInBounds(move[0], move[1]):
                    if board[move[0], move[1]] == "" :
                        bonus = move_pos_delta("n", (x, y), (move[0], move[1]), enemies_remaining)
                        knightMoves.append([mn_val + bonus, (x, y), (move[0], move[1])])
                    elif board[move[0], move[1]] == "X":
                        pass
                    elif board[move[0], move[1]][1] != color:
                        bonus = move_pos_delta("n", (x, y), (move[0], move[1]), enemies_remaining)
                        capture_bonus = enemy_threat_bonus.get((move[0], move[1]), 0)
                        knightMoves.append([
                            basePieceValues[board[move[0], move[1]][0]] + capture_bonus + mn_val + bonus,
                            (x, y),
                            (move[0], move[1])
                        ])
            return knightMoves

        def getRookMoves(x, y, isQueen=False):
            rookMoves = []
            mr_val = moveValues["mr"] if not isQueen else moveValues["mq"]
            piece = "q" if isQueen else "r"
            # Up
            for i in range(x + 1, 8):
                if board[i, y] == "":
                    bonus = move_pos_delta(piece, (x, y), (i, y), enemies_remaining)
                    rookMoves.append([mr_val + bonus, (x, y), (i, y)])
                elif board[i, y] == "X":
                    break
                elif board[i, y][1] != color:
                    bonus = move_pos_delta(piece, (x, y), (i, y), enemies_remaining)
                    capture_bonus = enemy_threat_bonus.get((i, y), 0)
                    rookMoves.append([basePieceValues[board[i, y][0]] + capture_bonus + mr_val + bonus, (x, y), (i, y)])
                    break
                else:
                    break
            # Down
            for i in range(x - 1, -1, -1):
                if board[i, y] == "":
                    bonus = move_pos_delta(piece, (x, y), (i, y), enemies_remaining)
                    rookMoves.append([mr_val + bonus, (x, y), (i, y)])
                elif board[i, y] == "X":
                    break
                elif board[i, y][1] != color:
                    bonus = move_pos_delta(piece, (x, y), (i, y), enemies_remaining)
                    capture_bonus = enemy_threat_bonus.get((i, y), 0)
                    rookMoves.append([basePieceValues[board[i, y][0]] + capture_bonus + mr_val + bonus, (x, y), (i, y)])
                    break
                else:
                    break
            # Right
            for j in range(y + 1, 8):
                if board[x, j] == "":
                    bonus = move_pos_delta(piece, (x, y), (x, j), enemies_remaining)
                    rookMoves.append([mr_val + bonus, (x, y), (x, j)])
                elif board[x, j] == "X":
                    break
                elif board[x, j][1] != color:
                    bonus = move_pos_delta(piece, (x, y), (x, j), enemies_remaining)
                    capture_bonus = enemy_threat_bonus.get((x, j), 0)
                    rookMoves.append([basePieceValues[board[x, j][0]] + capture_bonus + mr_val + bonus, (x, y), (x, j)])
                    break
                else:
                    break
            # Left
            for j in range(y - 1, -1, -1):
                if board[x, j] == "":
                    bonus = move_pos_delta(piece, (x, y), (x, j), enemies_remaining)
                    rookMoves.append([mr_val + bonus, (x, y), (x, j)])
                elif board[x, j] == "X":
                    break
                elif board[x, j][1] != color:
                    bonus = move_pos_delta(piece, (x, y), (x, j), enemies_remaining)
                    capture_bonus = enemy_threat_bonus.get((x, j), 0)
                    rookMoves.append([basePieceValues[board[x, j][0]] + capture_bonus + mr_val + bonus, (x, y), (x, j)])
                    break
                else:
                    break
            return rookMoves

        def getBishopMoves(x, y, isQueen=False):
            mb_val = moveValues["mb"] if not isQueen else moveValues["mq"]
            bishopMoves = []
            piece = "q" if isQueen else "b"
            # Up-Right
            i, j = x + 1, y + 1
            while isInBounds(i, j):
                if board[i, j] == "":
                    bonus = move_pos_delta(piece, (x, y), (i, j), enemies_remaining)
                    bishopMoves.append([mb_val + bonus, (x, y), (i, j)])
                elif board[i, j] == "X":
                    break
                elif board[i, j][1] != color:
                    bonus = move_pos_delta(piece, (x, y), (i, j), enemies_remaining)
                    capture_bonus = enemy_threat_bonus.get((i, j), 0)
                    bishopMoves.append([basePieceValues[board[i, j][0]] + capture_bonus + mb_val + bonus, (x, y), (i, j)])
                    break
                else:
                    break
                i += 1
                j += 1
            # Up-Left
            i, j = x + 1, y - 1
            while isInBounds(i, j):
                if board[i, j] == "":
                    bonus = move_pos_delta(piece, (x, y), (i, j), enemies_remaining)
                    bishopMoves.append([mb_val + bonus, (x, y), (i, j)])
                elif board[i, j] == "X":
                    break
                elif board[i, j][1] != color:
                    bonus = move_pos_delta(piece, (x, y), (i, j), enemies_remaining)
                    capture_bonus = enemy_threat_bonus.get((i, j), 0)
                    bishopMoves.append([basePieceValues[board[i, j][0]] + capture_bonus + mb_val + bonus, (x, y), (i, j)])
                    break
                else:
                    break
                i += 1
                j -= 1
            # Down-Right
            i, j = x - 1, y + 1
            while isInBounds(i, j):
                if board[i, j] == "":
                    bonus = move_pos_delta(piece, (x, y), (i, j), enemies_remaining)
                    bishopMoves.append([mb_val + bonus, (x, y), (i, j)])
                elif board[i, j] == "X":
                    break
                elif board[i, j][1] != color:
                    bonus = move_pos_delta(piece, (x, y), (i, j), enemies_remaining)
                    capture_bonus = enemy_threat_bonus.get((i, j), 0)
                    bishopMoves.append([basePieceValues[board[i, j][0]] + capture_bonus + mb_val + bonus, (x, y), (i, j)])
                    break
                else:
                    break
                i -= 1
                j += 1
            # Down-Left
            i, j = x - 1, y - 1
            while isInBounds(i, j):
                if board[i, j] == "":
                    bonus = move_pos_delta(piece, (x, y), (i, j), enemies_remaining)
                    bishopMoves.append([mb_val + bonus, (x, y), (i, j)])
                elif board[i, j] == "X":
                    break
                elif board[i, j][1] != color:
                    bonus = move_pos_delta(piece, (x, y), (i, j), enemies_remaining)
                    capture_bonus = enemy_threat_bonus.get((i, j), 0)
                    bishopMoves.append([basePieceValues[board[i, j][0]] + capture_bonus + mb_val + bonus, (x, y), (i, j)])
                    break
                else:
                    break
                i -= 1
                j -= 1
            return bishopMoves

        def getQueenMoves(x, y):
            queenMoves = []
            queenMoves.extend(getRookMoves(x, y, isQueen=True))
            queenMoves.extend(getBishopMoves(x, y, isQueen=True))
            return queenMoves

        def getKingMoves(x, y):
            mk_val = moveValues["mk"]
            kingMoves = []
            potentialMoves = [
                (x + 1, y),
                (x - 1, y),
                (x, y + 1),
                (x, y - 1),
                (x + 1, y + 1),
                (x + 1, y - 1),
                (x - 1, y + 1),
                (x - 1, y - 1)
            ]
            for move in potentialMoves:
                if isInBounds(move[0], move[1]):
                    if board[move[0], move[1]] == "" :
                        bonus = move_pos_delta("k", (x, y), (move[0], move[1]), enemies_remaining)
                        kingMoves.append([mk_val + bonus, (x, y), (move[0], move[1])])
                    elif board[move[0], move[1]] == "X":
                        pass
                    elif board[move[0], move[1]][1] != color:
                        bonus = move_pos_delta("k", (x, y), (move[0], move[1]), enemies_remaining)
                        capture_bonus = enemy_threat_bonus.get((move[0], move[1]), 0)
                        kingMoves.append([
                            basePieceValues[board[move[0], move[1]][0]] + capture_bonus + mk_val + bonus,
                            (x, y),
                            (move[0], move[1])
                        ])
            return kingMoves

        for x in range(board.shape[0]):
            for y in range(board.shape[1]):
                if board[x, y] == "" or board[x, y] == "X":
                    continue
                if board[x, y][1] != color:
                    continue
                match board[x, y][0]:
                    case "p":
                        everyPossibleMove.extend(apply_attack_malus(getPawnMoves(x, y), "p"))
                    case "n":
                        everyPossibleMove.extend(apply_attack_malus(getKnightMoves(x, y), "n"))
                    case "r":
                        everyPossibleMove.extend(apply_attack_malus(getRookMoves(x, y), "r"))
                    case "b":
                        everyPossibleMove.extend(apply_attack_malus(getBishopMoves(x, y), "b"))
                    case "q":
                        everyPossibleMove.extend(apply_attack_malus(getQueenMoves(x, y), "q"))
                    case "k":
                        everyPossibleMove.extend(apply_attack_malus(getKingMoves(x, y), "k"))
                    case _:
                        pass
        return everyPossibleMove

    
    def createNewBoard(board, nextMove): # creates a new board from one move
        new_board = board.copy()                    # Avoids modifying actual board
        new_board[nextMove[2]] = board[nextMove[1]] # This moves the piece to it's dest.
        new_board[nextMove[1]] = ""                 # The cell we moved from is now empty
        return new_board

    def minMax(board, depth, maximizing_player, score): # This will return the final score of the branch at the recursive stop.
        # Recrusive stop
        if depth == 0:
            return score

        # Our turn
        if maximizing_player:
            bestScore = -math.inf
            for nextMove in getAllMoves(board, our_color):
                new_board = createNewBoard(board, nextMove)
                nextRecursiveScore = minMax(new_board, depth-1, False, score + nextMove[0])
                bestScore = max(bestScore, nextRecursiveScore)
            return bestScore
        # Enemy's turn
        else:
            bestScore = math.inf
            for nextMove in getAllMoves(board, enemy_color):
                new_board = createNewBoard(board, nextMove)
                nextRecursiveScore = minMax(new_board, depth-1, True, score + nextMove[0]) # I am too tired too know if it's + or - here.
                bestScore = min(bestScore, nextRecursiveScore)
            return bestScore
    

    bestPossibleScore = -math.inf
    bestPossibleMove = [(0,0), (0,0)]
    searchDepth = 3
    # Recursive call
    for rootMove in getAllMoves(board, our_color):
        new_board = createNewBoard(board, rootMove)
        rootBestScore = minMax(new_board, searchDepth, False, rootMove[0]) # This set the rootMove[0]=rootMove's score to the best final path score.
        if  rootBestScore > bestPossibleScore:                  # If that score is the highest, then we go with the chosen path.
            bestPossibleScore = rootBestScore
            bestPossibleMove = [rootMove[1], rootMove[2]]

    
    print("Final move for this board:", bestPossibleMove[0], " to -> ", bestPossibleMove[1],", with a score of", bestPossibleScore, ". This took:", time.time()-startTime, " seconds !")
    return bestPossibleMove[0], bestPossibleMove[1]


register_chess_bot("MinMax_V3", minMaxBot)


# Notes:
# Have to implement, alpha-beta pruning to speed up the process.
#
# After thinking a bit.. I don't think that I did standard minMax
# algorithm correctly. I gave the score as one of it's arguments
# but then I can't do anything with the final state and apply
# pruning on it.
# I think I have to have a board that has a score on it's own
# instead of a path accumulated score.
# I decided to go with the path accumulated score because we
# assigned points to the moves and thought if we remove that,
# then our entire grid preference placements for each piece
# would be revoked.
# So might simply try to optimize this current version,
# instead of removing a core element to our concept.


# also, at line 561 for the enemy's score dunno +-.
