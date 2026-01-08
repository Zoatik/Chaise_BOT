
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

    bot_color = player_sequence[1]
    import time

    search_stats = {
        'nodes': 0,
        'max_depth': 0,
        'cutoffs': 0,
        'q_nodes': 0,
        'time_up': False
    }
    transposition_table = {}
    killer_moves = {}
    history_table = {}

    def get_color_orientation(color):
        return 1 if color == bot_color else -1

    piece_values = {
        'p': 10,
        'n': 30,
        'b': 30,
        'r': 50,
        'q': 90,
        'k': 10000
    }
    board_mask = 0xffffffffffffffff

    pawn_table = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [5, 5, 5, 5, 5, 5, 5, 5],
        [1, 1, 2, 3, 3, 2, 1, 1],
        [0, 0, 0, 2, 2, 0, 0, 0],
        [0, 0, 0, -2, -2, 0, 0, 0],
        [1, -1, -2, 0, 0, -2, -1, 1],
        [1, 2, 2, -2, -2, 2, 2, 1],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]

    knight_table = [
        [-5, -4, -3, -3, -3, -3, -4, -5],
        [-4, -2, 0, 0, 0, 0, -2, -4],
        [-3, 0, 1, 1, 1, 1, 0, -3],
        [-3, 0, 1, 2, 2, 1, 0, -3],
        [-3, 0, 1, 2, 2, 1, 0, -3],
        [-3, 0, 1, 1, 1, 1, 0, -3],
        [-4, -2, 0, 0, 0, 0, -2, -4],
        [-5, -4, -3, -3, -3, -3, -4, -5],
    ]

    bishop_table = [
        [-2, -1, -1, -1, -1, -1, -1, -2],
        [-1, 0, 0, 0, 0, 0, 0, -1],
        [-1, 0, 1, 1, 1, 1, 0, -1],
        [-1, 1, 1, 1, 1, 1, 1, -1],
        [-1, 0, 1, 1, 1, 1, 0, -1],
        [-1, 1, 1, 1, 1, 1, 1, -1],
        [-1, 0, 0, 0, 0, 0, 0, -1],
        [-2, -1, -1, -1, -1, -1, -1, -2],
    ]

    rook_table = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [-1, 0, 0, 0, 0, 0, 0, -1],
        [-1, 0, 0, 0, 0, 0, 0, -1],
        [-1, 0, 0, 0, 0, 0, 0, -1],
        [-1, 0, 0, 0, 0, 0, 0, -1],
        [-1, 0, 0, 0, 0, 0, 0, -1],
        [0, 0, 0, 1, 1, 0, 0, 0],
    ]

    queen_table = [
        [-2, -1, -1, 0, 0, -1, -1, -2],
        [-1, 0, 0, 0, 0, 0, 0, -1],
        [-1, 0, 1, 1, 1, 1, 0, -1],
        [0, 0, 1, 1, 1, 1, 0, -1],
        [0, 0, 1, 1, 1, 1, 0, -1],
        [-1, 0, 1, 1, 1, 1, 0, -1],
        [-1, 0, 0, 0, 0, 0, 0, -1],
        [-2, -1, -1, 0, 0, -1, -1, -2],
    ]

    king_table = [
        [-3, -4, -4, -5, -5, -4, -4, -3],
        [-3, -4, -4, -5, -5, -4, -4, -3],
        [-3, -4, -4, -5, -5, -4, -4, -3],
        [-3, -4, -4, -5, -5, -4, -4, -3],
        [-2, -3, -3, -4, -4, -3, -3, -2],
        [-1, -2, -2, -2, -2, -2, -2, -1],
        [2, 2, 0, 0, 0, 0, 2, 2],
        [2, 3, 1, 0, 0, 1, 3, 2],
    ]

    piece_square_tables = {
        'p': pawn_table,
        'n': knight_table,
        'b': bishop_table,
        'r': rook_table,
        'q': queen_table,
        'k': king_table,
    }

    def get_positional_value(piece_type, x, y, is_bot_piece):
        table = piece_square_tables.get(piece_type)
        if not table:
            return 0
        if is_bot_piece:
            return table[7 - x][y]
        return table[x][y]

    position_bitboards = {
        'w': {
            'p' : 0,
            'n': 0,
            'b': 0,
            'r': 0,
            'q': 0,
            'k': 0
        },
        'b': {
            'p' : 0,
            'n': 0,
            'b': 0,
            'r': 0,
            'q': 0,
            'k': 0
        }
    }

    def evaluate(board):
        material = 0
        bot_king = None
        opp_king = None
        for x in range(board.shape[0]):
            for y in range(board.shape[1]):
                piece = board[x,y]
                if piece == '':
                    continue
                piece_type = piece[0]
                is_bot_piece = piece[1] == bot_color
                color_multiplier = 1 if is_bot_piece else -1
                material += color_multiplier * piece_values.get(piece_type, 0)
                material += color_multiplier * get_positional_value(piece_type, x, y, is_bot_piece)
                if piece_type == 'k':
                    if is_bot_piece:
                        bot_king = (x, y)
                    else:
                        opp_king = (x, y)

        if bot_king is None:
            return -piece_values['k']
        if opp_king is None:
            return piece_values['k']

        opp_color = 'b' if bot_color == 'w' else 'w'
        hanging_penalty = 0
        for x in range(board.shape[0]):
            for y in range(board.shape[1]):
                piece = board[x, y]
                if piece == '' or piece[0] == 'k':
                    continue
                piece_color = piece[1]
                capture_moves = get_captures_on_square(board, opp_color if piece_color == bot_color else bot_color, x, y)
                if not capture_moves:
                    continue
                worst_gain = 0
                for cap_move in capture_moves:
                    gain = see_exchange(board, cap_move)
                    if gain > worst_gain:
                        worst_gain = gain
                if worst_gain > 0:
                    penalty = min(worst_gain, piece_values.get(piece[0], 0))
                    if piece_color == bot_color:
                        hanging_penalty -= penalty
                    else:
                        hanging_penalty += penalty

        material += hanging_penalty
        return material

    def bitboard_pos_to_coord(bitboard):
        for i in range(64):
            if bitboard & (1 << i):
                return (i // 8, i % 8)
        return None

    def generate_bitboards(board):
        w_pawn_bitboard = 0
        w_knight_bitboard = 0
        w_bishop_bitboard = 0
        w_rook_bitboard = 0
        w_queen_bitboard = 0
        w_king_bitboard = 0

        b_pawn_bitboard = 0
        b_knight_bitboard = 0
        b_bishop_bitboard = 0
        b_rook_bitboard = 0
        b_queen_bitboard = 0
        b_king_bitboard = 0


        for x in range(board.shape[0]):
            for y in range(board.shape[1]):
                piece = board[x,y]
                piece_type = piece[0] if piece != '' else ''
                piece_color = piece[1] if piece != '' else ''
                match piece_color:
                    case 'b':
                        match piece_type:
                            case 'p':
                                b_pawn_bitboard |= (1 << (x * 8 + y))
                            case 'n':
                                b_knight_bitboard |= (1 << (x * 8 + y))
                            case 'b':
                                b_bishop_bitboard |= (1 << (x * 8 + y))
                            case 'r':
                                b_rook_bitboard |= (1 << (x * 8 + y))
                            case 'q':
                                b_queen_bitboard |= (1 << (x * 8 + y))
                            case 'k':
                                b_king_bitboard |= (1 << (x * 8 + y))
                            case _:
                                pass
                    case 'w':
                        match piece_type:
                            case 'p':
                                w_pawn_bitboard |= (1 << (x * 8 + y))
                            case 'n':
                                w_knight_bitboard |= (1 << (x * 8 + y))
                            case 'b':
                                w_bishop_bitboard |= (1 << (x * 8 + y))
                            case 'r':
                                w_rook_bitboard |= (1 << (x * 8 + y))
                            case 'q':
                                w_queen_bitboard |= (1 << (x * 8 + y))
                            case 'k':
                                w_king_bitboard |= (1 << (x * 8 + y))
                            case _:
                                pass
                
        return {
            'w': {
                'p': w_pawn_bitboard,
                'n': w_knight_bitboard,
                'b': w_bishop_bitboard,
                'r': w_rook_bitboard,
                'q': w_queen_bitboard,
                'k': w_king_bitboard
            },
            'b': {
                'p': b_pawn_bitboard,
                'n': b_knight_bitboard,
                'b': b_bishop_bitboard,
                'r': b_rook_bitboard,
                'q': b_queen_bitboard,
                'k': b_king_bitboard
            }
        }
    
    def get_other_pieces(mycolor):
        other_color = 'b' if mycolor == 'w' else 'w'
        other_pieces = 0
        for p_type in position_bitboards[other_color]:
            other_pieces |= position_bitboards[other_color][p_type]
        return other_pieces
    
    def get_own_pieces(mycolor):
        own_pieces = 0
        for p_type in position_bitboards[mycolor]:
            own_pieces |= position_bitboards[mycolor][p_type]
        return own_pieces
    
    def get_all_pieces():
        all_pieces = 0
        for color in position_bitboards:
            for p_type in position_bitboards[color]:
                all_pieces |= position_bitboards[color][p_type]
        return all_pieces
    

    def iter_bit_positions(bitboard):
        while bitboard:
            lsb = bitboard & -bitboard
            idx = lsb.bit_length() - 1
            yield idx
            bitboard ^= lsb

    def get_attack_bits(pos_bitboard, p_type, p_color):
        if p_type != 'p':
            return get_moves(pos_bitboard, p_type, p_color)
        direction = get_color_orientation(p_color)
        file_a_mask = 0xfefefefefefefefe
        file_h_mask = 0x7f7f7f7f7f7f7f7f
        if direction == 1:
            attacks = ((pos_bitboard & file_a_mask) << 7) | ((pos_bitboard & file_h_mask) << 9)
        else:
            attacks = ((pos_bitboard & file_a_mask) >> 9) | ((pos_bitboard & file_h_mask) >> 7)
        return attacks & board_mask

    def get_moves(pos_bitboard, p_type, p_color):
        match p_type:
            case 'p':
                result = get_pawn_possible_bits(pos_bitboard, p_color)
            case 'n':
                result = get_knight_possible_bits(pos_bitboard, p_color)
            case 'b':
                result = get_bishop_possible_bits(pos_bitboard, p_color)
            case 'r':
                result = get_rook_possible_bits(pos_bitboard, p_color)
            case 'q':
                result = get_queen_possible_bits(pos_bitboard, p_color)
            case 'k':
                result = get_king_possible_bits(pos_bitboard, p_color)
            case _:
                result = 0
        return result & board_mask

    def get_pawn_possible_bits(pos_bitboard, p_color):
        possible_biboard = 0
        direction = get_color_orientation(p_color)
        file_a_mask = 0xfefefefefefefefe
        file_h_mask = 0x7f7f7f7f7f7f7f7f
        # Single move forward + diagonal captures
        if direction == 1:
            possible_biboard |= (pos_bitboard << 8) & ~get_all_pieces()
            possible_biboard |= ((pos_bitboard & file_a_mask) << 7) & get_other_pieces(p_color)  # capture left
            possible_biboard |= ((pos_bitboard & file_h_mask) << 9) & get_other_pieces(p_color)  # capture right
        else:
            possible_biboard |= (pos_bitboard >> 8) & ~get_all_pieces()
            possible_biboard |= ((pos_bitboard & file_a_mask) >> 9) & get_other_pieces(p_color)  # capture left
            possible_biboard |= ((pos_bitboard & file_h_mask) >> 7) & get_other_pieces(p_color)  # capture right


        return possible_biboard
    
    def get_knight_possible_bits(pos_bitboard, p_color):
        possible_biboard = 0
        not_a = 0xfefefefefefefefe
        not_h = 0x7f7f7f7f7f7f7f7f
        not_ab = 0xfcfcfcfcfcfcfcfc
        not_gh = 0x3f3f3f3f3f3f3f3f
        # Up 2, Left 1
        possible_biboard |= ((pos_bitboard & not_a) << 15) & ~get_own_pieces(p_color)
        # Up 2, Right 1
        possible_biboard |= ((pos_bitboard & not_h) << 17) & ~get_own_pieces(p_color)
        # Right 2, Up 1
        possible_biboard |= ((pos_bitboard & not_gh) << 10) & ~get_own_pieces(p_color)
        # Right 2, Down 1
        possible_biboard |= ((pos_bitboard & not_gh) >> 6) & ~get_own_pieces(p_color)
        # Down 2, Right 1
        possible_biboard |= ((pos_bitboard & not_h) >> 15) & ~get_own_pieces(p_color)
        # Down 2, Left 1
        possible_biboard |= ((pos_bitboard & not_a) >> 17) & ~get_own_pieces(p_color)
        # Left 2, Down 1
        possible_biboard |= ((pos_bitboard & not_ab) >> 10) & ~get_own_pieces(p_color)
        # Left 2, Up 1
        possible_biboard |= ((pos_bitboard & not_ab) << 6) & ~get_own_pieces(p_color)

        return possible_biboard
    
    def get_bishop_possible_bits(pos_bitboard, p_color):
        possible_biboard = 0
        own = get_own_pieces(p_color)
        other = get_other_pieces(p_color)
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for idx in iter_bit_positions(pos_bitboard):
            x = idx // 8
            y = idx % 8
            for dx, dy in directions:
                nx = x + dx
                ny = y + dy
                while 0 <= nx < 8 and 0 <= ny < 8:
                    bit = 1 << (nx * 8 + ny)
                    if bit & own:
                        break
                    possible_biboard |= bit
                    if bit & other:
                        break
                    nx += dx
                    ny += dy

        return possible_biboard
    
    def get_rook_possible_bits(pos_bitboard, p_color):
        possible_biboard = 0
        own = get_own_pieces(p_color)
        other = get_other_pieces(p_color)
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for idx in iter_bit_positions(pos_bitboard):
            x = idx // 8
            y = idx % 8
            for dx, dy in directions:
                nx = x + dx
                ny = y + dy
                while 0 <= nx < 8 and 0 <= ny < 8:
                    bit = 1 << (nx * 8 + ny)
                    if bit & own:
                        break
                    possible_biboard |= bit
                    if bit & other:
                        break
                    nx += dx
                    ny += dy

        return possible_biboard

    def get_queen_possible_bits(pos_bitboard, p_color):
        return get_bishop_possible_bits(pos_bitboard, p_color) | get_rook_possible_bits(pos_bitboard, p_color)

    def get_king_possible_bits(pos_bitboard, p_color):
        possible_biboard = 0
        own = get_own_pieces(p_color)
        directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        for idx in iter_bit_positions(pos_bitboard):
            x = idx // 8
            y = idx % 8
            for dx, dy in directions:
                nx = x + dx
                ny = y + dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    bit = 1 << (nx * 8 + ny)
                    if not (bit & own):
                        possible_biboard |= bit

        return possible_biboard

    def set_position_bitboards(current_board):
        position_bitboards.update(generate_bitboards(current_board))

    def generate_all_moves(current_board, color):
        set_position_bitboards(current_board)
        own_pieces = position_bitboards[color]
        all_moves = []

        def is_valid_move(move):
            (sx, sy), (dx, dy) = move
            if sx < 0 or sx > 7 or sy < 0 or sy > 7 or dx < 0 or dx > 7 or dy < 0 or dy > 7:
                return False
            piece = current_board[sx, sy]
            if piece == '' or piece[1] != color:
                return False
            dst = current_board[dx, dy]
            if dst != '' and dst[1] == color:
                return False
            return True

        for p_type, pos_bitboard in own_pieces.items():
            if pos_bitboard == 0:
                continue
            for src_idx in iter_bit_positions(pos_bitboard):
                src_bit = 1 << src_idx
                possible = get_moves(src_bit, p_type, color)
                if possible == 0:
                    continue
                sx = src_idx // 8
                sy = src_idx % 8
                for dst_idx in iter_bit_positions(possible):
                    dx = dst_idx // 8
                    dy = dst_idx % 8
                    move = ((sx, sy), (dx, dy))
                    if is_valid_move(move):
                        all_moves.append(move)

        return all_moves

    def apply_move(current_board, move):
        (sx, sy), (dx, dy) = move
        new_board = current_board.copy()
        new_board[dx, dy] = current_board[sx, sy]
        new_board[sx, sy] = ''
        return new_board

    def find_king(current_board, color):
        for x in range(current_board.shape[0]):
            for y in range(current_board.shape[1]):
                piece = current_board[x, y]
                if piece != '' and piece[0] == 'k' and piece[1] == color:
                    return (x, y)
        return None

    def king_capturable(current_board, color):
        king_pos = find_king(current_board, color)
        if king_pos is None:
            return True
        opp_color = 'b' if color == 'w' else 'w'
        attackers = get_attackers_values(current_board, king_pos[0], king_pos[1], opp_color)
        return len(attackers) > 0

    def get_attackers_values(current_board, target_x, target_y, color):
        set_position_bitboards(current_board)
        target_bit = 1 << (target_x * 8 + target_y)
        attackers = []
        for p_type, pos_bitboard in position_bitboards[color].items():
            if pos_bitboard == 0:
                continue
            for src_idx in iter_bit_positions(pos_bitboard):
                src_bit = 1 << src_idx
                if get_attack_bits(src_bit, p_type, color) & target_bit:
                    attackers.append(piece_values.get(p_type, 0))
        return attackers

    def get_captures_on_square(current_board, color, target_x, target_y):
        set_position_bitboards(current_board)
        target_bit = 1 << (target_x * 8 + target_y)
        capture_moves = []
        for p_type, pos_bitboard in position_bitboards[color].items():
            if pos_bitboard == 0:
                continue
            for src_idx in iter_bit_positions(pos_bitboard):
                src_bit = 1 << src_idx
                if get_attack_bits(src_bit, p_type, color) & target_bit:
                    sx = src_idx // 8
                    sy = src_idx % 8
                    capture_moves.append(((sx, sy), (target_x, target_y)))
        return capture_moves

    def see_exchange(current_board, move):
        (sx, sy), (dx, dy) = move
        moving_piece = current_board[sx, sy]
        captured_piece = current_board[dx, dy]
        if moving_piece == '' or captured_piece == '':
            return 0
        mover_color = moving_piece[1]
        opp_color = 'b' if mover_color == 'w' else 'w'
        moving_value = piece_values.get(moving_piece[0], 0)
        captured_value = piece_values.get(captured_piece[0], 0)

        next_board = apply_move(current_board, move)
        attackers = {
            mover_color: get_attackers_values(next_board, dx, dy, mover_color),
            opp_color: get_attackers_values(next_board, dx, dy, opp_color)
        }
        attackers[mover_color].append(moving_value)
        attackers[mover_color].sort()
        attackers[opp_color].sort()

        gain = [captured_value]
        side = opp_color
        while attackers[side]:
            value = attackers[side].pop(0)
            gain.append(value - gain[-1])
            side = mover_color if side == opp_color else opp_color

        for i in range(len(gain) - 2, -1, -1):
            gain[i] = max(-gain[i + 1], gain[i])

        return gain[0]

    def blunder_penalty(current_board, move):
        (sx, sy), (dx, dy) = move
        moving_piece = current_board[sx, sy]
        if moving_piece == '':
            return 0
        next_board = apply_move(current_board, move)
        mover_color = moving_piece[1]
        opp_color = 'b' if mover_color == 'w' else 'w'
        capture_moves = get_captures_on_square(next_board, opp_color, dx, dy)
        if not capture_moves:
            return 0
        worst_gain = 0
        for cap_move in capture_moves:
            gain = see_exchange(next_board, cap_move)
            if gain > worst_gain:
                worst_gain = gain
        return -worst_gain

    def add_killer_move(depth, move, current_board):
        (sx, sy), (dx, dy) = move
        if current_board[dx, dy] != '':
            return
        killers = killer_moves.get(depth, [])
        if move in killers:
            return
        killer_moves[depth] = [move] + killers[:1]

    def add_history(color, move, depth, current_board):
        (sx, sy), (dx, dy) = move
        if current_board[dx, dy] != '':
            return
        key = (color, sx, sy, dx, dy)
        history_table[key] = history_table.get(key, 0) + depth * depth

    def order_moves(moves, current_board, color_to_move, depth, apply_blunder_penalty=True):
        scored = []
        killers = killer_moves.get(depth, [])
        for move in moves:
            (sx, sy), (dx, dy) = move
            moving_piece = current_board[sx, sy]
            captured_piece = current_board[dx, dy]
            if moving_piece == '':
                continue
            moving_type = moving_piece[0]
            moving_color = moving_piece[1]
            is_bot_piece = moving_color == bot_color
            capture_value = piece_values.get(captured_piece[0], 0) if captured_piece != '' else 0
            pos_delta = get_positional_value(moving_type, dx, dy, is_bot_piece) - get_positional_value(moving_type, sx, sy, is_bot_piece)
            penalty = blunder_penalty(current_board, move) if apply_blunder_penalty else 0
            killer_bonus = 0
            if capture_value == 0 and move in killers:
                killer_bonus = 100
            history_bonus = 0
            if capture_value == 0:
                history_bonus = history_table.get((color_to_move, sx, sy, dx, dy), 0) // 5
            if capture_value > 0:
                exchange = see_exchange(current_board, move)
                score = exchange + pos_delta + penalty
            else:
                score = pos_delta + penalty + killer_bonus + history_bonus
            scored.append((score, move))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [move for _, move in scored]

    def time_exceeded(start_time, soft_limit):
        if soft_limit is None:
            return False
        if time.time() - start_time > soft_limit:
            search_stats['time_up'] = True
            return True
        return False

    def generate_capture_moves(current_board, color):
        moves = generate_all_moves(current_board, color)
        captures = []
        for move in moves:
            (sx, sy), (dx, dy) = move
            if current_board[dx, dy] != '':
                captures.append(move)
        return captures

    def quiescence_search(current_board, alpha, beta, color_to_move, start_time, soft_limit):
        search_stats['q_nodes'] += 1
        if time_exceeded(start_time, soft_limit):
            return evaluate(current_board)

        stand_pat = evaluate(current_board)
        if color_to_move == bot_color:
            if stand_pat >= beta:
                return stand_pat
            if stand_pat > alpha:
                alpha = stand_pat
            moves = generate_capture_moves(current_board, color_to_move)
            if moves:
                moves = order_moves(moves, current_board, color_to_move, 0, apply_blunder_penalty=False)
            for move in moves:
                next_board = apply_move(current_board, move)
                score = quiescence_search(next_board, alpha, beta, 'b' if color_to_move == 'w' else 'w', start_time, soft_limit)
                if score > alpha:
                    alpha = score
                if alpha >= beta:
                    search_stats['cutoffs'] += 1
                    break
            return alpha
        else:
            if stand_pat <= alpha:
                return stand_pat
            if stand_pat < beta:
                beta = stand_pat
            moves = generate_capture_moves(current_board, color_to_move)
            if moves:
                moves = order_moves(moves, current_board, color_to_move, 0, apply_blunder_penalty=False)
            for move in moves:
                next_board = apply_move(current_board, move)
                score = quiescence_search(next_board, alpha, beta, 'b' if color_to_move == 'w' else 'w', start_time, soft_limit)
                if score < beta:
                    beta = score
                if beta <= alpha:
                    search_stats['cutoffs'] += 1
                    break
            return beta

    def minimax(current_board, depth, alpha, beta, color_to_move, start_time, soft_limit, root_depth):
        search_stats['nodes'] += 1
        if depth > search_stats['max_depth']:
            search_stats['max_depth'] = depth
        if time_exceeded(start_time, soft_limit):
            return evaluate(current_board), None
        alpha_orig = alpha
        beta_orig = beta
        tt_key = (current_board.tobytes(), color_to_move, depth)
        tt_entry = transposition_table.get(tt_key)
        if tt_entry is not None:
            tt_depth, tt_score, tt_flag, tt_move = tt_entry
            if tt_depth >= depth:
                if tt_flag == 'EXACT':
                    return tt_score, tt_move
                if tt_flag == 'LOWER':
                    if tt_score > alpha:
                        alpha = tt_score
                elif tt_flag == 'UPPER':
                    if tt_score < beta:
                        beta = tt_score
                if alpha >= beta:
                    return tt_score, tt_move
        moves = generate_all_moves(current_board, color_to_move)
        if depth == 0 or not moves:
            score = quiescence_search(current_board, alpha, beta, color_to_move, start_time, soft_limit)
            return score, None
        moves = order_moves(moves, current_board, color_to_move, depth, apply_blunder_penalty=(depth > 1))
        if tt_entry is not None and tt_entry[3] in moves:
            moves.remove(tt_entry[3])
            moves.insert(0, tt_entry[3])

        maximizing = color_to_move == bot_color
        best_move = None

        trace_depth2 = kwargs.get('trace_depth2', False)
        if trace_depth2 and depth == root_depth:
            print(f"trace depth2: root depth={root_depth} moves={len(moves)}")
        if maximizing:
            best_score = -10**9
            for move in moves:
                if depth == root_depth:
                    if trace_depth2:
                        print(f"trace depth2: root move {move}")
                    (sx, sy), _ = move
                    moving_piece = current_board[sx, sy]
                    moving_value = piece_values.get(moving_piece[0], 0) if moving_piece != '' else 0
                    threshold = kwargs.get('root_blunder_threshold', None)
                    if threshold is None:
                        factor = kwargs.get('root_blunder_factor', 0.5)
                        threshold = moving_value * factor
                    if blunder_penalty(current_board, move) < -threshold:
                        if trace_depth2:
                            print(f"trace depth2: root move skipped by blunder_penalty {move}")
                        continue
                next_board = apply_move(current_board, move)
                if find_king(next_board, 'b' if bot_color == 'w' else 'w') is None:
                    return piece_values['k'], move
                if king_capturable(next_board, bot_color):
                    if trace_depth2 and depth == root_depth:
                        print(f"trace depth2: root move skipped by king_capturable {move}")
                    continue
                score, _ = minimax(next_board, depth - 1, alpha, beta, 'b' if color_to_move == 'w' else 'w', start_time, soft_limit, root_depth)
                if score > best_score:
                    best_score = score
                    best_move = move
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    search_stats['cutoffs'] += 1
                    add_killer_move(depth, move, current_board)
                    add_history(color_to_move, move, depth, current_board)
                    break
            if best_score <= alpha_orig:
                flag = 'UPPER'
            elif best_score >= beta_orig:
                flag = 'LOWER'
            else:
                flag = 'EXACT'
            transposition_table[tt_key] = (depth, best_score, flag, best_move)
            return best_score, best_move
        else:
            best_score = 10**9
            for move in moves:
                next_board = apply_move(current_board, move)
                if find_king(next_board, bot_color) is None:
                    return -piece_values['k'], move
                if trace_depth2 and depth == root_depth - 1:
                    print(f"trace depth2: opp move {move}")
                score, _ = minimax(next_board, depth - 1, alpha, beta, 'b' if color_to_move == 'w' else 'w', start_time, soft_limit, root_depth)
                if score < best_score:
                    best_score = score
                    best_move = move
                beta = min(beta, best_score)
                if beta <= alpha:
                    search_stats['cutoffs'] += 1
                    add_killer_move(depth, move, current_board)
                    add_history(color_to_move, move, depth, current_board)
                    break
            if best_score <= alpha_orig:
                flag = 'UPPER'
            elif best_score >= beta_orig:
                flag = 'LOWER'
            else:
                flag = 'EXACT'
            transposition_table[tt_key] = (depth, best_score, flag, best_move)
            return best_score, best_move

    def get_best_move(depth=4):
        search_stats['nodes'] = 0
        search_stats['max_depth'] = 0
        search_stats['cutoffs'] = 0
        search_stats['q_nodes'] = 0
        search_stats['time_up'] = False
        best_move = None
        best_score = -10**9
        start_time = time.time()
        max_depth = kwargs.get('max_depth', depth)
        max_depth_cap = kwargs.get('max_depth_cap', max_depth)
        soft_limit = time_budget * 0.9 if time_budget is not None else None
        depth_reached = 0
        for current_depth in range(1, max_depth_cap + 1):
            if soft_limit is not None and time.time() - start_time > soft_limit:
                break
            score, move = minimax(board, current_depth, -10**9, 10**9, bot_color, start_time, soft_limit, current_depth)
            if move is not None:
                best_move = move
                best_score = score
                depth_reached = current_depth
            if search_stats['time_up']:
                break
        elapsed = time.time() - start_time
        print(f"stats: nodes={search_stats['nodes']} q_nodes={search_stats['q_nodes']} max_depth={search_stats['max_depth']} cutoffs={search_stats['cutoffs']} depth_reached={depth_reached} time={elapsed:.3f}s score={best_score}")
        return best_move

    def play_random():
        import random
        all_moves = generate_all_moves(board, bot_color)
        if not all_moves:
            return None
        return random.choice(all_moves)
    

    max_depth = kwargs.get('max_depth', 6)
    return get_best_move(depth=max_depth)

#   Example how to register the function
register_chess_bot("ChaiseBotV4", chess_bot)
