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

        # Attacks
        "tp" : 4.0,
        "tn" : 6.0,
        "tr" : 6.0,
        "tb" : 8.0,
        "tq" : 16.0,
        "tk" : 100.0,
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

    def getAllMoves(board, color):
        enemies_remaining = count_enemies(board, color)
        moveValues = dict(baseMoveValues)
        everyPossibleMove = []

        def isInBounds(x, y):
            if x < 0 or x > 7:
                return False
            if y < 0 or y > 7:
                return False
            return True

        def getPawnMoves(x, y):
            mp_val = moveValues["mp"]
            pawnMoves = []
            if x + 1 > 7:
                return pawnMoves
            # Queen upgrade ?
            if x + 1 == 7 and board[x + 1, y] == "":
                promo_bonus = (
                    piece_pos_bonus("q", (x + 1, y), enemies_remaining)
                    - piece_pos_bonus("p", (x, y), enemies_remaining)
                )
                pawnMoves.append([moveValues["pup"] + promo_bonus, (x, y), (x + 1, y)])
            # Move forwards ?
            elif board[x + 1, y] == "":
                bonus = move_pos_delta("p", (x, y), (x + 1, y), enemies_remaining)
                pawnMoves.append([mp_val + bonus, (x, y), (x + 1, y)])
            # Diag attacks ?
            if y + 1 <= 7:
                if board[x + 1, y + 1] != "" and board[x + 1, y + 1] != "X":
                    if board[x + 1, y + 1][1] != color:
                        bonus = move_pos_delta("p", (x, y), (x + 1, y + 1), enemies_remaining)
                        pawnMoves.append([
                            moveValues["t" + board[x + 1, y + 1][0]] + mp_val + bonus,
                            (x, y),
                            (x + 1, y + 1)
                        ])
            if y - 1 >= 0:
                if board[x + 1, y - 1] != "" and board[x + 1, y - 1] != "X":
                    if board[x + 1, y - 1][1] != color:
                        bonus = move_pos_delta("p", (x, y), (x + 1, y - 1), enemies_remaining)
                        pawnMoves.append([
                            moveValues["t" + board[x + 1, y - 1][0]] + mp_val + bonus,
                            (x, y),
                            (x + 1, y - 1)
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
                        knightMoves.append([
                            moveValues["t" + board[move[0], move[1]][0]] + mn_val + bonus,
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
                    rookMoves.append([moveValues["t" + board[i, y][0]] + mr_val + bonus, (x, y), (i, y)])
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
                    rookMoves.append([moveValues["t" + board[i, y][0]] + mr_val + bonus, (x, y), (i, y)])
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
                    rookMoves.append([moveValues["t" + board[x, j][0]] + mr_val + bonus, (x, y), (x, j)])
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
                    rookMoves.append([moveValues["t" + board[x, j][0]] + mr_val + bonus, (x, y), (x, j)])
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
                    bishopMoves.append([moveValues["t" + board[i, j][0]] + mb_val + bonus, (x, y), (i, j)])
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
                    bishopMoves.append([moveValues["t" + board[i, j][0]] + mb_val + bonus, (x, y), (i, j)])
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
                    bishopMoves.append([moveValues["t" + board[i, j][0]] + mb_val + bonus, (x, y), (i, j)])
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
                    bishopMoves.append([moveValues["t" + board[i, j][0]] + mb_val + bonus, (x, y), (i, j)])
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
                        kingMoves.append([
                            moveValues["t" + board[move[0], move[1]][0]] + mk_val + bonus,
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
                        everyPossibleMove.extend(getPawnMoves(x, y))
                    case "n":
                        everyPossibleMove.extend(getKnightMoves(x, y))
                    case "r":
                        everyPossibleMove.extend(getRookMoves(x, y))
                    case "b":
                        everyPossibleMove.extend(getBishopMoves(x, y))
                    case "q":
                        everyPossibleMove.extend(getQueenMoves(x, y))
                    case "k":
                        everyPossibleMove.extend(getKingMoves(x, y))
                    case _:
                        pass
        return everyPossibleMove

            
    def getMax(moves): # returns the move with the highest score.
        highestScore = 0
        highestIndex = 0
        for index, value in enumerate(moves):
            if value[0] > highestScore:
                highestScore = value[0]
                highestIndex = index
        return moves[highestIndex]

    def getMin(moves): # idem lowest score.
        lowestScore = math.inf
        lowestIndex = 0
        for index, value in enumerate(moves):
            if value[0] < lowestScore:
                lowestScore = value[0]
                lowestIndex = index
        return moves[lowestIndex]

    def createNewBoard(board, nextMove): # creates a new board from one move
        new_board = board.copy()                    # Avoids modifying actual board
        new_board[nextMove[2]] = board[nextMove[1]] # This moves the piece to it's dest.
        new_board[nextMove[1]] = ""                 # The cell we moved from is now empty
        return new_board

    def minMax(board, depth, maximizing_player):
        # Recrusive stop
        if depth == 1:
            currentMoves = getAllMoves(board, our_color if maximizing_player else enemy_color)
            if len(currentMoves) != 0:
                return getMax(currentMoves)
            return [0, (0,0), (0,0)]

        # Our turn
        if maximizing_player:
            bestMove = [-math.inf, (0,0), (0,0)]
            for nextMove in getAllMoves(board, our_color):
                new_board = createNewBoard(board, nextMove)
                nextRecursiveMove = minMax(new_board, depth-1, False)
                bestMove = bestMove if bestMove[0] > nextRecursiveMove[0] else nextRecursiveMove
            return bestMove
        # Enemy's turn
        bestMove = [math.inf, (0,0), (0,0)]
        for nextMove in getAllMoves(board, enemy_color):
            new_board = createNewBoard(board, nextMove)
            nextRecursiveMove = minMax(new_board, depth-1, True)
            bestMove = bestMove if bestMove[0] < nextRecursiveMove[0] else nextRecursiveMove
        return bestMove
    


    # Recursive call
    optimalMove = minMax(board, 1, True) # Still contains [score, startingPos, destPos]
    
    if optimalMove != [0, (0,0), (0,0)]:
        print("Final move for this board: ", optimalMove[1], " to -> ", optimalMove[2], ". This took:", time.time()-startTime, " seconds !")
        return optimalMove[1], optimalMove[2]
    
    return (0,0), (0,0)


register_chess_bot("MinMax", minMaxBot)
