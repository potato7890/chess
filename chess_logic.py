import copy


class Board:
    def __init__(self):
        self.turn = 0
        self.game_board = {}
        self.current_white = True
        self.current_white_turn = True

        self.fifty_moves = 0
        self.en_passant_lane_for_opponent = False

        self.white_king_side_castle_right = True
        self.white_queen_side_castle_right = True
        self.black_king_side_castle_right = True
        self.black_queen_side_castle_right = True
        self.queen_side_castling = False
        self.king_side_castling = False

        self.all_moves = []
        self.all_opponent_attacks = []
        self.invalid_moves = []
        self.valid_moves = []
        self.game_state = 'match_in_progress'

        self.game_history = GameHistory()
        self.previous_move = False

        self.set_board()

    def get_current_color(self):
        if self.current_white:
            return 'w'
        else:
            return 'b'

    def get_current_turn(self):
        if self.current_white_turn:
            return 'w'
        else:
            return 'b'

    def set_board(self):
        self.game_board = {
            (0, 0): 'br', (0, 1): 'bp', (0, 2): ' ', (0, 3): ' ', (0, 4): ' ', (0, 5): ' ', (0, 6): 'wp', (0, 7): 'wr',
            (1, 0): 'bn', (1, 1): 'bp', (1, 2): ' ', (1, 3): ' ', (1, 4): ' ', (1, 5): ' ', (1, 6): 'wp', (1, 7): 'wn',
            (2, 0): 'bb', (2, 1): 'bp', (2, 2): ' ', (2, 3): ' ', (2, 4): ' ', (2, 5): ' ', (2, 6): 'wp', (2, 7): 'wb',
            (3, 0): 'bq', (3, 1): 'bp', (3, 2): ' ', (3, 3): ' ', (3, 4): ' ', (3, 5): ' ', (3, 6): 'wp', (3, 7): 'wq',
            (4, 0): 'bk', (4, 1): 'bp', (4, 2): ' ', (4, 3): ' ', (4, 4): ' ', (4, 5): ' ', (4, 6): 'wp', (4, 7): 'wk',
            (5, 0): 'bb', (5, 1): 'bp', (5, 2): ' ', (5, 3): ' ', (5, 4): ' ', (5, 5): ' ', (5, 6): 'wp', (5, 7): 'wb',
            (6, 0): 'bn', (6, 1): 'bp', (6, 2): ' ', (6, 3): ' ', (6, 4): ' ', (6, 5): ' ', (6, 6): 'wp', (6, 7): 'wn',
            (7, 0): 'br', (7, 1): 'bp', (7, 2): ' ', (7, 3): ' ', (7, 4): ' ', (7, 5): ' ', (7, 6): 'wp', (7, 7): 'wr'}
        self.en_passant_lane_for_opponent = False

        self.white_king_side_castle_right = True
        self.white_queen_side_castle_right = True
        self.black_king_side_castle_right = True
        self.black_queen_side_castle_right = True
        self.queen_side_castling = False
        self.king_side_castling = False

        self.all_moves = []
        self.all_opponent_attacks = []
        self.invalid_moves = []
        self.valid_moves = []
        self.game_state = 'match_in_progress'

        self.previous_move = False

        self.update_all_moves()  # important
        self.store_to_history()

    def flip_board(self):
        _flip_board = {}
        for square in self.game_board:
            _flip_board[(7 - square[0], 7 - square[1])] = self.game_board[square]
        self.game_board = _flip_board
        self.current_white = not self.current_white

    def move_piece(self, path, advance_turn=True, calculation=False):
        piece = self.game_board[path[0]]
        destination = self.game_board[path[1]]
        if advance_turn:
            if destination == ' ' and piece[1] != 'p':
                self.fifty_moves += 1
            else:
                self.fifty_moves = 0
            self.en_passant_lane_for_opponent = False
            if piece[1] == 'p' and path[0][1] - path[1][1] == 2:
                self.en_passant_lane_for_opponent = 7 - path[0][0]
            elif piece[1] == 'k':
                if self.current_white:
                    self.white_king_side_castle_right = False
                    self.white_queen_side_castle_right = False
                else:
                    self.black_king_side_castle_right = False
                    self.black_queen_side_castle_right = False
                if abs(path[0][0] - path[1][0]) == 2:
                    if path[0][0] < path[1][0]:
                        self.game_board[(7, 7)] = ' '
                        self.game_board[(path[1][0] - 1, 7)] = ''.join([self.get_current_color(), 'r'])
                    elif path[0][0] > path[1][0]:
                        self.game_board[(0, 7)] = ' '
                        self.game_board[(path[1][0] + 1, 7)] = ''.join([self.get_current_color(), 'r'])
            elif path[0] in [(0, 7), (7, 7)] or path[1] in [(0, 7), (7, 7)]:
                if self.current_white:
                    if path[0] == (0, 7) or path[1] == (0, 7):
                        self.white_queen_side_castle_right = False
                    else:
                        self.white_king_side_castle_right = False
                else:
                    if path[0] == (7, 7) or path[1] == (7, 7):
                        self.black_queen_side_castle_right = False
                    else:
                        self.black_king_side_castle_right = False
        if piece[1] == 'p' and path[0][0] != path[1][0] and destination == ' ':
            self.game_board[(path[1][0], 3)] = ' '
        self.game_board[path[0]] = ' '
        self.game_board[path[1]] = piece
        if len(path) == 3:
            self.game_board[path[1]] = path[2]
        if advance_turn:
            self.advance_turn(calculation)
            self.previous_move = path

    def advance_turn(self, calculation):
        # updates flags, precise order required:
        # store_to_history before determine_game_state, update_all_moves after determine_game_state
        self.current_white_turn = not self.current_white_turn
        self.turn += 1
        if self.current_white == self.current_white_turn:
            self.get_opponent_attacked_squares()
            self.find_invalid_moves()
            self.update_castle_rights()
            self.store_to_history(calculation=calculation)
            self.determine_game_state(calculation=calculation)
            self.game_history.main_branch[-1].game_state = self.game_state
            self.update_all_moves()
            self.game_history.main_branch[-1].all_moves = self.all_moves
            self.game_history.main_branch[-1].valid_moves = self.valid_moves
        else:
            self.flip_board()
            self.get_opponent_attacked_squares()
            self.find_invalid_moves()
            self.update_castle_rights()
            self.store_to_history(calculation=calculation)
            self.determine_game_state(calculation=calculation)
            self.game_history.main_branch[-1].game_state = self.game_state
            self.update_all_moves()
            self.game_history.main_branch[-1].all_moves = self.all_moves
            self.game_history.main_branch[-1].valid_moves = self.valid_moves
            self.flip_board()

    def store_to_history(self, calculation=False):
        entry = Entry(self.turn, self.game_board, self.current_white_turn, self.fifty_moves,
                      self.en_passant_lane_for_opponent,
                      self.white_king_side_castle_right, self.white_queen_side_castle_right,
                      self.black_king_side_castle_right, self.black_queen_side_castle_right, self.queen_side_castling,
                      self.king_side_castling, self.all_moves, self.all_opponent_attacks, self.invalid_moves,
                      self.valid_moves, self.game_state, self.previous_move)
        if not calculation:
            del self.game_history.main_branch[self.turn:]
            self.game_history.main_branch.append(entry)
        else:
            self.game_history.calculation_branch.append(entry)

    def load_from_history(self, turn=-1, calculation=False):
        if not calculation:
            self.turn = turn
            entry = self.game_history.main_branch[turn]
        else:
            entry = self.game_history.calculation_branch[-1]

        self.turn = entry.turn
        self.game_board = entry.game_board.copy()
        self.current_white_turn = entry.current_white_turn
        self.fifty_moves = entry.fifty_moves
        self.en_passant_lane_for_opponent = entry.en_passant_lane_for_opponent
        self.white_king_side_castle_right = entry.white_king_side_castle_right
        self.white_queen_side_castle_right = entry.white_queen_side_castle_right
        self.black_king_side_castle_right = entry.black_king_side_castle_right
        self.black_queen_side_castle_right = entry.black_queen_side_castle_right
        self.queen_side_castling = entry.queen_side_castling
        self.king_side_castling = entry.king_side_castling
        self.all_moves = list(entry.all_moves)
        self.all_opponent_attacks = list(entry.all_opponent_attacks)
        self.invalid_moves = list(entry.invalid_moves)
        self.valid_moves = list(entry.valid_moves)
        self.game_state = entry.game_state
        self.previous_move = entry.previous_move

        # sets game_board perspective to match current perspective
        if self.current_white != entry.current_white_turn and not calculation:
            self.current_white = entry.current_white_turn
            self.flip_board()
        # sets current perspective flag to game_board perspective
        elif self.current_white != entry.current_white_turn and calculation:
            self.current_white = entry.current_white_turn

    @staticmethod
    def check_boundary(square):
        if -1 < square[0] < 8 and -1 < square[1] < 8:
            return True
        else:
            return False

    @staticmethod
    def move_north(position, distance):
        return position[0], position[1] - distance

    @staticmethod
    def move_east(position, distance):
        return position[0] + distance, position[1]

    @staticmethod
    def move_south(position, distance):
        return position[0], position[1] + distance

    @staticmethod
    def move_west(position, distance):
        return position[0] - distance, position[1]

    @staticmethod
    def move_northeast(position, distance):
        return position[0] + distance, position[1] - distance

    @staticmethod
    def move_northwest(position, distance):
        return position[0] - distance, position[1] - distance

    @staticmethod
    def move_southeast(position, distance):
        return position[0] + distance, position[1] + distance

    @staticmethod
    def move_southwest(position, distance):
        return position[0] - distance, position[1] + distance

    def find_pawn_moves(self, color, position, omit_pawn_forward=False):
        results = []
        capture_squares = [(position[0] - 1, position[1] - 1), (position[0] + 1, position[1] - 1)]
        move_squares = [(position[0], position[1] - 1)]
        if position[1] == 6 and not omit_pawn_forward:
            move_squares.append((position[0], position[1] - 2))
        if omit_pawn_forward:
            move_squares = []
        for square in capture_squares:
            if self.check_boundary(square) and self.game_board[square][0] != color \
                    and self.game_board[square] != ' ':
                results.append(square)
        if self.check_boundary(move_squares[0]) and self.game_board[move_squares[0]] == ' ':
            results.append(move_squares[0])
            if len(move_squares) == 2:
                if self.check_boundary(move_squares[1]) and self.game_board[move_squares[1]] == ' ':
                    results.append(move_squares[1])
        if abs(self.en_passant_lane_for_opponent - position[0]) == 1 and position[1] == 3:
            results.append((self.en_passant_lane_for_opponent, 2))
        return results

    def directional_search(self, color, position, direction_function, maximum_distance=7):
        distance = 1
        results = []
        while True:
            square = direction_function(position, distance)
            if self.check_boundary(square) and self.game_board[square][0] != color:
                results.append(square)
                if self.game_board[square][0] != ' ':
                    break
                if distance == maximum_distance:
                    break
                distance += 1
            else:
                break
        return results

    def find_rook_moves(self, color, position):
        results = []
        directions = [self.move_north, self.move_east, self.move_south, self.move_west]
        for direction in directions:
            for result in self.directional_search(color, position, direction):
                results.append(result)
        return results

    def find_knight_moves(self, color, position):
        results = []
        moves = [(position[0] + 1, position[1] + 2), (position[0] + 2, position[1] + 1),
                 (position[0] + 1, position[1] - 2), (position[0] + 2, position[1] - 1),
                 (position[0] - 1, position[1] + 2), (position[0] - 2, position[1] + 1),
                 (position[0] - 1, position[1] - 2), (position[0] - 2, position[1] - 1)]
        for move in moves:
            if self.check_boundary(move):
                if self.game_board[move][0] != color:
                    results.append(move)
        return results

    def find_bishop_moves(self, color, position):
        results = []
        directions = [self.move_northeast, self.move_northwest, self.move_southeast, self.move_southwest]
        for direction in directions:
            for result in self.directional_search(color, position, direction):
                results.append(result)
        return results

    def find_king_moves(self, color, position, omit_castle=False):
        results = []
        directions = [self.move_north, self.move_east, self.move_south, self.move_west,
                      self.move_northeast, self.move_northwest, self.move_southeast, self.move_southwest]
        for direction in directions:
            for result in self.directional_search(color, position, direction, 1):
                results.append(result)
        if not omit_castle:
            if (self.current_white_turn and (
                        self.white_king_side_castle_right or self.white_queen_side_castle_right)) or (
                        not self.current_white_turn and (
                                self.black_king_side_castle_right or self.black_queen_side_castle_right)):
                if self.current_white_turn:
                    if self.queen_side_castling:
                        results.append((2, 7))
                    if self.king_side_castling:
                        results.append((6, 7))
                else:
                    if self.queen_side_castling:
                        results.append((5, 7))
                    if self.king_side_castling:
                        results.append((1, 7))
        return results

    def find_queen_moves(self, color, position):
        results = []
        for result in self.find_bishop_moves(color, position):
            results.append(result)
        for result in self.find_rook_moves(color, position):
            results.append(result)
        return results

    def king_is_attacked(self):
        king_position = ()
        for key in self.game_board:
            if self.game_board[key][0] == self.get_current_turn():
                if self.game_board[key][1] == 'k':
                    king_position = key
        if king_position in self.all_opponent_attacks:
            return True
        else:
            return False

    def find_invalid_moves(self):
        # creates list of invalid moves from board perspective
        results = []
        saved_board = self.game_board.copy()
        for move in self.find_all_moves(omit_castle=True):
            self.move_piece(move, advance_turn=False)
            self.get_opponent_attacked_squares()
            if self.king_is_attacked():
                results.append(move)
            self.game_board = saved_board.copy()
        self.invalid_moves = results

    def find_all_moves(self, omit_castle=False):
        # creates list of all possible moves from board perspective
        color = self.get_current_color()
        results = []
        for position in self.game_board:
            if self.game_board[position][0] == color:
                if self.game_board[position][1] == 'p':
                    for move in self.find_pawn_moves(color, position, omit_pawn_forward=False):
                        if move[1] == 0:
                            results.append((position, move, ''.join([self.get_current_turn(), 'q'])))
                            results.append((position, move, ''.join([self.get_current_turn(), 'n'])))
                            results.append((position, move, ''.join([self.get_current_turn(), 'r'])))
                            results.append((position, move, ''.join([self.get_current_turn(), 'b'])))
                        else:
                            results.append((position, move))
                elif self.game_board[position][1] == 'r':
                    for move in self.find_rook_moves(color, position):
                        results.append((position, move))
                elif self.game_board[position][1] == 'n':
                    for move in self.find_knight_moves(color, position):
                        results.append((position, move))
                elif self.game_board[position][1] == 'b':
                    for move in self.find_bishop_moves(color, position):
                        results.append((position, move))
                elif self.game_board[position][1] == 'q':
                    for move in self.find_queen_moves(color, position):
                        results.append((position, move))
                elif self.game_board[position][1] == 'k':
                    for move in self.find_king_moves(color, position, omit_castle):
                        results.append((position, move))
        return results

    def update_all_moves(self):
        # creates list of all possible moves minus all invalid moves from board perspective
        if self.game_state in ['check', 'match_in_progress']:
            self.all_moves = self.find_all_moves()
            self.valid_moves = [move for move in self.all_moves if move not in self.invalid_moves]
        else:
            self.all_moves = []
            self.valid_moves = []

    def get_opponent_attacked_squares(self):
        self.all_opponent_attacks = []
        results = []
        self.flip_board()
        for path in self.find_all_moves(omit_castle=True):
            results.append(path[1])
        self.flip_board()
        for move in results:
            self.all_opponent_attacks.append((7 - move[0], 7 - move[1]))

    def update_castle_rights(self):
        checks = 0
        self.queen_side_castling = False
        self.king_side_castling = False
        queen_side_right = False
        king_side_right = False
        if self.current_white_turn:
            queen_side = [(3, 7), (2, 7), (1, 7)]
            king_side = [(5, 7), (6, 7)]
            king = (4, 7)
            if self.white_queen_side_castle_right:
                queen_side_right = True
            if self.white_king_side_castle_right:
                king_side_right = True
        else:
            queen_side = [(4, 7), (5, 7), (6, 7)]
            king_side = [(1, 7), (2, 7)]
            king = (3, 7)
            if self.black_queen_side_castle_right:
                queen_side_right = True
            if self.black_king_side_castle_right:
                king_side_right = True
        if queen_side_right or king_side_right:
            if king not in self.all_opponent_attacks:
                if queen_side_right:
                    for square in queen_side:
                        if square not in self.all_opponent_attacks and self.game_board[square] == ' ':
                            checks += 1
                    if checks == 3:
                        self.queen_side_castling = True
                    else:
                        self.queen_side_castling = False
                if king_side_right:
                    checks = 0
                    for square in king_side:
                        if square not in self.all_opponent_attacks and self.game_board[square] == ' ':
                            checks += 1
                    if checks == 2:
                        self.king_side_castling = True
                    else:
                        self.king_side_castling = False
            else:
                self.queen_side_castling = False
                self.king_side_castling = False

    def determine_game_state(self, calculation):
        pieces_on_board = [piece for piece in self.game_board.values() if piece != ' ']
        pieces_on_board_reduced = [piece for piece in [piece[1] for piece in pieces_on_board] if
                                   piece not in ['k', 'b', 'n']]
        if self.game_history.three_fold_repetition(calculation):
            self.game_state = 'draw_three_fold_repetition'
        elif self.fifty_moves >= 50:
            self.game_state = 'draw_fifty_moves_rule'
        elif not pieces_on_board_reduced:
            # add conditional for same colored bishop
            # white_pieces = [piece[1] for piece in pieces_on_board if piece[0] == 'w']
            # black_pieces = [piece[1] for piece in pieces_on_board if piece[0] == 'b']
            if len(pieces_on_board) <= 3:
                self.game_state = 'draw_insufficient_material'
            else:
                self.game_state = 'match_in_progress'
        elif self.king_is_attacked():
            if not self.valid_moves:
                self.game_state = 'check_mate'
            else:
                self.game_state = 'check'
        elif not self.valid_moves:
            self.game_state = 'draw_stalemate'
        else:
            self.game_state = 'match_in_progress'

    def evaluate_position(self):
        result = 0
        piece_values = {' ': 0,
                        'wp': 1.4, 'bp': -1.4,
                        'wn': 3.0, 'bn': -3.0,
                        'wb': 3.5, 'bb': -3.5,
                        'wr': 5.0, 'br': -5.0,
                        'wq': 9.0, 'bq': -9.0,
                        'wk': 0, 'bk': 0}
        for piece in self.game_board.values():
            result += piece_values[piece]
        if self.current_white:
            result += len(self.valid_moves) * 0.01
            result -= len(self.all_opponent_attacks) * 0.01
        else:
            result -= len(self.valid_moves) * 0.01
            result += len(self.all_opponent_attacks) * 0.01
        return result

    def find_best_move(self, maximum_depth=2):
        depth = 0
        if self.current_white_turn != self.current_white:
            self.flip_board()

        def minimax():
            nonlocal maximum_depth
            nonlocal depth
            if depth < maximum_depth:
                depth += 1
                results = []
                if self.game_state[:4] == 'draw':
                    results.append(0)
                elif self.game_state == 'check_mate':
                    if not self.current_white_turn:
                        results.append(100)
                    else:
                        results.append(-100)
                else:
                    for move in self.valid_moves:
                        self.move_piece(move, calculation=True)  # store
                        self.flip_board()
                        results.append(minimax())
                        del self.game_history.calculation_branch[-1]  # load
                        self.load_from_history(calculation=True)  # load
                depth -= 1
                if self.current_white_turn:
                    return max(results)
                else:
                    return min(results)
            else:
                if self.game_state[:4] == 'draw':
                    return 0
                elif self.game_state == 'check_mate':
                    if not self.current_white_turn:
                        return 100
                    else:
                        return -100
                else:
                    return self.evaluate_position()

        first_level_results = []
        n = len(self.valid_moves)
        m = 0
        self.store_to_history(calculation=True)  # store
        for first_level_move in self.valid_moves:
            m += 1
            print('turn: ' + str(self.turn) + ' considering move: ' + str(m) + ' of ' + str(n))
            self.move_piece(first_level_move, calculation=True)  # store
            self.flip_board()
            first_level_results.append(minimax())
            del self.game_history.calculation_branch[-1]  # load
            self.load_from_history(calculation=True)  # load

        if len(first_level_results) > 0:
            if self.current_white_turn:
                return self.valid_moves[first_level_results.index(max(first_level_results))]
            else:
                return self.valid_moves[first_level_results.index(min(first_level_results))]
        else:
            return 0


class GameHistory:
    def __init__(self):
        self.main_branch = []
        self.calculation_branch = []

    def three_fold_repetition(self, calculation):
        if calculation:
            branch = self.main_branch + self.calculation_branch
        else:
            branch = self.main_branch
        relevant_list = [(condition.game_board, condition.current_white_turn) for condition in branch]
        for condition in relevant_list:
            if relevant_list.count(condition) >= 3:
                return True


class Entry:
    def __init__(self, turn, game_board, current_white_turn, fifty_moves, en_passant_lane_for_opponent,
                 white_king_side_castle_right, white_queen_side_castle_right, black_king_side_castle_right,
                 black_queen_side_castle_right, queen_side_castling, king_side_castling, all_moves,
                 all_opponent_attacks, invalid_moves, valid_moves, game_state, previous_move):
        self.turn = turn
        self.game_board = game_board.copy()
        self.current_white_turn = current_white_turn
        self.fifty_moves = fifty_moves
        self.en_passant_lane_for_opponent = en_passant_lane_for_opponent
        self.white_king_side_castle_right = white_king_side_castle_right
        self.white_queen_side_castle_right = white_queen_side_castle_right
        self.black_king_side_castle_right = black_king_side_castle_right
        self.black_queen_side_castle_right = black_queen_side_castle_right
        self.queen_side_castling = queen_side_castling
        self.king_side_castling = king_side_castling
        self.all_moves = list(all_moves)
        self.all_opponent_attacks = list(all_opponent_attacks)
        self.invalid_moves = list(invalid_moves)
        self.valid_moves = list(valid_moves)
        self.game_state = game_state
        self.previous_move = previous_move
