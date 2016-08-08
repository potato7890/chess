import pygame
import os
from chess_logic import *

os.environ['SDL_VIDEO_CENTERED'] = '1'


class Window:
    def __init__(self, x, y, caption, icon, flags):
        pygame.init()
        self.display = pygame.display.set_mode((x, y), flags)
        pygame.display.set_caption(caption)
        pygame.display.set_icon(icon)


class ChessGame(Window):
    clock = pygame.time.Clock()
    light = [(240, 250, 240),
             (250, 250, 230),
             (250, 250, 230),
             (250, 250, 250),
             (250, 250, 250)]
    dark = [(150, 210, 90),
            (230, 170, 50),
            (210, 150, 90),
            (150, 150, 150),
            (220, 220, 220)]
    selected_color = [(110, 200, 250),
                      (200, 230, 250),
                      (250, 250, 230)]
    highlighted_color = []
    squares = [(x, y) for x in range(8) for y in range(8)]
    icons_50 = {'wp': pygame.image.load('wpawn.png'),
                'wr': pygame.image.load('wrook.png'),
                'wn': pygame.image.load('wknight.png'),
                'wb': pygame.image.load('wbishop.png'),
                'wk': pygame.image.load('wking.png'),
                'wq': pygame.image.load('wqueen.png'),
                'bp': pygame.image.load('bpawn.png'),
                'br': pygame.image.load('brook.png'),
                'bn': pygame.image.load('bknight.png'),
                'bb': pygame.image.load('bbishop.png'),
                'bk': pygame.image.load('bking.png'),
                'bq': pygame.image.load('bqueen.png')}

    def __init__(self, load_game=False):
        self.abstract_board = Board()
        self.square_size = 70
        self.board_color = 4
        icon = pygame.image.load('icon.png')
        super().__init__(self.square_size * 8, self.square_size * 8, 'chess', icon, pygame.DOUBLEBUF)
        self.draw_clean_board()
        self.draw_pieces()
        self.clicked_square = ()
        self.release_square = (0, 0)
        self.mouse_button = 1
        self.mouse_being_pressed = False
        self.clicked_piece = 'wp'
        self.selected_squares = []
        self.highlighted_squares = []
        self.mode = 'default_game_board'
        self.promotion_square_from = (1, 1)
        self.promotion_square_to = (1, 1)
        self.promotion_menu_squares = []
        self.game_loop()

    def draw_clean_board(self):
        # pygame.draw.rect(self.display, (255, 255, 255), (0, 0, 5000, 5000))
        color = self.board_color
        for corner in self.squares:
            if (corner[0] + corner[1]) % 2 == 0:
                pygame.draw.rect(self.display, self.light[color],
                                 (corner[0] * self.square_size, corner[1] * self.square_size,
                                  self.square_size, self.square_size))
            else:
                pygame.draw.rect(self.display, self.dark[color],
                                 (corner[0] * self.square_size, corner[1] * self.square_size,
                                  self.square_size, self.square_size))

    @staticmethod
    def brighten(color):
        return color

    @staticmethod
    def darken(color):
        return color

    @staticmethod
    def red_shift(color):
        return color

    @staticmethod
    def blue_shift(color):
        return color

    @staticmethod
    def invert_square(square):
        return 7 - square[0], 7 - square[1]

    def highlight_square(self, corner, highlight_color=0):
        if corner:
            pygame.draw.rect(self.display, self.selected_color[highlight_color],
                             (corner[0] * self.square_size, corner[1] * self.square_size,
                              self.square_size, self.square_size))

    def find_clicked_square(self, coordinates):
        return (coordinates[0] // self.square_size), (coordinates[1] // self.square_size)

    def draw_piece(self, piece, corner=(1, 1), icon_set=1, icon_size=50, center_on_cursor=False):
        icon_sets = {1: self.icons_50}
        if not center_on_cursor:
            piece_corner = tuple([x * self.square_size + self.square_size / 2 - icon_size / 2 for x in corner])
        else:
            piece_corner = tuple([n - icon_size / 2 for n in pygame.mouse.get_pos()])
        self.display.blit(icon_sets[icon_set][piece], piece_corner)

    def draw_pieces(self, omitted_square=(-1, -1)):
        _board = self.abstract_board.game_board
        for square in _board:
            if _board[square] != ' ' and square != omitted_square:
                self.draw_piece(_board[square], square)

    def highlight_moves(self, clicked_square):
        results = []
        final_results = []
        selectable_color = self.abstract_board.get_current_turn()
        clicked_piece = self.abstract_board.game_board[clicked_square]
        if clicked_piece != ' ' and clicked_piece[0] == selectable_color:
            if self.abstract_board.current_white == self.abstract_board.current_white_turn:
                if clicked_piece[1] == 'p':
                    for square in self.abstract_board.find_pawn_moves(selectable_color, clicked_square):
                        results.append((self.clicked_square, square))
                elif clicked_piece[1] == 'r':
                    for square in self.abstract_board.find_rook_moves(selectable_color, clicked_square):
                        results.append((self.clicked_square, square))
                elif clicked_piece[1] == 'b':
                    for square in self.abstract_board.find_bishop_moves(selectable_color, clicked_square):
                        results.append((self.clicked_square, square))
                elif clicked_piece[1] == 'q':
                    for square in self.abstract_board.find_queen_moves(selectable_color, clicked_square):
                        results.append((self.clicked_square, square))
                elif clicked_piece[1] == 'k':
                    for square in self.abstract_board.find_king_moves(selectable_color, clicked_square):
                        results.append((self.clicked_square, square))
                elif clicked_piece[1] == 'n':
                    for square in self.abstract_board.find_knight_moves(selectable_color, clicked_square):
                        results.append((self.clicked_square, square))
                pre_final_results = [result for result in results if result not in self.abstract_board.invalid_moves]
                for result in pre_final_results:
                    final_results.append(result[1])
            else:
                clicked_square_inverted = (7 - clicked_square[0], 7 - clicked_square[1])
                self.abstract_board.flip_board()
                if clicked_piece[1] == 'p':
                    for square in self.abstract_board.find_pawn_moves(selectable_color, clicked_square_inverted):
                        results.append((clicked_square_inverted, square))
                elif clicked_piece[1] == 'r':
                    for square in self.abstract_board.find_rook_moves(selectable_color, clicked_square_inverted):
                        results.append((clicked_square_inverted, square))
                elif clicked_piece[1] == 'b':
                    for square in self.abstract_board.find_bishop_moves(selectable_color, clicked_square_inverted):
                        results.append((clicked_square_inverted, square))
                elif clicked_piece[1] == 'q':
                    for square in self.abstract_board.find_queen_moves(selectable_color, clicked_square_inverted):
                        results.append((clicked_square_inverted, square))
                elif clicked_piece[1] == 'k':
                    for square in self.abstract_board.find_king_moves(selectable_color, clicked_square_inverted):
                        results.append((clicked_square_inverted, square))
                elif clicked_piece[1] == 'n':
                    for square in self.abstract_board.find_knight_moves(selectable_color, clicked_square_inverted):
                        results.append((clicked_square_inverted, square))
                pre_final_results = [result for result in results if result not in self.abstract_board.invalid_moves]
                for result in pre_final_results:
                    final_results.append((7 - result[1][0], 7 - result[1][1]))
                self.abstract_board.flip_board()

        self.highlighted_squares = final_results
        self.keep_highlighting()
        return final_results

    def keep_highlighting(self):
        for square in self.highlighted_squares:
            self.highlight_square(square, 1)

    def show_promotion_menu(self):
        self.draw_clean_board()
        self.draw_pieces(omitted_square=self.clicked_square)
        if self.abstract_board.current_white == self.abstract_board.current_white_turn:
            multiplier = 1
        else:
            multiplier = -1
        self.promotion_menu_squares = [(self.release_square, 'q'),
                                       ((self.release_square[0], self.release_square[1] + 1 * multiplier), 'n'),
                                       ((self.release_square[0], self.release_square[1] + 2 * multiplier), 'r'),
                                       ((self.release_square[0], self.release_square[1] + 3 * multiplier), 'b')]
        for x in range(4):
            self.highlight_square(self.promotion_menu_squares[x][0], 2)
            self.draw_piece(''.join([self.abstract_board.get_current_turn(), self.promotion_menu_squares[x][1]]),
                            self.promotion_menu_squares[x][0])

    def promotion_menu_handler(self):
        if self.clicked_square in [option[0] for option in self.promotion_menu_squares]:
            self.abstract_board.move_piece((self.promotion_square_from, self.promotion_square_to, self.clicked_piece))
        self.highlighted_squares = []
        self.draw_clean_board()
        self.draw_pieces()
        self.mode = 'promotion_menu_exit'

    def mouse_press_handler(self, clicked_piece=None):
        if self.mode == 'default_game_board':
            if self.mouse_button == 1:
                if clicked_piece != ' ':
                    # pygame.mouse.set_visible(0)
                    self.draw_clean_board()
                    self.highlight_square(self.clicked_square)
                    self.highlight_moves(self.clicked_square)
                    self.draw_pieces(omitted_square=self.clicked_square)
                    self.draw_piece(clicked_piece, center_on_cursor=True)

                else:
                    self.draw_clean_board()
                    self.highlight_moves(self.clicked_square)
                    self.highlight_square(self.clicked_square)
                    self.draw_pieces()

    def mouse_click_handler(self):
        if self.mode == 'default_game_board':
            if self.mouse_button == 1:
                self.draw_clean_board()
                self.highlight_square(self.clicked_square)
                self.keep_highlighting()
                self.draw_pieces()
            elif self.mouse_button == 2:
                self.abstract_board.flip_board()
                self.draw_clean_board()
                self.draw_pieces()

    def drag_handler(self):
        # pygame.mouse.set_visible(0)
        if self.mode == 'default_game_board':
            self.draw_clean_board()
            self.highlight_square(self.clicked_square)
            self.keep_highlighting()
            self.draw_pieces(omitted_square=self.clicked_square)
            self.draw_piece(self.clicked_piece, center_on_cursor=True)

    def drop_handler(self):
        # pygame.mouse.set_visible(1)
        if self.abstract_board.current_white == self.abstract_board.current_white_turn:
            promotion_row = 0
        else:
            promotion_row = 7
        if self.mode == 'default_game_board':
            if self.release_square not in self.highlighted_squares:
                self.draw_clean_board()
                self.highlight_square(self.clicked_square)
                self.keep_highlighting()
                self.draw_pieces()
            else:
                if self.clicked_piece[1] == 'p' and self.release_square[1] == promotion_row:
                    self.show_promotion_menu()
                    self.promotion_square_from = self.clicked_square
                    self.promotion_square_to = self.release_square
                    self.mode = 'promotion_menu'
                else:
                    if self.abstract_board.current_white == self.abstract_board.current_white_turn:
                        self.abstract_board.move_piece((self.clicked_square, self.release_square))
                    else:
                        self.abstract_board.flip_board()
                        self.abstract_board.move_piece(
                            (self.invert_square(self.clicked_square), self.invert_square(self.release_square)))
                        self.abstract_board.flip_board()
                    self.draw_clean_board()
                    self.draw_pieces()

    def take_back(self):
        if self.abstract_board.turn > 0:
            self.abstract_board.load_from_history(self.abstract_board.turn - 1)
            self.draw_clean_board()
            self.draw_pieces()

    def take_forward(self):
        if self.abstract_board.turn + 1 < len(self.abstract_board.game_history.main_branch):
            self.abstract_board.load_from_history(self.abstract_board.turn + 1)
            self.draw_clean_board()
            self.draw_pieces()

    def game_loop(self):
        while True:
            self.clock.tick(60)
            for event in pygame.event.get():
                # print(event)
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        quit()
                    elif event.key == pygame.K_LEFT:
                        self.take_back()
                    elif event.key == pygame.K_RIGHT:
                        self.take_forward()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        self.take_back()
                    elif event.button == 5:
                        self.take_forward()
                    else:
                        if self.mode == 'default_game_board':
                            self.mouse_being_pressed = True
                            self.clicked_square = self.find_clicked_square(pygame.mouse.get_pos())
                            self.clicked_piece = self.abstract_board.game_board[self.clicked_square]
                            if event.button == 1:
                                self.mouse_button = 1
                                self.mouse_press_handler(clicked_piece=self.clicked_piece)
                            elif event.button == 3:
                                self.mouse_button = 2
                                self.mouse_click_handler()
                        elif self.mode == 'promotion_menu' and pygame.mouse.get_pressed()[0] == 1:
                            self.mouse_being_pressed = True
                            self.clicked_square = self.find_clicked_square(pygame.mouse.get_pos())
                            for option in self.promotion_menu_squares:
                                if self.clicked_square == option[0]:
                                    self.clicked_piece = ''.join([self.abstract_board.get_current_turn(), option[1]])
                            self.promotion_menu_handler()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button != 4 and event.button != 5:
                        self.mouse_being_pressed = False
                        if self.mode == 'default_game_board':
                            self.release_square = self.find_clicked_square(pygame.mouse.get_pos())
                            if self.find_clicked_square(pygame.mouse.get_pos()) == self.clicked_square \
                                    and self.mouse_button != 2:
                                self.mouse_click_handler()
                            elif self.find_clicked_square(pygame.mouse.get_pos()) != self.clicked_square \
                                    and self.mouse_button != 2:
                                self.drop_handler()
                        if self.mode == 'promotion_menu_exit':
                            self.mode = 'default_game_board'
                elif event.type == pygame.MOUSEMOTION:
                    if self.mode == 'default_game_board':
                        if self.mouse_being_pressed and self.mouse_button == 1 and self.clicked_piece != ' ':
                            self.drag_handler()

            pygame.display.update()


def run_chess():
    ChessGame().__init__()


if __name__ == '__main__':
    run_chess()
