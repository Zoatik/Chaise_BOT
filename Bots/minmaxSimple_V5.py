from Bots.ChessBotList import register_chess_bot

import time
import math


def minMaxBot(player_sequence, board, time_budget, **kwargs):
    startTime = time.time()

    our_color = player_sequence[1]
    enemy_color = "w" if our_color != "w" else "b"

    def opp(c):
        return "w" if c != "w" else "b"

    basePieceValues = {
        "p": 1.0,
        "n": 3.2,
        "b": 3.33,
        "r": 5.1,
        "q": 8.8,
        "k": 100.0,
    }

    # --- PST (as you had) ---
    position_bonus = {
        "n": {
            "start": [
                [-5, -4, -3, -3, -3, -3, -4, -5],
                [-4, -2, 0, 0.5, 0.5, 0, -2, -4],
                [-3, 0, 1, 1.5, 1.5, 1, 0, -3],
                [-3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3],
                [-3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3],
                [-3, 0, 1, 1.5, 1.5, 1, 0, -3],
                [-4, -2, 0, 0.5, 0.5, 0, -2, -4],
                [-5, -4, -3, -3, -3, -3, -4, -5],
            ],
            "end": [
                [-4, -3, -2, -2, -2, -2, -3, -4],
                [-3, -1, 0, 0.5, 0.5, 0, -1, -3],
                [-2, 0, 1.5, 2, 2, 1.5, 0, -2],
                [-2, 0.5, 2, 2.5, 2.5, 2, 0.5, -2],
                [-2, 0.5, 2, 2.5, 2.5, 2, 0.5, -2],
                [-2, 0, 1.5, 2, 2, 1.5, 0, -2],
                [-3, -1, 0, 0.5, 0.5, 0, -1, -3],
                [-4, -3, -2, -2, -2, -2, -3, -4],
            ],
        },
        "k": {
            "start": [
                [2, 3, 1, 0, 0, 1, 3, 2],
                [2, 2, -0.5, -0.5, -0.5, -0.5, 2, 2],
                [-1, -2, -2, -2, -2, -2, -2, -1],
                [-2, -3, -3, -4, -4, -3, -3, -2],
                [-3, -4, -4, -5, -5, -4, -4, -3],
                [-4, -5, -5, -6, -6, -5, -5, -4],
                [-6, -6, -6, -6, -6, -6, -6, -6],
                [-8, -7, -7, -7, -7, -7, -7, -8],
            ],
            "end": [
                [-3, -2, -1, -1, -1, -1, -2, -3],
                [-2, 0, 0.5, 0.5, 0.5, 0.5, 0, -2],
                [-1, 0.5, 1.5, 2, 2, 1.5, 0.5, -1],
                [-1, 0.5, 2, 2.5, 2.5, 2, 0.5, -1],
                [-1, 0.5, 2, 2.5, 2.5, 2, 0.5, -1],
                [-1, 0.5, 1.5, 2, 2, 1.5, 0.5, -1],
                [-2, 0, 0.5, 0.5, 0.5, 0.5, 0, -2],
                [-3, -2, -1, -1, -1, -1, -2, -3],
            ],
        },
        "p": {
            "start": [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
                [1, 1, 1.5, 2, 2, 1.5, 1, 1],
                [1.5, 1.5, 2, 2.5, 2.5, 2, 1.5, 1.5],
                [2, 2, 2.5, 3, 3, 2.5, 2, 2],
                [2.5, 2.5, 3, 3.5, 3.5, 3, 2.5, 2.5],
                [3, 3, 3, 3, 3, 3, 3, 3],
                [0, 0, 0, 0, 0, 0, 0, 0],
            ],
            "end": [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [2, 2.5, 3, 3.5, 3.5, 3, 2.5, 2],
                [3, 3.5, 4, 4.5, 4.5, 4, 3.5, 3],
                [4, 4.5, 5, 5.5, 5.5, 5, 4.5, 4],
                [5, 5.5, 6, 6.5, 6.5, 6, 5.5, 5],
                [7, 7, 7, 7, 7, 7, 7, 7],
                [0, 0, 0, 0, 0, 0, 0, 0],
            ],
        },
        "b": {
            "start": [
                [-2, -1, -1, -1, -1, -1, -1, -2],
                [-1, 0, 0.5, 0.5, 0.5, 0.5, 0, -1],
                [-1, 0.5, 1, 1.5, 1.5, 1, 0.5, -1],
                [-1, 0.5, 1.5, 2, 2, 1.5, 0.5, -1],
                [-1, 0.5, 1.5, 2, 2, 1.5, 0.5, -1],
                [-1, 0.5, 1, 1.5, 1.5, 1, 0.5, -1],
                [-1, 0, 0.5, 0.5, 0.5, 0.5, 0, -1],
                [-2, -1, -1, -1, -1, -1, -1, -2],
            ],
            "end": [
                [-1, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -1],
                [-0.5, 0, 0.5, 1, 1, 0.5, 0, -0.5],
                [-0.5, 0.5, 1.5, 2, 2, 1.5, 0.5, -0.5],
                [-0.5, 1, 2, 2.5, 2.5, 2, 1, -0.5],
                [-0.5, 1, 2, 2.5, 2.5, 2, 1, -0.5],
                [-0.5, 0.5, 1.5, 2, 2, 1.5, 0.5, -0.5],
                [-0.5, 0, 0.5, 1, 1, 0.5, 0, -0.5],
                [-1, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -1],
            ],
        },
        "r": {
            "start": [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0.5, 0.5, 1, 1, 0.5, 0.5, 0],
                [0, 1, 1.5, 2, 2, 1.5, 1, 0],
                [0, 1, 1.5, 2, 2, 1.5, 1, 0],
                [0, 1, 1.5, 2, 2, 1.5, 1, 0],
                [0, 1, 1.5, 2, 2, 1.5, 1, 0],
                [0, 1, 1, 1.5, 1.5, 1, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
            ],
            "end": [
                [0, 0.5, 0.5, 1, 1, 0.5, 0.5, 0],
                [0, 1, 1.5, 2, 2, 1.5, 1, 0],
                [0, 1.5, 2.5, 3, 3, 2.5, 1.5, 0],
                [0, 1.5, 2.5, 3, 3, 2.5, 1.5, 0],
                [0, 1.5, 2.5, 3, 3, 2.5, 1.5, 0],
                [0, 1.5, 2.5, 3, 3, 2.5, 1.5, 0],
                [0.5, 2, 2.5, 3, 3, 2.5, 2, 0.5],
                [0, 0.5, 0.5, 1, 1, 0.5, 0.5, 0],
            ],
        },
        "q": {
            "start": [
                [-2, -1, -1, -1, -1, -1, -1, -2],
                [-1, 0, 0, 0, 0, 0, 0, -1],
                [-1, 0, 0.5, 0.5, 0.5, 0.5, 0, -1],
                [-1, 0, 0.5, 1, 1, 0.5, 0, -1],
                [-1, 0, 0.5, 1, 1, 0.5, 0, -1],
                [-1, 0, 0.5, 0.5, 0.5, 0.5, 0, -1],
                [-1, 0, 0, 0, 0, 0, 0, -1],
                [-2, -1, -1, -1, -1, -1, -1, -2],
            ],
            "end": [
                [-1, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -1],
                [-0.5, 0, 0.5, 1, 1, 0.5, 0, -0.5],
                [-0.5, 0.5, 1.5, 2, 2, 1.5, 0.5, -0.5],
                [-0.5, 1, 2, 2.5, 2.5, 2, 1, -0.5],
                [-0.5, 1, 2, 2.5, 2.5, 2, 1, -0.5],
                [-0.5, 0.5, 1.5, 2, 2, 1.5, 0.5, -0.5],
                [-0.5, 0, 0.5, 1, 1, 0.5, 0, -0.5],
                [-1, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -1],
            ],
        },
    }

    # -----------------------------
    # Orientation helpers (player-relative)
    # -----------------------------
    def rotate_board_180(b):
        nb = b.copy()
        for i in range(8):
            for j in range(8):
                nb[7 - i, 7 - j] = b[i, j]
        return nb

    def time_up(margin=0.03):
        return (time.time() - startTime) >= (time_budget - margin)

    def isInBounds(i, j):
        return 0 <= i <= 7 and 0 <= j <= 7

    def pawn_dx(piece_color, perspective_color):
        # In "side-to-move" perspective, side-to-move pawns go +x, other pawns go -x
        return 1 if piece_color == perspective_color else -1

    # -----------------------------
    # Attacks / Move-gen in a given perspective_color
    # -----------------------------
    def get_piece_attacks(b, pos, pt, pc, perspective_color):
        x, y = pos
        out = []

        if pt == "p":
            dx = pawn_dx(pc, perspective_color)
            for dy in (-1, 1):
                nx, ny = x + dx, y + dy
                if isInBounds(nx, ny) and b[nx, ny] != "X":
                    out.append((nx, ny))
            return out

        if pt == "n":
            for dx, dy in (
                (2, 1), (2, -1), (-2, 1), (-2, -1),
                (1, 2), (1, -2), (-1, 2), (-1, -2),
            ):
                nx, ny = x + dx, y + dy
                if isInBounds(nx, ny) and b[nx, ny] != "X":
                    out.append((nx, ny))
            return out

        if pt == "k":
            for dx, dy in (
                (1, 0), (-1, 0), (0, 1), (0, -1),
                (1, 1), (1, -1), (-1, 1), (-1, -1),
            ):
                nx, ny = x + dx, y + dy
                if isInBounds(nx, ny) and b[nx, ny] != "X":
                    out.append((nx, ny))
            return out

        directions = []
        if pt in ("b", "q"):
            directions += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        if pt in ("r", "q"):
            directions += [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while isInBounds(nx, ny):
                if b[nx, ny] == "X":
                    break
                out.append((nx, ny))
                if b[nx, ny] != "":
                    break
                nx += dx
                ny += dy
        return out

    def getAttackedSquares(b, attacker_color, perspective_color):
        attacked = set()
        for x in range(8):
            for y in range(8):
                cell = b[x, y]
                if cell == "" or cell == "X" or cell[1] != attacker_color:
                    continue
                pt = cell[0]
                for sq in get_piece_attacks(b, (x, y), pt, attacker_color, perspective_color):
                    attacked.add(sq)
        return attacked

    def getAllMoves(b, color, perspective_color):
        moves = []

        def is_enemy(x, y):
            cell = b[x, y]
            return cell != "" and cell != "X" and cell[1] != color

        def is_empty(x, y):
            return b[x, y] == ""

        def pawn_moves(x, y):
            pm = []
            dx = pawn_dx(color, perspective_color)
            nx = x + dx
            if isInBounds(nx, y) and is_empty(nx, y):
                pm.append(((x, y), (nx, y)))
            for dy in (-1, 1):
                ny = y + dy
                if isInBounds(nx, ny) and is_enemy(nx, ny):
                    pm.append(((x, y), (nx, ny)))
            return pm

        def knight_moves(x, y):
            km = []
            for nx, ny in (
                (x + 2, y + 1), (x + 2, y - 1), (x - 2, y + 1), (x - 2, y - 1),
                (x + 1, y + 2), (x + 1, y - 2), (x - 1, y + 2), (x - 1, y - 2),
            ):
                if isInBounds(nx, ny) and (b[nx, ny] == "" or is_enemy(nx, ny)):
                    km.append(((x, y), (nx, ny)))
            return km

        def sliding_moves(x, y, dirs):
            out = []
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                while isInBounds(nx, ny):
                    if b[nx, ny] == "X":
                        break
                    if b[nx, ny] == "":
                        out.append(((x, y), (nx, ny)))
                    else:
                        if is_enemy(nx, ny):
                            out.append(((x, y), (nx, ny)))
                        break
                    nx += dx
                    ny += dy
            return out

        def rook_moves(x, y):
            return sliding_moves(x, y, [(1, 0), (-1, 0), (0, 1), (0, -1)])

        def bishop_moves(x, y):
            return sliding_moves(x, y, [(1, 1), (1, -1), (-1, 1), (-1, -1)])

        def king_moves(x, y):
            km = []
            for nx, ny in (
                (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1),
                (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1),
            ):
                if isInBounds(nx, ny) and (b[nx, ny] == "" or is_enemy(nx, ny)):
                    km.append(((x, y), (nx, ny)))
            return km

        for x in range(8):
            for y in range(8):
                cell = b[x, y]
                if cell == "" or cell == "X" or cell[1] != color:
                    continue
                pt = cell[0]
                if pt == "p":
                    moves.extend(pawn_moves(x, y))
                elif pt == "n":
                    moves.extend(knight_moves(x, y))
                elif pt == "r":
                    moves.extend(rook_moves(x, y))
                elif pt == "b":
                    moves.extend(bishop_moves(x, y))
                elif pt == "q":
                    moves.extend(rook_moves(x, y))
                    moves.extend(bishop_moves(x, y))
                elif pt == "k":
                    moves.extend(king_moves(x, y))
        return moves

    def createNewBoard(b, move, perspective_color):
        nb = b.copy()
        start, dest = move
        piece = b[start]

        if piece != "" and piece != "X" and piece[0] == "p":
            dx = pawn_dx(piece[1], perspective_color)
            if (dx == 1 and dest[0] == 7) or (dx == -1 and dest[0] == 0):
                piece = "q" + piece[1]

        nb[dest] = piece
        nb[start] = ""
        return nb

    # -----------------------------
    # SEE helpers (used for ordering AND safety gating)
    # -----------------------------
    def build_attackers_by_square(b, perspective_color):
        att = {"w": {}, "b": {}}
        for x in range(8):
            for y in range(8):
                cell = b[x, y]
                if cell == "" or cell == "X":
                    continue
                pt, pc = cell[0], cell[1]
                v = basePieceValues.get(pt, 0.0)
                for (ax, ay) in get_piece_attacks(b, (x, y), pt, pc, perspective_color):
                    if b[ax, ay] == "X":
                        continue
                    att[pc].setdefault((ax, ay), []).append(v)
        for c in ("w", "b"):
            for sq in att[c]:
                att[c][sq].sort()
        return att

    def see_exchange_static(dest, attacker_value, captured_value, color, attackers_by_square):
        opponent_color = opp(color)
        our_atts = list(attackers_by_square[color].get(dest, []))
        opp_atts = list(attackers_by_square[opponent_color].get(dest, []))

        try:
            our_atts.remove(attacker_value)
        except ValueError:
            pass

        gains = [captured_value]
        captured_on_square_value = attacker_value
        side = opponent_color

        while True:
            if side == opponent_color:
                if not opp_atts:
                    break
                next_att = opp_atts.pop(0)
                gains.append(captured_on_square_value - gains[-1])
                captured_on_square_value = next_att
                side = color
            else:
                if not our_atts:
                    break
                next_att = our_atts.pop(0)
                gains.append(captured_on_square_value - gains[-1])
                captured_on_square_value = next_att
                side = opponent_color

        for i in range(len(gains) - 2, -1, -1):
            gains[i] = max(gains[i], -gains[i + 1])
        return gains[0]

    # -----------------------------
    # Evaluation (ALWAYS from our_color perspective)
    # and SAFETY FIX: enemy-attack bonus only if SEE >= 0
    # -----------------------------
    def piece_pos_bonus(pt, pos, enemies_remaining):
        position_scale = 0.25
        if pt not in position_bonus:
            return 0.0
        max_enemies = 16
        enemies_remaining = max(0, min(max_enemies, enemies_remaining))
        t = 1.0 - (enemies_remaining / max_enemies)
        x, y = pos
        start_val = float(position_bonus[pt]["start"][x][y])
        end_val = float(position_bonus[pt]["end"][x][y])
        return (start_val + (end_val - start_val) * t) * position_scale

    def count_enemies(b, our_c):
        c = 0
        for x in range(8):
            for y in range(8):
                cell = b[x, y]
                if cell == "" or cell == "X":
                    continue
                if cell[1] != our_c:
                    c += 1
        return c

    def evaluate_board_components(board_oriented, perspective_color):
        # Rotate to our_color perspective so PST & pawn logic are consistent
        if perspective_color != our_color:
            b = rotate_board_180(board_oriented)
            eval_persp = our_color
        else:
            b = board_oriented
            eval_persp = our_color

        enemies_remaining = count_enemies(b, our_color)

        attacked_by_enemy = getAttackedSquares(b, enemy_color, eval_persp)
        attacked_by_us = getAttackedSquares(b, our_color, eval_persp)

        attackers_by_square = build_attackers_by_square(b, eval_persp)

        material_sum = 0.0
        position_sum = 0.0
        safety_sum = 0.0

        # Stronger hanging penalty; scale with value a bit
        def hanging_penalty(v):
            # queen should be VERY expensive to hang
            return 0.75 * v + 0.03 * v * v

        defended_penalty = 0.18  # attacked but defended (small)
        attacked_enemy_reward_scale = 0.55  # reward for truly "winnable" hanging enemy pieces

        max_threat_reward_total = 2.5     # CAP GLOBAL : empêche safety=60
        threat_reward_total = 0.0
        threat_reward_per_piece_cap = 1.2 # CAP PAR PIÈCE

        # 1) material + PST
        for x in range(8):
            for y in range(8):
                cell = b[x, y]
                if cell == "" or cell == "X":
                    continue
                pt, pc = cell[0], cell[1]
                v = basePieceValues.get(pt, 0.0)
                sign = 1.0 if pc == our_color else -1.0

                material_sum += sign * v
                pv = piece_pos_bonus(pt, (x, y), enemies_remaining)
                pv = max(pv, -0.3 * v)
                position_sum += sign * pv

        # 2) safety: penalize our hanging pieces hard
        for x in range(8):
            for y in range(8):
                cell = b[x, y]
                if cell == "" or cell == "X":
                    continue
                pt, pc = cell[0], cell[1]
                v = basePieceValues.get(pt, 0.0)
                sq = (x, y)

                if pc == our_color:
                    if sq in attacked_by_enemy:
                        if sq in attacked_by_us:
                            safety_sum -= defended_penalty * v
                        else:
                            safety_sum -= hanging_penalty(v)

        # 3) safety: reward enemy pieces attacked ONLY if capture is not losing (SEE >= 0)
        # This prevents "queen suicide gives huge +safety because it attacks everything".
        for x in range(8):
            for y in range(8):
                cell = b[x, y]
                if cell == "" or cell == "X":
                    continue
                pt, pc = cell[0], cell[1]
                if pc != enemy_color:
                    continue

                sq = (x, y)
                if sq not in attacked_by_us:
                    continue

                enemy_v = basePieceValues.get(pt, 0.0)

                our_atts = attackers_by_square[our_color].get(sq, [])
                if not our_atts:
                    continue

                cheapest = our_atts[0]
                see = see_exchange_static(sq, cheapest, enemy_v, our_color, attackers_by_square)
                if see < 0:
                    continue

                # bounded reward
                reward = min(threat_reward_per_piece_cap, 0.35 * enemy_v + 0.5 * min(see, enemy_v))
                threat_reward_total += reward

                if threat_reward_total >= max_threat_reward_total:
                    threat_reward_total = max_threat_reward_total
                    break
            if threat_reward_total >= max_threat_reward_total:
                break

        safety_sum += threat_reward_total

        total = material_sum + position_sum + safety_sum
        return total, {"material": material_sum, "position": position_sum, "safety": safety_sum}

    def evaluate_board(board_oriented, perspective_color):
        return evaluate_board_components(board_oriented, perspective_color)[0]

    # -----------------------------
    # Ordering
    # -----------------------------
    def get_capture_moves(b, color, perspective_color):
        caps = []
        for mv in getAllMoves(b, color, perspective_color):
            _, d = mv
            t = b[d]
            if t != "" and t != "X" and t[1] != color:
                caps.append(mv)
        return caps

    def move_gives_check(b, move, attacker_color, perspective_color):
        nb = createNewBoard(b, move, perspective_color)
        victim = opp(attacker_color)
        king_pos = None
        for x in range(8):
            for y in range(8):
                c = nb[x, y]
                if c != "" and c != "X" and c[0] == "k" and c[1] == victim:
                    king_pos = (x, y)
                    break
            if king_pos is not None:
                break
        if king_pos is None:
            return False
        return king_pos in getAttackedSquares(nb, attacker_color, perspective_color)

    def order_moves(b, moves, color, perspective_color, reverse=True):
        opponent_color = opp(color)

        attacked_before = getAttackedSquares(b, opponent_color, perspective_color)
        protected_before = getAttackedSquares(b, color, perspective_color)
        attackers_by_square = build_attackers_by_square(b, perspective_color)

        ordered = []
        for mv in moves:
            s, d = mv
            piece = b[s]
            if piece == "" or piece == "X":
                continue
            pv = basePieceValues.get(piece[0], 0.0)

            target = b[d]
            is_cap = (target != "" and target != "X" and target[1] != color)

            score = 0.0

            if is_cap:
                cv = basePieceValues.get(target[0], 0.0)
                score += see_exchange_static(d, pv, cv, color, attackers_by_square)

            # checks: only a bonus if the checking piece is not hanging after the move
            gives_check = move_gives_check(b, mv, color, perspective_color)

            # post-move safety check (cheap and very effective)
            risky = is_cap or (d in attacked_before)
            if risky and not time_up(margin=0.06):
                nb = createNewBoard(b, mv, perspective_color)

                # --- INSERT: "real capturability" blunder check via move-gen ---
                # This catches cases where attacked-squares are inconsistent with actual legal captures.
                opp_caps = get_capture_moves(nb, opponent_color, perspective_color)
                if any(od == d for (_, od) in opp_caps):
                    # Very strong penalty: piece can be taken immediately.
                    score -= pv * 1.6
                    if gives_check:
                        score -= pv * 0.6
                # --- END INSERT ---

                attacked_after = getAttackedSquares(nb, opponent_color, perspective_color)
                protected_after = getAttackedSquares(nb, color, perspective_color)
                if d in attacked_after and d not in protected_after:
                    score -= pv * 1.10  # stronger: don't hang pieces
                    # and if it's a "check sacrifice", don't get baited
                    if gives_check:
                        score -= pv * 0.40
                elif d in attacked_after:
                    score -= pv * 0.25

            if gives_check:
                score += 22.0  # reduced (was too magnetic)

            # pre-move heuristics
            if d in attacked_before:
                score -= pv * 0.25
            if (s in attacked_before) and (s not in protected_before) and ((d not in attacked_before) or (d in protected_before)):
                score += pv * 0.20

            ordered.append((score, mv))

        ordered.sort(key=lambda t: t[0], reverse=reverse)
        return [m for _, m in ordered]


    # -----------------------------
    # Side-to-move rotation per ply
    # -----------------------------
    def next_state_after_move(b, stm_color, mv):
        nb = createNewBoard(b, mv, perspective_color=stm_color)
        return rotate_board_180(nb), opp(stm_color)

    # -----------------------------
    # Quiescence / AlphaBeta
    # -----------------------------
    def quiescence(b, stm_color, alpha, beta):
        if time_up(margin=0.03):
            raise TimeoutError("time budget exceeded")

        stand_pat = evaluate_board(b, perspective_color=stm_color)
        maximizing = (stm_color == our_color)

        if maximizing:
            if stand_pat >= beta:
                return stand_pat
            alpha = max(alpha, stand_pat)

            moves = get_capture_moves(b, stm_color, stm_color)
            moves = order_moves(b, moves, stm_color, stm_color, reverse=True)
            for mv in moves:
                if time_up(margin=0.03):
                    raise TimeoutError("time budget exceeded")
                nb2, next_stm = next_state_after_move(b, stm_color, mv)
                score = quiescence(nb2, next_stm, alpha, beta)
                alpha = max(alpha, score)
                if alpha >= beta:
                    break
            return alpha
        else:
            if stand_pat <= alpha:
                return stand_pat
            beta = min(beta, stand_pat)

            moves = get_capture_moves(b, stm_color, stm_color)
            moves = order_moves(b, moves, stm_color, stm_color, reverse=False)
            for mv in moves:
                if time_up(margin=0.03):
                    raise TimeoutError("time budget exceeded")
                nb2, next_stm = next_state_after_move(b, stm_color, mv)
                score = quiescence(nb2, next_stm, alpha, beta)
                beta = min(beta, score)
                if alpha >= beta:
                    break
            return beta

    def alpha_beta(b, stm_color, depth, alpha, beta):
        if depth == 0:
            return quiescence(b, stm_color, alpha, beta)

        if time_up(margin=0.03):
            raise TimeoutError("time budget exceeded")

        maximizing = (stm_color == our_color)

        moves = getAllMoves(b, stm_color, stm_color)
        moves = order_moves(b, moves, stm_color, stm_color, reverse=maximizing)

        if maximizing:
            value = -math.inf
            for mv in moves:
                if time_up(margin=0.03):
                    raise TimeoutError("time budget exceeded")
                nb2, next_stm = next_state_after_move(b, stm_color, mv)
                value = max(value, alpha_beta(nb2, next_stm, depth - 1, alpha, beta))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = math.inf
            for mv in moves:
                if time_up(margin=0.03):
                    raise TimeoutError("time budget exceeded")
                nb2, next_stm = next_state_after_move(b, stm_color, mv)
                value = min(value, alpha_beta(nb2, next_stm, depth - 1, alpha, beta))
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value

    # -----------------------------
    # Root iterative deepening
    # -----------------------------
    bestPossibleScore = -math.inf
    bestPossibleMove = [(0, 0), (0, 0)]

    maxDepth = 6
    depth = 1
    aspiration = 2.0

    root_board = board
    root_stm = our_color

    while depth <= maxDepth:
        if time_up(margin=0.06):
            break

        bestScoreThisDepth = -math.inf
        bestMoveThisDepth = bestPossibleMove

        rootMoves = getAllMoves(root_board, root_stm, root_stm)
        rootMoves = order_moves(root_board, rootMoves, root_stm, root_stm, reverse=True)

        a0 = bestPossibleScore - aspiration if bestPossibleScore != -math.inf else -math.inf
        b0 = bestPossibleScore + aspiration if bestPossibleScore != -math.inf else math.inf
        window_failed = False

        for mv in rootMoves:
            if time_up(margin=0.06):
                break

            nb2, next_stm = next_state_after_move(root_board, root_stm, mv)

            try:
                score = alpha_beta(nb2, next_stm, depth - 1, a0, b0)
            except TimeoutError:
                break

            if score <= a0 or score >= b0:
                window_failed = True
                try:
                    score = alpha_beta(nb2, next_stm, depth - 1, -math.inf, math.inf)
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
    final_board = createNewBoard(root_board, (bestPossibleMove[0], bestPossibleMove[1]), perspective_color=our_color)
    final_score, score_details = evaluate_board_components(final_board, perspective_color=our_color)

    print(
        "Final move for this board:",
        bestPossibleMove[0], "to ->", bestPossibleMove[1],
        ", with a score of", bestPossibleScore,
        ". This took:", time.time() - startTime, "seconds!"
    )
    print("Score details:", score_details, "total:", final_score)

    return bestPossibleMove[0], bestPossibleMove[1]


register_chess_bot("MinMax_V5_FIXED_PLAYERREL_SEESafety", minMaxBot)
