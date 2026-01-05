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

    def minMax(board, depth, maximizing_player):

        def getAllMoves(board, color):
            pieceValues = {
                "p" : 1,
                "n" : 3,
                "r" : 3,
                "b" : 4,
                "q" : 8,
                "k" : 100
            }
            moveValues = {
                # Moves
                "mp" : 2,
                "mn" : 5,
                "mr" : 4,
                "mb" : 4,
                "mq" : 6,
                "mk" : 2,

                # Attacks
                "tp" : 4,
                "tn" : 6,
                "tr" : 6,
                "tb" : 8,
                "tq" : 16,
                "tk" : 100,
                # Specials
                "pup" : 10
            }

            everyPossibleMove = []

            # Scans every cell on the board.
            for x in range(board.shape[0]):
                for y in range(board.shape[1]):
                    # If current cell does not contain anything or is
                    #  invalide, move to the next iteration of y.
                    if board[x,y]=="" or board[x,y]=="X":
                        continue
                    # We now presume that we have landed on a valid cell
                    # that contins a piece, we can reach board[x,y][1]
                    # without any issues.
                    if board[x,y][1]!=color:
                        continue


                    def isInBounds(x,y):
                        if x < 0 or x > 7:
                            return False
                        if y < 0 or y > 7:
                            return False
                        return True

                    # We now find ourselves on a cell containing one
                    # of our pieces.

                    # All moves getter:
                    # return an array of arrays composed of a move score
                    # as well as the move it's self.
                    # This score will later be used by minMax to
                    # determine which is the best move for our game.
                    def getAllSinglePieceMoves(board):
                        allMoves = []
                        match board[x,y][0]:
                            case "p":
                                # print("Pawn")
                                allMoves.extend( getPawnMoves(x,y)   )
                            case "n":
                                # print("Knight")
                                allMoves.extend( getKnightMoves(x,y) )
                            case "r":
                                # print("Rook")
                                allMoves.extend( getRookMoves(x,y)   )
                            case "b":
                                # print("Bishop")
                                allMoves.extend( getBishopMoves(x,y) )
                            case "q":
                                # print("Queen")
                                allMoves.extend( getQueenMoves(x,y)  )
                            case "k":
                                # print("King")
                                allMoves.extend( getKingMoves(x,y)   )
                            case _:
                                print("Zis is not on of ours !")
                                sys.exit("Stopping execution.")
                        
                        # print("All moves", allMoves)
                        return allMoves
                    
                    def getPawnMoves(x, y):
                        mp_val = moveValues["mp"]
                        pawnMoves = []
                        # Queen upgrade ?
                        if x+1 == 7:
                            if board[x+1,y] == "":
                                # print("PAWN UPGRADE")
                                pawnMoves.append([moveValues["pup"], (x,y), (x+1,y)])
                        # Move forwards ?
                        else:
                            if board[x+1,y] == "":
                                # print("PAWN MOVED FORWARDS")
                                pawnMoves.append([mp_val, (x,y), (x+1,y)])
                        # Diag attacks ?
                        if y + 1 <= 7:
                            if board[x+1,y+1] == "" or board[x+1,y+1] == "X":
                                pass
                            elif board[x+1,y+1][1] != color:
                                # print("PAWN ATTACKED")
                                pawnMoves.append([moveValues["t"+board[x+1,y+1][0]] + mp_val, (x,y), (x+1,y+1)])
                        if y - 1 >= 0:
                            if board[x+1,y-1] == "" or board[x+1,y-1] == "X":
                                pass
                            elif board[x+1,y-1][1] != color:
                                # print("PAWN ATTACKED")
                                pawnMoves.append([moveValues["t"+board[x+1,y-1][0]] + mp_val, (x,y), (x+1,y-1)])
                        return pawnMoves

                    def getKnightMoves(x,y):
                        mn_val = moveValues["mn"]
                        knightMoves = []
                        potentialMoves = [
                            (x+2, y+1),
                            (x+2, y-1),
                            (x-2, y+1),
                            (x-2, y-1),
                            (x+1, y+2),
                            (x+1, y-2),
                            (x-1, y+2),
                            (x-1, y-2)
                        ]
                        for move in potentialMoves:
                            if isInBounds(move[0], move[1]):
                                if board[move[0], move[1]] == "" :
                                    knightMoves.append([mn_val, (x,y), (move[0], move[1])])
                                elif board[move[0], move[1]] == "X":
                                    pass
                                elif board[move[0], move[1]][1] != color:
                                    knightMoves.append([moveValues["t"+board[move[0], move[1]][0]] + mn_val, (x,y), (move[0], move[1])])
                        return knightMoves
                    
                    def getRookMoves(x,y, isQueen=False):
                        rookMoves = []
                        mr_val = moveValues["mr"] if not isQueen else moveValues["mq"]
                        # Up
                        for i in range(x+1, 8):
                            if board[i,y] == "":
                                rookMoves.append([mr_val, (x,y), (i,y)])
                            elif board[i,y] == "X":
                                break
                            elif board[i,y][1] != color:
                                rookMoves.append([moveValues["t" + board[i,y][0]] + mr_val, (x,y), (i,y)])
                                break
                            else:
                                break
                        # Down
                        for i in range(x-1, -1, -1):
                            if board[i,y] == "":
                                rookMoves.append([mr_val, (x,y), (i,y)])
                            elif board[i,y] == "X":
                                break
                            elif board[i,y][1] != color:
                                rookMoves.append([moveValues["t" + board[i,y][0]] + mr_val, (x,y), (i,y)])
                                break
                            else:
                                break
                        # Right
                        for j in range(y+1, 8):
                            if board[x,j] == "":
                                rookMoves.append([mr_val, (x,y), (x,j)])
                            elif board[x,j] == "X":
                                break
                            elif board[x,j][1] != color:
                                rookMoves.append([moveValues["t" + board[x,j][0]] + mr_val, (x,y), (x,j)])
                                break
                            else:
                                break
                        # Left
                        for j in range(y-1, -1, -1):
                            if board[x,j] == "":
                                rookMoves.append([mr_val, (x,y), (x,j)])
                            elif board[x,j] == "X":
                                break
                            elif board[x,j][1] != color:
                                rookMoves.append([moveValues["t" + board[x,j][0]] + mr_val, (x,y), (x,j)])
                                break
                            else:
                                break
                        return rookMoves
                    
                    def getBishopMoves(x,y, isQueen=False):
                        mb_val = moveValues["mb"] if not isQueen else moveValues["mq"]
                        bishopMoves = [] 
                        # Up-Right
                        i, j = x+1, y+1
                        while isInBounds(i,j):
                            if board[i,j] == "":
                                bishopMoves.append([mb_val, (x,y), (i,j)])
                            elif board[i,j] == "X":
                                break
                            elif board[i,j][1] != color:
                                bishopMoves.append([moveValues["t" + board[i,j][0]] + mb_val, (x,y), (i,j)])
                                break
                            else:
                                break
                            i += 1
                            j += 1
                        # Up-Left
                        i, j = x+1, y-1
                        while isInBounds(i,j):
                            if board[i,j] == "":
                                bishopMoves.append([mb_val, (x,y), (i,j)])
                            elif board[i,j] == "X":
                                break
                            elif board[i,j][1] != color:
                                bishopMoves.append([moveValues["t" + board[i,j][0]] + mb_val, (x,y), (i,j)])
                                break
                            else:
                                break
                            i += 1
                            j -= 1
                        # Down-Right
                        i, j = x-1, y+1
                        while isInBounds(i,j):
                            if board[i,j] == "":
                                bishopMoves.append([mb_val, (x,y), (i,j)])
                            elif board[i,j] == "X":
                                break
                            elif board[i,j][1] != color:
                                bishopMoves.append([moveValues["t" + board[i,j][0]] + mb_val, (x,y), (i,j)])
                                break
                            else:
                                break
                            i -= 1
                            j += 1
                        # Down-Left
                        i, j = x-1, y-1
                        while isInBounds(i,j):
                            if board[i,j] == "":
                                bishopMoves.append([mb_val, (x,y), (i,j)])
                            elif board[i,j] == "X":
                                break
                            elif board[i,j][1] != color:
                                bishopMoves.append([moveValues["t" + board[i,j][0]] + mb_val, (x,y), (i,j)])
                                break
                            else:
                                break
                            i -= 1
                            j -= 1
                        return bishopMoves
                    
                    def getQueenMoves(x,y):
                        queenMoves = []
                        # Combine rook and bishop moves
                        # Rook-like moves
                        queenMoves.extend(getRookMoves(x,y, isQueen=True))
                        # Bishop-like moves
                        queenMoves.extend(getBishopMoves(x,y, isQueen=True))
                        return queenMoves
                    
                    def getKingMoves(x,y):
                        mk_val = moveValues["mk"]
                        kingMoves = []
                        potentialMoves = [
                            (x+1, y),
                            (x-1, y),
                            (x, y+1),
                            (x, y-1),
                            (x+1, y+1),
                            (x+1, y-1),
                            (x-1, y+1),
                            (x-1, y-1)
                        ]
                        for move in potentialMoves:
                            if isInBounds(move[0], move[1]):
                                if board[move[0], move[1]] == "" :
                                    kingMoves.append([mk_val, (x,y), (move[0], move[1])])
                                elif board[move[0], move[1]] == "X":
                                    pass
                                elif board[move[0], move[1]][1] != color:
                                    kingMoves.append([moveValues["t"+board[move[0], move[1]][0]] + mk_val, (x,y), (move[0], move[1])])
                        return kingMoves
                    

                    allSinglePieceMoves = getAllSinglePieceMoves(board) # gets all the possible moves for the piece on the current cell.

                    everyPossibleMove.extend(allSinglePieceMoves) # adds these moves to the total current board possible moves
                    
            return everyPossibleMove # returns all the possible moves for the current board. format: [[score, startPos, destPos], [...]]
            
        def getMax(moves): # returns the move with the highest score.
            highestScore = 0
            highestIndex = 0
            for index,value in enumerate(moves):
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

        # Recrusive stop
        if depth == 1:
            currentMoves = getAllMoves(board, our_color if maximizing_player else enemy_color)
            if len(currentMoves) != 0:
                finalMove = getMax(currentMoves)
                # print("Final move : ", finalMove, " that took", time.time() - startTime, " seconds !")
                return finalMove # old version where I used to give the final move instead of the score: finalMove[1], finalMove[2]
            else:
                return [0, (0,0), (0,0)]
            
        
            

        # /////////////////////////////////////////// CURRENT STATUS ///////////////////////////////////////////
        # At the moment, this section is supposed to handle the recursive minMax but when the depth is set
        # bigger than 1, then our pieces do not move. I think this is because we might be giving the
        # enemy's move instead of our own.. which would make the move invalid and skip us.
        #
        # SO FIX IT !///////////////////////////////////////////////////////////////////////////////////////////
        #
        # Our turn
        if maximizing_player:
            bestMove = [-math.inf, (0,0), (0,0)]
            for nextMove in getAllMoves(board, our_color):
                new_board = createNewBoard(board, nextMove)             # Create new board with the chosen move
                nextRecursiveMove = minMax(new_board, depth-1, False)   # gets the best move for that new board
                bestMove = bestMove if bestMove[0] > nextRecursiveMove[0] else nextRecursiveMove # assigns the best move depending on it's score nextRecursiveMove[0] == "score".
            return bestMove
        # Enemy's turn
        else:
            bestMove = [math.inf, (0,0), (0,0)]
            for nextMove in getAllMoves(board, enemy_color):
                new_board = createNewBoard(board, nextMove)             # Create new board with the chosen move
                nextRecursiveMove = minMax(new_board, depth-1, True)    # gets the best move for that new board
                bestMove = bestMove if bestMove[0] < nextRecursiveMove[0] else nextRecursiveMove # assigns the best move depending on it's score nextRecursiveMove[0] == "score".
            return bestMove
    


    # Recursive call
    optimalMove = minMax(board, 1, True) # Still contains [score, startingPos, destPos]
    
    if optimalMove != [0, (0,0), (0,0)]:
        print("Final move for this board: ", optimalMove[1], " to -> ", optimalMove[2], ". This took:", time.time()-startTime, " seconds !")
        return optimalMove[1], optimalMove[2]
    
    return (0,0), (0,0)


register_chess_bot("MinMax", minMaxBot)
