from Bots.ChessBotList import register_chess_bot

from time import time

nbr_nodes = 0
make_move_time = []
evaluate_time = []
generate_moves_time = []
order_moves_time = []

#region FUNCTIONS
def load_from_string(board):
    squares = [tuple()] * 64
    for y in range(8):
        for x in range(8):
            symbol = board[y][x]
            index = (7 - y) * 8 + (7 - x)
            if symbol == "":
                squares[index] = Pieces.none, Pieces.none
            else:
                color = Pieces.white if symbol[1] == "w" else Pieces.black
                piece = MoveUtils.piece_type_from_symbol.get(symbol[0])
                squares[index] = piece, color
    return squares
    
def precompute_move_data():
    num_square_to_edge = [None] * 64
    for file in range(8):
        for rank in range(8):
            num_up = 7 - rank
            num_down = rank
            num_left = file
            num_right = 7 - file
            square_index = rank * 8 + file

            num_square_to_edge[square_index] = [
                num_up,  # 0: up
                num_down,  # 1: down
                num_left,  # 2: left
                num_right,  # 3: right
                min(num_up, num_left),  # 4: up_left
                min(num_down, num_left),  # 5: down_left
                min(num_up, num_right),  # 6: up_right
                min(num_down, num_right),  # 7: down_right
            ]
    return num_square_to_edge

def get_pawn_directions(player_sequence) -> dict[int, int]:
    """
    player_sequence
        0w0 : 
        - 0 = ID de l'équipe
        - w = couleur : white
        - 0 = orientation du plateau
    
        1b2
        - 1 = ID de l'équipe
        - b = couleur : black
        - 2 = orientation du plateau
    
    orientation
        '0': White Down (-8), Black Up (+8)
        '2': White Up (+8), Black Down (-8) (Assumed standard)
    """
    orientation = player_sequence[2]
    if orientation == "0":
        return {Pieces.white: MoveUtils.down, Pieces.black: MoveUtils.up}
    else:
        return {Pieces.white: MoveUtils.up, Pieces.black: MoveUtils.down}

def index_to_xy(n: int):
    y = 7 - (n // 8)
    x = 7 - (n % 8)
    return y, x

def make_move(squares, move):
    st = time()
    # copy the board
    new_squares = squares[:]

    # get the piece at start square
    piece = new_squares[move.start_square]

    # if piece is pawn and at last square, transform to queen
    target_y = index_to_xy(move.target_square)[0]
    if piece[0] == Pieces.pawn and (target_y == 7 or target_y == 0):
        piece = (Pieces.queen, piece[1])

    # move piece to target square
    new_squares[move.target_square] = piece

    # clear the start square
    new_squares[move.start_square] = (Pieces.none, Pieces.none)

    make_move_time.append(time() - st)
    return new_squares
#endregion

#region CLASSES
class SearchTimeout(Exception):
    pass

class Pieces:
    none = 0

    king = 1
    pawn = 2
    knight = 3
    bishop = 4
    rook = 5
    queen = 6

    white = 8
    black = 16

class Move:
    __slots__ = "start_square", "target_square"
    def __init__(self, start_square, target_square):
        self.start_square = start_square
        self.target_square = target_square

class MoveUtils:
    direction_offsets = [8, -8, -1, 1, 7, -9, 9, -7]

    num_squares_to_edges = precompute_move_data()

    piece_type_from_symbol = {
        "k": Pieces.king,
        "q": Pieces.queen,
        "n": Pieces.knight,
        "b": Pieces.bishop,
        "r": Pieces.rook,
        "p": Pieces.pawn,
    }

    up = 8
    down = -8
    left = -1
    right = 1
    up_left = 7
    up_right = 9
    down_left = -9
    down_right = -7

class PiecesValues:
    get_piece_value = {
        Pieces.pawn : 10,
        Pieces.knight : 30,
        Pieces.bishop : 30,
        Pieces.rook : 50,
        Pieces.queen : 90,
        Pieces.king : 900,
    }

    pawn_table = [
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
        5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,
        1.0,  1.0,  2.0,  3.0,  3.0,  2.0,  1.0,  1.0,
        0.5,  0.5,  1.0,  2.5,  2.5,  1.0,  0.5,  0.5,
        0.0,  0.0,  0.0,  2.0,  2.0,  0.0,  0.0,  0.0,
        0.5, -0.5, -1.0,  0.0,  0.0, -1.0, -0.5,  0.5,
        0.5,  1.0,  1.0, -2.0, -2.0,  1.0,  1.0,  0.5,
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
    ]

    knight_table = [
        -5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0,
        -4.0, -2.0,  0.0,  0.0,  0.0,  0.0, -2.0, -4.0,
        -3.0,  0.0,  1.0,  1.5,  1.5,  1.0,  0.0, -3.0,
        -3.0,  0.5,  1.5,  2.0,  2.0,  1.5,  0.5, -3.0,
        -3.0,  0.0,  1.5,  2.0,  2.0,  1.5,  0.0, -3.0,
        -3.0,  0.5,  1.0,  1.5,  1.5,  1.0,  0.5, -3.0,
        -4.0, -2.0,  0.0,  0.5,  0.5,  0.0, -2.0, -4.0,
        -5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0,
    ]

    bishop_table = [
        -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0,
        -1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0,
        -1.0,  0.0,  0.5,  1.0,  1.0,  0.5,  0.0, -1.0,
        -1.0,  0.5,  0.5,  1.0,  1.0,  0.5,  0.5, -1.0,
        -1.0,  0.0,  1.0,  1.0,  1.0,  1.0,  0.0, -1.0,
        -1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0, -1.0,
        -1.0,  0.5,  0.0,  0.0,  0.0,  0.0,  0.5, -1.0,
        -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0,
    ]

    rook_table = [
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
        0.5,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  0.5,
        -0.5, 0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
        -0.5, 0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
        -0.5, 0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
        -0.5, 0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
        -0.5, 0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
        0.0,  0.0,  0.0,  0.5,  0.5,  0.0,  0.0,  0.0,
    ]

    queen_table = [
        -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0,
        -1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0,
        -1.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0,
        -0.5,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5,
         0.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5,
        -1.0,  0.5,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0,
        -1.0,  0.0,  0.5,  0.0,  0.0,  0.0,  0.0, -1.0,
        -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0,
    ]

    king_table = [
        -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
        -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
        -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
        -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
        -2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0,
        -1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0,
         2.0,  2.0,  0.0,  0.0,  0.0,  0.0,  2.0,  2.0,
         2.0,  3.0,  1.0,  0.0,  0.0,  1.0,  3.0,  2.0,
    ]

    piece_tables = {
        Pieces.pawn: pawn_table,
        Pieces.knight: knight_table,
        Pieces.bishop: bishop_table,
        Pieces.rook: rook_table,
        Pieces.queen: queen_table,
        Pieces.king: king_table,
    }
    
class MoveGeneration:
    @staticmethod
    def generate_pawn_moves(squares, start_square, piece, pawn_directions):
        moves = list()
        piece_type, piece_color = piece
        (
            max_up,
            max_down,
            max_left,
            max_right,
            max_up_left,
            max_down_left,
            max_up_right,
            max_down_right,
        ) = MoveUtils.num_squares_to_edges[start_square]
        direction = pawn_directions[piece_color]
    
        if direction == MoveUtils.down:
            # Down (Move)
            if max_down > 0:
                target_square = start_square + MoveUtils.down
                if squares[target_square][0] == Pieces.none:
                    moves.append(Move(start_square, target_square))
            # Down-Left (Capture)
            if max_down_left > 0:
                target_square = start_square + MoveUtils.down_left
                target_piece, target_color = squares[target_square]
                if target_piece != Pieces.none and target_color != piece_color:
                    moves.append(Move(start_square, target_square))
            # Down-Right (Capture)
            if max_down_right > 0:
                target_square = start_square + MoveUtils.down_right
                target_piece, target_color = squares[target_square]
                if target_piece != Pieces.none and target_color != piece_color:
                    moves.append(Move(start_square, target_square))
    
        elif direction == MoveUtils.up:
            # Up (Move)
            if max_up > 0:
                target_square = start_square + MoveUtils.up
                if squares[target_square][0] == Pieces.none:
                    moves.append(Move(start_square, target_square))
            # Up-Left (Capture)
            if max_up_left > 0:
                target_square = start_square + MoveUtils.up_left
                target_piece, target_color = squares[target_square]
                if target_piece != Pieces.none and target_color != piece_color:
                    moves.append(Move(start_square, target_square))
            # Up-Right (Capture)
            if max_up_right > 0:
                target_square = start_square + MoveUtils.up_right
                target_piece, target_color = squares[target_square]
                if target_piece != Pieces.none and target_color != piece_color:
                    moves.append(Move(start_square, target_square))
    
        return moves
    
    @staticmethod
    def generate_king_moves(squares, start_square, piece):
        moves = list()
        piece_color = piece[1]
    
        for i in range(8):
            max_steps = MoveUtils.num_squares_to_edges[start_square][i]
            if max_steps > 0:
                target = start_square + MoveUtils.direction_offsets[i]
                if squares[target][1] != piece_color:
                    moves.append(Move(start_square, target))
        return moves
    
    @staticmethod
    def generate_knight_moves(squares, start_square, piece):
        moves = list()
        piece_color = piece[1]
        max_up, max_down, max_left, max_right = MoveUtils.num_squares_to_edges[
            start_square
        ][:4]
    
        # big : up-left (2 left, 1 up)
        if max_left >= 2 and max_up >= 1:
            target_square = start_square - 2 + MoveUtils.up
            if squares[target_square][1] != piece_color:
                moves.append(Move(start_square, target_square))
    
        # big : up-right (2 right, 1 up)
        if max_right >= 2 and max_up >= 1:
            target_square = start_square + 2 + MoveUtils.up
            if squares[target_square][1] != piece_color:
                moves.append(Move(start_square, target_square))
    
        # big : down-left (2 left, 1 down)
        if max_left >= 2 and max_down >= 1:
            target_square = start_square - 2 + MoveUtils.down
            if squares[target_square][1] != piece_color:
                moves.append(Move(start_square, target_square))
    
        # big : down-right (2 right, 1 down)
        if max_right >= 2 and max_down >= 1:
            target_square = start_square + 2 + MoveUtils.down
            if squares[target_square][1] != piece_color:
                moves.append(Move(start_square, target_square))
    
        # small : up-left (1 left, 2 up)
        if max_left >= 1 and max_up >= 2:
            target_square = start_square - 1 + 2 * MoveUtils.up
            if squares[target_square][1] != piece_color:
                moves.append(Move(start_square, target_square))
    
        # small : up-right (1 right, 2 up)
        if max_right >= 1 and max_up >= 2:
            target_square = start_square + 1 + 2 * MoveUtils.up
            if squares[target_square][1] != piece_color:
                moves.append(Move(start_square, target_square))
    
        # small : down-left (1 left, 2 down)
        if max_left >= 1 and max_down >= 2:
            target_square = start_square - 1 + 2 * MoveUtils.down
            if squares[target_square][1] != piece_color:
                moves.append(Move(start_square, target_square))
    
        # small : down-right (1 right, 2 down)
        if max_right >= 1 and max_down >= 2:
            target_square = start_square + 1 + 2 * MoveUtils.down
            if squares[target_square][1] != piece_color:
                moves.append(Move(start_square, target_square))
    
        return moves
    
    @staticmethod
    def generate_sliding_moves(squares, start_square, piece):
        moves = list()
        piece_type, piece_color = piece
    
        start_dir_index = 0
        end_dir_index = 0
    
        match piece_type:
            case Pieces.bishop:
                start_dir_index = 4
                end_dir_index = 7
            case Pieces.rook:
                start_dir_index = 0
                end_dir_index = 3
            case Pieces.queen:
                start_dir_index = 0
                end_dir_index = 7
    
        for direction_index in range(start_dir_index, end_dir_index + 1):
            for n in range(MoveUtils.num_squares_to_edges[start_square][direction_index]):
                target_square = start_square + MoveUtils.direction_offsets[
                    direction_index
                ] * (n + 1)
                color_on_target = squares[target_square][1]
    
                # blocked by friendly piece
                if color_on_target == piece_color:
                    break
    
                moves.append(Move(start_square, target_square))
    
                # blocked by enemy piece (can capture but stop after)
                if color_on_target != Pieces.none:
                    break
        return moves
#endregion

def chess_bot(player_sequence, board, time_budget, **kwargs):
    start_time = time()
    generate_moves_memo = {}
    alpha_beta_memoization = {}
    
    def order_moves(squares, moves, pawn_directions):
        st = time()
        ordered = []
    
        for move in moves :
            move_score_guess = 0
            piece = squares[move.start_square]
            move_piece_type, move_piece_color = squares[move.start_square]
            captured_piece_type, caputre_piece_color = squares[move.target_square]
    
            if captured_piece_type != Pieces.none :
                move_score_guess = 10 * PiecesValues.get_piece_value.get(captured_piece_type) - PiecesValues.get_piece_value.get(move_piece_type)
    
            target_y = index_to_xy(move.target_square)[0]
            if piece[0] == Pieces.pawn and (target_y == 7 or target_y == 0):
                move_score_guess += PiecesValues.get_piece_value.get(Pieces.queen)
            
            ordered.append([move, move_score_guess])
        
        ordered.sort(key=lambda x: x[1], reverse=True)
        p = [move for move, score in ordered]
        order_moves_time.append(time() - st)
        return p
    
    def alpha_beta(squares, color: int, depth: int, pawn_directions, alpha, beta) -> int:
        global nbr_nodes
        nbr_nodes += 1
        
        if depth <= 0:
            return evaluate(squares, color, pawn_directions)

        sq_key = tuple(squares), depth
        if sq_key in alpha_beta_memoization:
            return alpha_beta_memoization[sq_key]
        
        moves = generate_moves(squares, color, pawn_directions)
        if not moves:
            # Checkmate or Stalemate. Prioritize faster checkmates.
            return -PiecesValues.get_piece_value[Pieces.king] - depth
    
        moves = order_moves(squares, moves, pawn_directions)
        for m in moves:
            if time() - start_time >= time_budget - 0.03:
                raise SearchTimeout()
            
            if squares[m.target_square][0] == Pieces.king:
                return PiecesValues.get_piece_value[Pieces.king] + depth
            new_squares = make_move(squares, m)
            score = -alpha_beta(new_squares, Pieces.white if color == Pieces.black else Pieces.black, depth - 1, pawn_directions, -beta, -alpha)
            if score >= beta :
                return beta
            alpha = int(max(score, alpha))

        alpha_beta_memoization[sq_key] = alpha
        return alpha

    def find_best_move(squares, color: int, depth: int, pawn_directions) -> tuple[tuple[tuple[int, int], tuple[int, int]], int]:
        best_move = Move(0, 0)
        best_eval = float("-inf")
    
        moves = generate_moves(squares, color, pawn_directions)
    
        for m in moves:
            if squares[m.target_square][0] == Pieces.king:
                return (index_to_xy(m.start_square), index_to_xy(m.target_square)), PiecesValues.get_piece_value[Pieces.king] + depth
        
            new_squares = make_move(squares, m)
            eval = -alpha_beta(new_squares, Pieces.white if color == Pieces.black else Pieces.black, depth - 1, pawn_directions, float("-inf"), float("inf"))
    
            if eval > best_eval:
                best_eval = eval
                best_move = m
        
        return (index_to_xy(best_move.start_square), index_to_xy(best_move.target_square)), best_eval

    def generate_moves(squares, mycolor, pawn_directions):
        dict_key = tuple(squares), mycolor
        if dict_key in generate_moves_memo:
            return generate_moves_memo[dict_key]

        st = time()
        moves = list()
        for start_square, piece in enumerate(squares):
            piece_type, piece_color = piece
            if piece_type and piece_color == mycolor:
                match piece_type:
                    case Pieces.king:
                        moves.extend(MoveGeneration.generate_king_moves(squares, start_square, piece))
                    case Pieces.pawn:
                        moves.extend(MoveGeneration.generate_pawn_moves(squares, start_square, piece, pawn_directions))
                    case Pieces.knight:
                        moves.extend(MoveGeneration.generate_knight_moves(squares, start_square, piece))
                    case Pieces.bishop | Pieces.rook | Pieces.queen:
                        moves.extend(MoveGeneration.generate_sliding_moves(squares, start_square, piece))
                    case _:
                        print("INFO : problem generating moves")
        
        generate_moves_memo[dict_key] = moves
        generate_moves_time.append(time() - st)
        return moves

    def evaluate(squares, mycolor, pawn_directions):
        st = time()
        material = 0

        for square_index in range(64):
            piece_type, piece_color = squares[square_index]

            if piece_type == Pieces.none:
                continue
            
            piece_value = PiecesValues.get_piece_value[piece_type]
            
            index = 63 - square_index if pawn_directions[Pieces.white] != MoveUtils.down else square_index
            position_bonus = PiecesValues.piece_tables[piece_type][index]
            
            total_value = piece_value + position_bonus

            if piece_color == mycolor:
                material += total_value
            else:
                material -= total_value

        evaluate_time.append(time() - st)
        return material

    global make_move_time, evaluate_time, generate_moves_time, order_moves_time, nbr_nodes
    make_move_time = []
    evaluate_time = []
    generate_moves_time = []
    order_moves_time = []
    nbr_nodes = 0
    
    loaded_board = load_from_string(board)
    pawn_directions = get_pawn_directions(player_sequence)
    mycolor = Pieces.white if player_sequence[1] == "w" else Pieces.black

    best_current_move = ((0,0), (0,0)), -float('inf')
    depth = 1
    while True:
        if time() - start_time >= time_budget - 0.03:
            break
        try:            
            best_current_move = find_best_move(loaded_board, mycolor, depth, pawn_directions)
            # print(depth, nbr_nodes)
            depth += 1
            nbr_nodes = 0
        except SearchTimeout:
            break
    
    temps_total = time() - start_time
    # def getPourcentage(t):
    #     return str(round(sum(t)/temps_total * 100)) + "%"
    print("total :", temps_total)
    # print("make_move total: ", sum(make_move_time), "->", getPourcentage(make_move_time))
    # print("evaluate total: ", sum(evaluate_time), "->", getPourcentage(evaluate_time))
    # print("generate_moves total: ", sum(generate_moves_time), "->", getPourcentage(generate_moves_time))
    # print("order_moves total: ", sum(order_moves_time), "->", getPourcentage(order_moves_time))
    
    print(f"last_best (depth {depth})", best_current_move)
    return best_current_move[0]

register_chess_bot("TigreBot", chess_bot)