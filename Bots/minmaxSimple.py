from Bots.ChessBotList import register_chess_bot

import time

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

    color = player_sequence[1]

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
        "mp" : 1,
        "mn" : 6,
        "mr" : 4,
        "mb" : 4,
        "mq" : 3,
        "mk" : 1,

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

    everyPieceBestMove = []

    # Scans every cell on the board.
    for x in range(board.shape[0]-1):
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
            def getAllMoves():
                allMoves = []
                match board[x,y][0]:
                    case "p":
                        mp_val = moveValues["mp"]
                        print("////// Pawn //////")
                        # Queen upgrade ?
                        if x+1 == 7:
                            if board[x+1,y] == "":
                                # print("PAWN UPGRADE")
                                allMoves.append([moveValues["pup"], (x,y), (x+1,y)])
                        # Move forwards ?
                        else:
                            if board[x+1,y] == "":
                                # print("PAWN MOVED FORWARDS")
                                allMoves.append([mp_val, (x,y), (x+1,y)])
                        # Diag attacks ?
                        if y + 1 <= 7:
                            if board[x+1,y+1] == "" or board[x+1,y+1] == "X":
                                pass
                            elif board[x+1,y+1][1] != color:
                                # print("PAWN ATTACKED")
                                allMoves.append([moveValues["t"+board[x+1,y+1][0]] + mp_val, (x,y), (x+1,y+1)])
                        if y - 1 >= 0:
                            if board[x+1,y-1] == "" or board[x+1,y-1] == "X":
                                pass
                            elif board[x+1,y-1][1] != color:
                                # print("PAWN ATTACKED")
                                allMoves.append([moveValues["t"+board[x+1,y-1][0]] + mp_val, (x,y), (x+1,y-1)])
                        
                    case "n":
                        print("Knight")
                        allMoves.extend( getKnightMoves(x,y) )
                        pass
                    case "r":
                        print("Rook")
                        allMoves.extend( getRookMoves(x,y) )
                    case "b":
                        print("Bishop")
                        allMoves.extend( getBishopMoves(x,y) )
                    case "q":
                        print("Queen")
                        allMoves.extend( getQueenMoves(x,y) )
                    case "k":
                        print("King")
                        allMoves.extend( getKingMoves(x,y) )
                    case _:
                        print("Zis is not on of ours !")
                        sys.exit("Stopping execution.")
                
                print("All moves", allMoves)
                return allMoves
            

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
            


            allMoves = getAllMoves()

            if len(allMoves) != 0:
                # Hard coded getMax() function because had issues.
                highestScore = 0
                highestIndex = 0
                for index,value in enumerate(allMoves):
                    if value[0] > highestScore:
                        highestScore = value[0]
                        highestIndex = index
                everyPieceBestMove.append(allMoves[highestIndex])

            

    def getMax(moves):
        highestScore = 0
        highestIndex = 0
        for index,value in enumerate(moves):
            if value[0] > highestScore:
                highestScore = value[0]
                highestIndex = index
        return moves[highestIndex]
    
    print("everyPieceBestMove : ", everyPieceBestMove)
    if len(everyPieceBestMove) != 0:
        finalMove = getMax(everyPieceBestMove)
        print("Final move : ", finalMove, " that took", time.time() - startTime, " seconds !")
        return finalMove[1], finalMove[2]
    
    return (0,0), (0,0)


register_chess_bot("MinMax", minMaxBot)
