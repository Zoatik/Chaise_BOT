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
        "ptp" : 2,
        "ptn" : 3,
        "ptr" : 3,
        "ptb" : 4,
        "ptq" : 8,
        "ptk" : 100,

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
                                allMoves.append([moveValues["mp"], (x,y), (x+1,y)])
                        # Diag attacks ?
                        print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSCANNNNNNNNNNNNNNNNNNNNNNN")
                        if y + 1 <= 7:
                            if board[x+1,y+1] == "" or board[x+1,y+1] == "X":
                                pass
                            elif board[x+1,y+1][1] != color:
                                # print("PAWN ATTACKED")
                                allMoves.append([moveValues["pt"+board[x+1,y+1][0]], (x,y), (x+1,y+1)])
                        if y - 1 >= 0:
                            if board[x+1,y-1] == "" or board[x+1,y-1] == "X":
                                pass
                            elif board[x+1,y-1][1] != color:
                                # print("PAWN ATTACKED")
                                allMoves.append([moveValues["pt"+board[x+1,y-1][0]], (x,y), (x+1,y-1)])
                        
                    case "n":
                        print("Knight")
                        pass
                    case "r":
                        print("Rook")
                        pass
                    case "b":
                        print("Bishop")
                        pass
                    case "q":
                        print("Queen")
                        pass
                    case "k":
                        print("King")
                        pass
                    case _:
                        print("Zis is not on of ours !")
                        sys.exit("Stopping execution.")
                
                print("All moves", allMoves)
                return allMoves
            
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
