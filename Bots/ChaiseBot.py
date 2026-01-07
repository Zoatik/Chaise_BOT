
#
#   Example function to be implemented for
#       Single important function is next_best
#           color: a single character str indicating the color represented by this bot ('w' for white)
#           board: a 2d matrix containing strings as a descriptors of the board '' means empty location "XC" means a piece represented by X of the color C is present there
#           budget: time budget allowed for this turn, the function must return a pair (xs,ys) --> (xd,yd) to indicate a piece at xs, ys moving to xd, yd
#

#   Be careful with modules to import from the root (don't forget the Bots.)
from Bots.ChessBotList import register_chess_bot

#   Simply move the pawns forward and tries to capture as soon as possible
def chess_bot(player_sequence, board, time_budget, **kwargs):


    color = player_sequence[1]
    for x in range(board.shape[0]-1):
        for y in range(board.shape[1]):
            if board[x,y] != "p"+color:
                continue
            if y > 0 and board[x+1,y-1] != '' and board[x+1,y-1][-1] != color:
                return (x,y), (x+1,y-1)
            if y < board.shape[1] - 1 and board[x+1,y+1] != '' and board[x+1,y+1][1] != color:
                return (x,y), (x+1,y+1)
            elif board[x+1,y] == '':
                return (x,y), (x+1,y)

    return (0,0), (0,0)

#   Example how to register the function
register_chess_bot("ChaiseBot", chess_bot)

class Utils:
    basePieceValues = {
        "p" : 1,
        "n" : 3.2,
        "r" : 5.1,
        "b" : 3.33,
        "q" : 8.8,
        "k" : 100
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
    def getAllMoves(cls, board, color, our_color):
        everyPossibleMove = []

        def isInBounds(x, y):
            return 0 <= x <= 7 and 0 <= y <= 7

        def is_enemy(x, y):
            cell = board[x, y]
            return cell != "" and cell != "X" and cell[1] != color

        def is_empty(x, y):
            return board[x, y] == ""

        def getPawnMoves(x, y):
            pawnMoves = []
            if color == our_color:
                if x + 1 <= 7:
                    if is_empty(x + 1, y):
                        pawnMoves.append(((x, y), (x + 1, y)))
                    if y + 1 <= 7 and is_enemy(x + 1, y + 1):
                        pawnMoves.append(((x, y), (x + 1, y + 1)))
                    if y - 1 >= 0 and is_enemy(x + 1, y - 1):
                        pawnMoves.append(((x, y), (x + 1, y - 1)))
            else:
                if x - 1 >= 0:
                    if is_empty(x - 1, y):
                        pawnMoves.append(((x, y), (x - 1, y)))
                    if y + 1 <= 7 and is_enemy(x - 1, y + 1):
                        pawnMoves.append(((x, y), (x - 1, y + 1)))
                    if y - 1 >= 0 and is_enemy(x - 1, y - 1):
                        pawnMoves.append(((x, y), (x - 1, y - 1)))
            return pawnMoves

        def getKnightMoves(x, y):
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
                    if board[move[0], move[1]] == "" or is_enemy(move[0], move[1]):
                        knightMoves.append(((x, y), (move[0], move[1])))
            return knightMoves

        def getRookMoves(x, y, isQueen=False):
            rookMoves = []
            for i in range(x + 1, 8):
                if board[i, y] == "":
                    rookMoves.append(((x, y), (i, y)))
                elif board[i, y] == "X":
                    break
                elif is_enemy(i, y):
                    rookMoves.append(((x, y), (i, y)))
                    break
                else:
                    break
            for i in range(x - 1, -1, -1):
                if board[i, y] == "":
                    rookMoves.append(((x, y), (i, y)))
                elif board[i, y] == "X":
                    break
                elif is_enemy(i, y):
                    rookMoves.append(((x, y), (i, y)))
                    break
                else:
                    break
            for j in range(y + 1, 8):
                if board[x, j] == "":
                    rookMoves.append(((x, y), (x, j)))
                elif board[x, j] == "X":
                    break
                elif is_enemy(x, j):
                    rookMoves.append(((x, y), (x, j)))
                    break
                else:
                    break
            for j in range(y - 1, -1, -1):
                if board[x, j] == "":
                    rookMoves.append(((x, y), (x, j)))
                elif board[x, j] == "X":
                    break
                elif is_enemy(x, j):
                    rookMoves.append(((x, y), (x, j)))
                    break
                else:
                    break
            return rookMoves

        def getBishopMoves(x, y, isQueen=False):
            bishopMoves = []
            i, j = x + 1, y + 1
            while isInBounds(i, j):
                if board[i, j] == "":
                    bishopMoves.append(((x, y), (i, j)))
                elif board[i, j] == "X":
                    break
                elif is_enemy(i, j):
                    bishopMoves.append(((x, y), (i, j)))
                    break
                else:
                    break
                i += 1
                j += 1
            i, j = x + 1, y - 1
            while isInBounds(i, j):
                if board[i, j] == "":
                    bishopMoves.append(((x, y), (i, j)))
                elif board[i, j] == "X":
                    break
                elif is_enemy(i, j):
                    bishopMoves.append(((x, y), (i, j)))
                    break
                else:
                    break
                i += 1
                j -= 1
            i, j = x - 1, y + 1
            while isInBounds(i, j):
                if board[i, j] == "":
                    bishopMoves.append(((x, y), (i, j)))
                elif board[i, j] == "X":
                    break
                elif is_enemy(i, j):
                    bishopMoves.append(((x, y), (i, j)))
                    break
                else:
                    break
                i -= 1
                j += 1
            i, j = x - 1, y - 1
            while isInBounds(i, j):
                if board[i, j] == "":
                    bishopMoves.append(((x, y), (i, j)))
                elif board[i, j] == "X":
                    break
                elif is_enemy(i, j):
                    bishopMoves.append(((x, y), (i, j)))
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
                    if board[move[0], move[1]] == "" or is_enemy(move[0], move[1]):
                        kingMoves.append(((x, y), (move[0], move[1])))
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

    @classmethod
    def count_enemies(cls, b, our_c):
        c = 0
        for x in range(8):
            for y in range(8):
                cell = b[x, y]
                if cell == "" or cell == "X":
                    continue
                if cell[1] != our_c:
                    c += 1
        return c

    @classmethod
    def orderMoves(cls, moves, board, color, our_color):
        def moveValue(move):
            xs, ys = move[0]
            xd, yd = move[1]
            piece = board[xs, ys]
            target = board[xd, yd]
            value = 0
            if target != "" and target != "X":
                value += cls.basePieceValues[target[0]]
            value += cls.piece_pos_bonus()
            return value
        
        our_attacked_pieces = cls.get_attacked_pieces(board, our_color)
        for our_attacked_piece in our_attacked_pieces:
        return sorted(moves, key=moveValue, reverse=True)

    @classmethod
    def get_attacked_pieces(cls, board, color):
        attacked = set()
        enemy_color = 'w' if color == 'b' else 'b'
        enemy_moves = cls.getAllMoves(board, enemy_color, color)
        for move in enemy_moves:
            xs, ys = move[0]
            xd, yd = move[1]
            if board[xd, yd] != "" and board[xd, yd] != "X" and board[xd, yd][1] == color:
                attacked.add((board[xd, yd], (xd, yd)))
        return attacked

    
    @classmethod
    def evaluateBoard(cls, board, our_color):
        score = 0
        enemy_count = cls.count_enemies(board, our_color)
        for x in range(8):
            for y in range(8):
                cell = board[x, y]
                if cell == "" or cell == "X":
                    continue
                piece_type = cell[0]
                piece_color = cell[1]
                base_value = cls.basePieceValues.get(piece_type, 0)
                pos_bonus = cls.piece_pos_bonus(piece_type, (x, y), enemy_count)
                total_value = base_value + pos_bonus
                if piece_color == our_color:
                    score += total_value
                else:
                    score -= total_value
        return score



