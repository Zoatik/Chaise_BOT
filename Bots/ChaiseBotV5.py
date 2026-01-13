from Bots.ChessBotList import register_chess_bot
from time import time

BOT_NAME = "ChaiseBotV5"

def chess_bot(player_sequence, board, time_budget, **kwargs):
    # -------------------- Config --------------------
    print(board)
    USE_QUIESCENCE = True
    QUIESCENCE_MAX_PLIES = 16          # safety cap
    USE_KILLER_HISTORY = True          # allow history for killers
    MAX_KILLERS_PER_DEPTH = 2

    TIME_MARGIN = 0.03

    DEFAULT_MAX_DEPTH = 10

    # -------------------- Board / pieces helpers --------------------
    bot_color = player_sequence[1]          # 'w' or 'b'
    opp_color = 'b' if bot_color == 'w' else 'w'

    def in_bounds(x, y):
        return 0 <= x < 8 and 0 <= y < 8

    def xy_to_i(x, y):
        return x * 8 + y

    def i_to_xy(i):
        return i // 8, i % 8

    def load_squares_from_board(board_2d):
        squares = [('.', '.') for _ in range(64)]
        for x in range(8):
            for y in range(8):
                s = board_2d[x, y]
                if s == '':
                    continue
                squares[xy_to_i(x, y)] = (s[0], s[1])
        return squares

    def piece_value(pt):
        return {
            'p': 10,
            'n': 30,
            'b': 30,
            'r': 50,
            'q': 90,
            'k': 900  
        }.get(pt, 0)

    # -------------------- PST --------------------
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
    pst = {
        'p': pawn_table,
        'n': knight_table,
        'b': bishop_table,
        'r': rook_table,
        'q': queen_table,
        'k': king_table,
    }

    def pst_value(pt, x, y, is_bot_piece):
        t = pst.get(pt)
        if not t:
            return 0
        return t[7 - x][y] if is_bot_piece else t[x][y]

    # -------------------- Move generation --------------------
    knight_offsets = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                      (1, 2), (1, -2), (-1, 2), (-1, -2)]
    king_offsets = [(1, 0), (-1, 0), (0, 1), (0, -1),
                    (1, 1), (1, -1), (-1, 1), (-1, -1)]
    bishop_dirs = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    rook_dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    queen_dirs = bishop_dirs + rook_dirs

    def find_king(squares, color):
        for i, (pt, pc) in enumerate(squares):
            if pt == 'k' and pc == color:
                return i
        return None

    def generate_moves(squares, color):
        moves = []
        dir_x = 1 if color == bot_color else -1
        enemy = opp_color if color == bot_color else bot_color

        for si, (pt, pc) in enumerate(squares):
            if pc != color:
                continue
            sx, sy = i_to_xy(si)

            if pt == 'p':
                fx = sx + dir_x
                # forward
                if in_bounds(fx, sy):
                    fi = xy_to_i(fx, sy)
                    if squares[fi][0] == '.':
                        moves.append((si, fi))
                # captures
                for dy in (-1, 1):
                    cx, cy = sx + dir_x, sy + dy
                    if not in_bounds(cx, cy):
                        continue
                    ci = xy_to_i(cx, cy)
                    cpt, cpc = squares[ci]
                    if cpt != '.' and cpc == enemy:
                        moves.append((si, ci))

            elif pt == 'n':
                for dx, dy in knight_offsets:
                    nx, ny = sx + dx, sy + dy
                    if not in_bounds(nx, ny):
                        continue
                    ni = xy_to_i(nx, ny)
                    tpt, tpc = squares[ni]
                    if tpc != color:
                        moves.append((si, ni))

            elif pt == 'k':
                for dx, dy in king_offsets:
                    nx, ny = sx + dx, sy + dy
                    if not in_bounds(nx, ny):
                        continue
                    ni = xy_to_i(nx, ny)
                    tpt, tpc = squares[ni]
                    if tpc != color:
                        moves.append((si, ni))

            elif pt in ('b', 'r', 'q'):
                dirs = bishop_dirs if pt == 'b' else rook_dirs if pt == 'r' else queen_dirs
                for dx, dy in dirs:
                    nx, ny = sx + dx, sy + dy
                    while in_bounds(nx, ny):
                        ni = xy_to_i(nx, ny)
                        tpt, tpc = squares[ni]
                        if tpc == color:
                            break
                        moves.append((si, ni))
                        if tpt != '.':  # capture ends ray
                            break
                        nx += dx
                        ny += dy

        return moves

    def generate_capture_moves(squares, color):
        enemy = opp_color if color == bot_color else bot_color
        caps = []
        for si, di in generate_moves(squares, color):
            if squares[di][0] != '.' and squares[di][1] == enemy:
                caps.append((si, di))
        return caps

    # -------------------- Make move --------------------
    def make_move(squares, move):
        si, di = move
        pt, pc = squares[si]
        new_sq = squares[:]  

        tx, _ = i_to_xy(di)
        if pt == 'p':
            if (pc == bot_color and tx == 7) or (pc != bot_color and tx == 0):
                pt = 'q'

        new_sq[di] = (pt, pc)
        new_sq[si] = ('.', '.')
        return new_sq

    # -------------------- Evaluation --------------------
    WIN = 10**7

    def evaluate(squares, pov_color):
        bk = find_king(squares, bot_color)
        ok = find_king(squares, opp_color)
        if bk is None:
            return -WIN
        if ok is None:
            return WIN

        score = 0
        for i, (pt, pc) in enumerate(squares):
            if pt == '.':
                continue
            x, y = i_to_xy(i)
            val = piece_value(pt)
            pos = pst_value(pt, x, y, pc == bot_color)
            total = val + pos
            if pc == pov_color:
                score += total
            else:
                score -= total
        return int(score)

    # -------------------- Move ordering --------------------
    killer = {}    
    history = {}   

    def order_moves(squares, moves, color, depth):
        enemy = opp_color if color == bot_color else bot_color
        km = killer.get(depth, [])
        ordered = []

        for m in moves:
            si, di = m
            spt, _ = squares[si]
            dpt, dpc = squares[di]

            score = 0

            # Killer moves first (quiet)
            if USE_KILLER_HISTORY and dpt == '.' and m in km:
                score += 10_000

            # Captures: MVV-LVA
            if dpt != '.' and dpc == enemy:
                score += 1000 + 10 * piece_value(dpt) - piece_value(spt)

            # Promotion bonus
            if spt == 'p':
                tx, _ = i_to_xy(di)
                if (color == bot_color and tx == 7) or (color != bot_color and tx == 0):
                    score += 900

            # History bonus (quiet)
            if USE_KILLER_HISTORY and dpt == '.':
                score += history.get((color, si, di), 0)

            ordered.append((score, m))

        ordered.sort(key=lambda t: t[0], reverse=True)
        return [m for _, m in ordered]

    # -------------------- Search stats --------------------
    stats = {
        "tt_hits": 0,
        "tt_cutoffs": 0,
        "ab_cutoffs": 0,
        "nodes": 0,
    }

    # -------------------- TT --------------------

    tt = {}

    class SearchTimeout(Exception):
        pass

    start_time = time()
    hard_deadline = start_time + (time_budget if time_budget is not None else 0.0) - TIME_MARGIN

    def check_time():
        if time() >= hard_deadline:
            raise SearchTimeout()

    def tt_probe(squares_t, color, depth, alpha, beta):
        e = tt.get((squares_t, color))
        if e is None:
            return None
        stats["tt_hits"] += 1
        ed, es, ef, em = e
        if ed < depth:
            return None
        if ef == 'EXACT':
            stats["tt_cutoffs"] += 1
            return (es, em, alpha, beta, True)
        if ef == 'LOWER':
            alpha = max(alpha, es)
        elif ef == 'UPPER':
            beta = min(beta, es)
        if alpha >= beta:
            stats["tt_cutoffs"] += 1
            return (es, em, alpha, beta, True)
        return (es, em, alpha, beta, False)

    def tt_store(squares_t, color, depth, score, alpha_orig, beta_orig, best_move):
        if score <= alpha_orig:
            flag = 'UPPER'
        elif score >= beta_orig:
            flag = 'LOWER'
        else:
            flag = 'EXACT'
        prev = tt.get((squares_t, color))
        if prev is None or prev[0] <= depth:
            tt[(squares_t, color)] = (depth, score, flag, best_move)

    # -------------------- Quiescence --------------------
    def quiescence(squares, color, alpha, beta, ply=0):
        stats["nodes"] += 1
        check_time()
        stand = evaluate(squares, color)
        if stand >= beta:
            return stand
        if stand > alpha:
            alpha = stand

        if ply >= QUIESCENCE_MAX_PLIES:
            return alpha

        caps = generate_capture_moves(squares, color)
        if not caps:
            return alpha

        caps = order_moves(squares, caps, color, depth=0)

        for m in caps:
            # immediate king capture
            if squares[m[1]][0] == 'k':
                return WIN

            child = make_move(squares, m)
            next_color = opp_color if color == bot_color else bot_color
            score = -quiescence(child, next_color, -beta, -alpha, ply + 1)
            if score >= beta:
                return score
            if score > alpha:
                alpha = score
        return alpha

    # -------------------- Negamax alpha-beta --------------------
    def negamax(squares, color, depth, alpha, beta, root_depth):
        stats["nodes"] += 1
        check_time()

        enemy = opp_color if color == bot_color else bot_color
        if find_king(squares, enemy) is None:
            return WIN
        if find_king(squares, color) is None:
            return -WIN

        if depth <= 0:
            if USE_QUIESCENCE:
                return quiescence(squares, color, alpha, beta)
            return evaluate(squares, color)

        squares_t = tuple(squares)
        alpha_orig, beta_orig = alpha, beta

        tp = tt_probe(squares_t, color, depth, alpha, beta)
        if tp is not None:
            tscore, tmove, alpha, beta, cutoff = tp
            if cutoff:
                return tscore

        moves = generate_moves(squares, color)
        if not moves:
            return -WIN + (root_depth - depth)

        moves = order_moves(squares, moves, color, depth)

        best_move = None
        best_score = -WIN

        for m in moves:
            # Fast win if can capture king 
            if squares[m[1]][0] == 'k':
                return WIN - (root_depth - depth)

            child = make_move(squares, m)
            score = -negamax(child, opp_color if color == bot_color else bot_color, depth - 1, -beta, -alpha, root_depth)
            if score > best_score:
                best_score = score
                best_move = m
            if score > alpha:
                alpha = score
            if alpha >= beta:
                stats["ab_cutoffs"] += 1
                # killer/history updates
                if USE_KILLER_HISTORY:
                    # killer: only quiet moves
                    if squares[m[1]][0] == '.':
                        km = killer.get(depth, [])
                        if m not in km:
                            km = [m] + km[:MAX_KILLERS_PER_DEPTH - 1]
                            killer[depth] = km
                        history[(color, m[0], m[1])] = history.get((color, m[0], m[1]), 0) + depth * depth
                break

        tt_store(squares_t, color, depth, best_score, alpha_orig, beta_orig, best_move)
        return best_score

    # -------------------- MAIN --------------------
    squares0 = load_squares_from_board(board)
    root_moves = generate_moves(squares0, bot_color)
    if not root_moves:
        return None

    best_move = root_moves[0]
    best_score = -WIN

    max_depth = DEFAULT_MAX_DEPTH
    

    depth = 1
    try:
        while depth <= max_depth:
            check_time()
            moves = order_moves(squares0, root_moves, bot_color, depth)

            local_best_move = best_move
            local_best_score = -WIN

            alpha, beta = -WIN, WIN

            for m in moves:
                check_time()

                # win win win
                if squares0[m[1]][0] == 'k':
                    local_best_move = m
                    local_best_score = WIN
                    break

                child = make_move(squares0, m)
                score = -negamax(child, opp_color, depth - 1, -beta, -alpha, depth)

                if score > local_best_score:
                    local_best_score = score
                    local_best_move = m

                if score > alpha:
                    alpha = score

            best_move = local_best_move
            best_score = local_best_score
            depth += 1

    except SearchTimeout:
        pass

    si, di = best_move
    sx, sy = i_to_xy(si)
    dx, dy = i_to_xy(di)
    print(
        f"{BOT_NAME}: best depth={depth-1} score={best_score} move=({sx},{sy})->({dx},{dy}) "
        f"tt_hits={stats['tt_hits']} tt_cutoffs={stats['tt_cutoffs']} "
        f"ab_cutoffs={stats['ab_cutoffs']} nodes={stats['nodes']}"
    )
    return ((sx, sy), (dx, dy))


register_chess_bot(BOT_NAME, chess_bot)
