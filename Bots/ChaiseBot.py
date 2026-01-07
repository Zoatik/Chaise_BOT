
#
#   Example function to be implemented for
#       Single important function is next_best
#           color: a single character str indicating the color represented by this bot ('w' for white)
#           board: a 2d matrix containing strings as a descriptors of the board '' means empty location "XC" means a piece represented by X of the color C is present there
#           budget: time budget allowed for this turn, the function must return a pair (xs,ys) --> (xd,yd) to indicate a piece at xs, ys moving to xd, yd
#

#   Be careful with modules to import from the root (don't forget the Bots.)
import math
import time
from Bots.ChessBotList import register_chess_bot
import csv
import os

#   Simply move the pawns forward and tries to capture as soon as possible
def chess_bot(player_sequence, board, time_budget, **kwargs):
    startTime = time.time()
    stats = Stats()

    def get_capture_moves(b, color, perspective_color):
        caps = []
        for mv in Utils.getAllMoves(b, color, perspective_color):
            _, d = mv
            t = b[d]
            if t != "" and t != "X" and t[1] != color:
                caps.append(mv)
        return caps

    player_color = player_sequence[1]
    def quiescence(b, stm_color, alpha, beta):
        if Utils.time_up(start_time = startTime, time_budget=time_budget, margin=0.03):
            raise TimeoutError("time budget exceeded")

        stand_pat = Utils.evaluateBoard(b, perspective_color=stm_color)
        maximizing = (stm_color == player_color)

        if maximizing:
            if stand_pat >= beta:
                return stand_pat
            alpha = max(alpha, stand_pat)

            moves = get_capture_moves(b, stm_color, player_color)
            moves = Utils.order_moves(moves, b, stm_color, player_color, reverse=True)
            for mv in moves:
                if Utils.time_up(start_time=startTime, time_budget=time_budget, margin=0.03):
                    raise TimeoutError("time budget exceeded")
                stats.q_nodes += 1
                nb = Utils.create_new_board(b, mv)
                next_stm = 'w' if stm_color == 'b' else 'b'
                score = quiescence(nb, next_stm, alpha, beta)
                alpha = max(alpha, score)
                if alpha >= beta:
                    stats.cutoffs += 1
                    break
            return alpha
        else:
            if stand_pat <= alpha:
                return stand_pat
            beta = min(beta, stand_pat)

            moves = get_capture_moves(b, stm_color, player_color)
            moves = Utils.order_moves(moves, b, stm_color, player_color, reverse=False)
            for mv in moves:
                if Utils.time_up(start_time=startTime, time_budget=time_budget, margin=0.03):
                    raise TimeoutError("time budget exceeded")
                stats.q_nodes += 1
                nb = Utils.create_new_board(b, mv)
                next_stm = 'w' if stm_color == 'b' else 'b'
                score = quiescence(nb, next_stm, alpha, beta)
                beta = min(beta, score)
                if alpha >= beta:
                    stats.cutoffs += 1
                    break
            return beta

    def alpha_beta(b, stm_color, depth, alpha, beta):
        if depth == 0:
            return quiescence(b, stm_color, alpha, beta)

        if Utils.time_up(start_time=startTime, time_budget=time_budget, margin=0.03):
            raise TimeoutError("time budget exceeded")

        maximizing = (stm_color == player_color)

        moves = Utils.getAllMoves(b, stm_color, player_color)
        moves = Utils.order_moves(moves, b, stm_color, player_color, reverse=maximizing)

        if maximizing:
            value = -math.inf
            for mv in moves:
                if Utils.time_up(start_time=startTime, time_budget=time_budget, margin=0.03):
                    raise TimeoutError("time budget exceeded")
                
                stats.nodes += 1

                nb = Utils.create_new_board(b, mv)
                next_stm = 'w' if stm_color == 'b' else 'b'
                value = max(value, alpha_beta(nb, next_stm, depth - 1, alpha, beta))
                alpha = max(alpha, value)
                if alpha >= beta:
                    stats.cutoffs += 1
                    break
            return value
        else:
            value = math.inf
            for mv in moves:
                if Utils.time_up(start_time=startTime, time_budget=time_budget, margin=0.03):
                    raise TimeoutError("time budget exceeded")
                
                stats.nodes += 1

                nb = Utils.create_new_board(b, mv)
                next_stm = 'w' if stm_color == 'b' else 'b'
                value = min(value, alpha_beta(nb, next_stm, depth - 1, alpha, beta))
                beta = min(beta, value)
                if alpha >= beta:
                    stats.cutoffs += 1
                    break
            return value
        
    bestPossibleScore = -math.inf
    bestPossibleMove = [(0, 0), (0, 0)]

    maxDepth = 6
    depth = 1
    aspiration = 2.0

    root_board = board
    root_stm = player_color

    while depth <= maxDepth:
        if Utils.time_up(start_time=startTime, time_budget=time_budget, margin=0.06):
            break

        bestScoreThisDepth = -math.inf
        bestMoveThisDepth = bestPossibleMove

        rootMoves = Utils.getAllMoves(root_board, root_stm, player_color)
        rootMoves = Utils.order_moves(rootMoves, root_board, root_stm, player_color,reverse=True)

        a0 = bestPossibleScore - aspiration if bestPossibleScore != -math.inf else -math.inf
        b0 = bestPossibleScore + aspiration if bestPossibleScore != -math.inf else math.inf
        window_failed = False

        for mv in rootMoves:
            if Utils.time_up(start_time=startTime, time_budget=time_budget, margin=0.06):
                break

            nb = Utils.create_new_board(root_board, mv)
            next_stm = 'w' if root_stm == 'b' else 'b'

            try:
                score = alpha_beta(nb, next_stm, depth - 1, a0, b0)
            except TimeoutError:
                break

            if score <= a0 or score >= b0:
                window_failed = True
                try:
                    score = alpha_beta(nb, next_stm, depth - 1, -math.inf, math.inf)
                except TimeoutError:
                    break

            if score > bestScoreThisDepth:
                bestScoreThisDepth = score
                bestMoveThisDepth = [mv[0], mv[1]]

        if bestScoreThisDepth != -math.inf:
            bestPossibleScore = bestScoreThisDepth
            bestPossibleMove = bestMoveThisDepth

        aspiration = min(aspiration * 1.7, 8.0) if window_failed else max(1.5, aspiration * 0.9)
        depth += 1

    # Print using the SAME evaluation convention (root perspective)
    final_board = Utils.create_new_board(root_board, (bestPossibleMove[0], bestPossibleMove[1]))
    final_score = Utils.evaluateBoard(final_board, perspective_color=player_color)

    finalTime = time.time()-startTime
    print(
        "Final move for this board:",
        bestPossibleMove[0], "to ->", bestPossibleMove[1],
        ", with a score of", bestPossibleScore,
        ". This took:", finalTime, "seconds!",
        " With a depth of:", depth - 1,". Final eval:", final_score
    )

    # Write stats to CSV file
    file_exists = os.path.isfile("StatsChaiseCSVFile")

    with open("StatsChaiseCSVFile", mode="a", newline="") as file:
        writer = csv.writer(file)
        # Write header only once
        if not file_exists:
            writer.writerow([
                "Total nodes visited",
                "Total quiescence nodes",
                "Alpha-beta cutoffs",
                "Alpha-beta improvement",
                "Nodes per second"
            ])
        writer.writerow([
            stats.nodes+stats.q_nodes,
            stats.q_nodes,
            stats.cutoffs,
            math.floor(stats.cutoffs/(stats.nodes+stats.q_nodes)*100),
            round((stats.nodes+stats.q_nodes)/finalTime, 2)
        ])
    print(
        "--- Stats ---           ", "\n",
        "Total nodes visited:    ", stats.nodes+stats.q_nodes, "\n",
        "Total quiescence nodes: ", stats.q_nodes, "\n",
        "Alpha-beta cutoffs:     ", stats.cutoffs, "\n",
        "Alpha-beta improvement: ", math.floor(stats.cutoffs/(stats.nodes+stats.q_nodes)*100), "%\n",
        "Nodes per second:       ", round((stats.nodes+stats.q_nodes)/finalTime, 2), "\n",
    )

    return bestPossibleMove[0], bestPossibleMove[1]

#   Example how to register the function
register_chess_bot("ChaiseBot", chess_bot)





class Stats:
 def __init__(self):
        self.nodes = 0
        self.q_nodes = 0
        self.cutoffs = 0





class Utils:
    basePieceValues = {
        "p" : 1,
        "n" : 3.2,
        "r" : 5.1,
        "b" : 3.33,
        "q" : 8.8,
        "k" : 100
    }

    movesValue = {
        "capture": 10,
        "threaten": 10,
        "capture_threat": 5,
        "center_control": 3,
        "development": 2,
        "king_safety": 15,
        "pup": 8
    }

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




    @classmethod
    def piece_pos_bonus(cls, pieceType, pos, enemies_remaining):
        position_scale = 0.1
        if pieceType not in cls.position_bonus:
            return 0
        max_enemies = 16
        enemies_remaining = max(0, min(max_enemies, enemies_remaining))
        t = 1.0 - (enemies_remaining / max_enemies)
        x, y = pos
        start_val = cls.position_bonus[pieceType]["start"][x][y]
        end_val = cls.position_bonus[pieceType]["end"][x][y]
        return start_val + (end_val - start_val) * t * position_scale

    @classmethod
    def getAllMoves(cls, board, color, player_color):
        everyPossibleMove = []
        for x in range(board.shape[0]):
            for y in range(board.shape[1]):
                if board[x, y] == "":
                    continue
                if board[x, y][1] != color:
                    continue
                match board[x, y][0]:
                    case "p":
                        everyPossibleMove.extend(cls.getPawnMoves(x, y, board, color, player_color))
                    case "n":
                        everyPossibleMove.extend(cls.getKnightMoves(x, y, board, color))
                    case "r":
                        everyPossibleMove.extend(cls.getRookMoves(x, y, board, color))
                    case "b":
                        everyPossibleMove.extend(cls.getBishopMoves(x, y, board, color))
                    case "q":
                        everyPossibleMove.extend(cls.getQueenMoves(x, y, board, color))
                    case "k":
                        everyPossibleMove.extend(cls.getKingMoves(x, y, board, color))
                    case _:
                        pass
        return everyPossibleMove
        
    @classmethod
    def isInBounds(cls, x, y):
        return 0 <= x <= 7 and 0 <= y <= 7
    @classmethod
    def is_enemy(cls, x, y, board, color):
        cell = board[x, y]
        return cell != "" and cell[1] != color
    @classmethod
    def is_empty(cls, x, y, board):
        return board[x, y] == ""
    
    @classmethod
    def getPawnMoves(cls, x, y, board, color, player_color):
        pawnMoves = []
        if color == player_color:
            if x + 1 <= 7:
                if cls.is_empty(x + 1, y, board):
                    pawnMoves.append(((x, y), (x + 1, y)))
                if y + 1 <= 7 and cls.is_enemy(x + 1, y + 1, board, color):
                    pawnMoves.append(((x, y), (x + 1, y + 1)))
                if y - 1 >= 0 and cls.is_enemy(x + 1, y - 1, board, color):
                    pawnMoves.append(((x, y), (x + 1, y - 1)))
        else:
            if x - 1 >= 0:
                if cls.is_empty(x - 1, y, board):
                    pawnMoves.append(((x, y), (x - 1, y)))
                if y + 1 <= 7 and cls.is_enemy(x - 1, y + 1, board, color):
                    pawnMoves.append(((x, y), (x - 1, y + 1)))
                if y - 1 >= 0 and cls.is_enemy(x - 1, y - 1, board, color):
                    pawnMoves.append(((x, y), (x - 1, y - 1)))
        return pawnMoves

    @classmethod
    def getKnightMoves(cls, x, y, board, color):
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
            if cls.isInBounds(move[0], move[1]):
                if board[move[0], move[1]] == "" or cls.is_enemy(move[0], move[1], board, color):
                    knightMoves.append(((x, y), (move[0], move[1])))
        return knightMoves

    @classmethod
    def getRookMoves(cls, x, y, board, color, isQueen=False):
        rookMoves = []
        for i in range(x + 1, 8):
            if board[i, y] == "":
                rookMoves.append(((x, y), (i, y)))
            elif cls.is_enemy(i, y, board, color):
                rookMoves.append(((x, y), (i, y)))
                break
            else:
                break
        for i in range(x - 1, -1, -1):
            if board[i, y] == "":
                rookMoves.append(((x, y), (i, y)))
            elif cls.is_enemy(i, y, board, color):
                rookMoves.append(((x, y), (i, y)))
                break
            else:
                break
        for j in range(y + 1, 8):
            if board[x, j] == "":
                rookMoves.append(((x, y), (x, j)))
            elif cls.is_enemy(x, j, board, color):
                rookMoves.append(((x, y), (x, j)))
                break
            else:
                break
        for j in range(y - 1, -1, -1):
            if board[x, j] == "":
                rookMoves.append(((x, y), (x, j)))
            elif cls.is_enemy(x, j, board, color):
                rookMoves.append(((x, y), (x, j)))
                break
            else:
                break
        return rookMoves
    
    @classmethod
    def getBishopMoves(cls, x, y, board, color, isQueen=False):
        bishopMoves = []
        i, j = x + 1, y + 1
        while cls.isInBounds(i, j):
            if board[i, j] == "":
                bishopMoves.append(((x, y), (i, j)))
            elif cls.is_enemy(i, j, board, color):
                bishopMoves.append(((x, y), (i, j)))
                break
            else:
                break
            i += 1
            j += 1
        i, j = x + 1, y - 1
        while cls.isInBounds(i, j):
            if board[i, j] == "":
                bishopMoves.append(((x, y), (i, j)))
            elif cls.is_enemy(i, j, board, color):
                bishopMoves.append(((x, y), (i, j)))
                break
            else:
                break
            i += 1
            j -= 1
        i, j = x - 1, y + 1
        while cls.isInBounds(i, j):
            if board[i, j] == "":
                bishopMoves.append(((x, y), (i, j)))
            elif cls.is_enemy(i, j, board, color):
                bishopMoves.append(((x, y), (i, j)))
                break
            else:
                break
            i -= 1
            j += 1
        i, j = x - 1, y - 1
        while cls.isInBounds(i, j):
            if board[i, j] == "":
                bishopMoves.append(((x, y), (i, j)))
            elif cls.is_enemy(i, j, board, color):
                bishopMoves.append(((x, y), (i, j)))
                break
            else:
                break
            i -= 1
            j -= 1
        return bishopMoves

    @classmethod
    def getQueenMoves(cls, x, y, board, color):
        queenMoves = []
        queenMoves.extend(cls.getRookMoves(x, y, board, color, isQueen=True))
        queenMoves.extend(cls.getBishopMoves(x, y, board, color, isQueen=True))
        return queenMoves

    @classmethod
    def getKingMoves(cls, x, y, board, color):
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
            if cls.isInBounds(move[0], move[1]):
                if board[move[0], move[1]] == "" or cls.is_enemy(move[0], move[1], board, color):
                    kingMoves.append(((x, y), (move[0], move[1])))
        return kingMoves

        

    @classmethod
    def count_enemies(cls, b, our_c):
        c = 0
        for x in range(8):
            for y in range(8):
                cell = b[x, y]
                if cell == "":
                    continue
                if cell[1] != our_c:
                    c += 1
        return c

    @classmethod
    def time_up(cls, start_time, time_budget, margin=0.03):
        return (time.time() - start_time) >= (time_budget - margin)

    @classmethod
    def order_moves(cls, moves, board, color, player_color, reverse=True):
        def moveValue(move):
            attacked_pieces = cls.get_attacked_pieces(board, color, player_color)
            attacking_pieces = cls.get_attacking_pieces(board, color, player_color)
            piece_pos = move[0]
            target_pos = move[1]
            piece = board[piece_pos[0], piece_pos[1]]
            target = board[target_pos[0], target_pos[1]]
            value = 0
            if target != "":
                value += cls.basePieceValues[target[0]]
            value += cls.piece_pos_bonus(piece[0], target_pos, cls.count_enemies(board, color))

            if (piece in attacked_pieces):
                value += cls.movesValue["threaten"]
            if (piece in attacking_pieces):
                value += cls.movesValue["capture"]
                if(cls.can_piece_attack(board, piece_pos, target_pos, player_color)):
                    value += cls.movesValue["capture_threat"]  

            if (piece[0] == 'p'):
                if cls.pawn_promotion_available(board, piece_pos, color, player_color):
                    value += Utils.movesValue["pup"]
            
            return value

        return sorted(moves, key=moveValue, reverse=reverse)

    @classmethod
    def pawn_promotion_available(cls, board, pawn_pos, color, player_color):
        pawn_moves = cls.getPawnMoves(pawn_pos[0], pawn_pos[1], board, color, player_color)
        for move in pawn_moves:
            target_pos = move[1]
            if color == player_color and target_pos[0] == 7:
                return True
            elif color != player_color and target_pos[0] == 0:
                return True
        return False    

    @classmethod
    def can_piece_attack(cls, board, piece_pos, target_pos, player_color):
        xs, ys = piece_pos
        xd, yd = target_pos
        piece = board[xs, ys]
        color = piece[1]
        possible_moves = cls.getAllMoves(board, color, player_color)
        for move in possible_moves:
            if move[0] == piece_pos and move[1] == target_pos:
                return True
        return False


    @classmethod
    def get_attacked_pieces(cls, board, color, player_color):
        attacked = set()
        enemy_color = 'w' if color == 'b' else 'b'
        enemy_moves = cls.getAllMoves(board, enemy_color, player_color)
        for move in enemy_moves:
            xs, ys = move[0]
            xd, yd = move[1]
            if board[xd, yd] != "" and board[xd, yd][1] == color:
                attacked.add((board[xd, yd], (xd, yd)))
        return attacked

    @classmethod
    def get_attacking_pieces(cls, board, color, player_color):
        attacking = set()
        our_moves = cls.getAllMoves(board, color, player_color)
        for move in our_moves:
            xs, ys = move[0]
            xd, yd = move[1]
            if board[xd, yd] != "" and board[xd, yd][1] != color:
                attacking.add((board[xs, ys], (xs, ys)))
        return attacking

    
    @classmethod
    def evaluateBoard(cls, board, perspective_color):
        score = 0
        enemy_count = cls.count_enemies(board, perspective_color)
        for x in range(8):
            for y in range(8):
                cell = board[x, y]
                if cell == "":
                    continue
                piece_type = cell[0]
                piece_color = cell[1]
                base_value = cls.basePieceValues.get(piece_type, 0)
                pos_bonus = cls.piece_pos_bonus(piece_type, (x, y), enemy_count)
                total_value = base_value + pos_bonus
                if piece_color == perspective_color:
                    score += total_value
                else:
                    score -= total_value
        return score
    
    @classmethod
    def create_new_board(cls, b, move):
        nb = b.copy()
        start, dest = move
        piece = b[start]
        target = b[dest]

        if piece == "":
            raise ValueError("No piece at the starting position")
        if target != "" and target[1] == piece[1]:
            raise ValueError("Cannot capture own piece")

        nb[dest] = piece
        nb[start] = "" 

        return nb

