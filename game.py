import random
import turtle

from scoreboard import ScoreBoard


BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_SIZE = 30
SCREEN_WIDTH = 760
SCREEN_HEIGHT = 760
BOARD_LEFT = -(BOARD_WIDTH * CELL_SIZE) // 2
BOARD_BOTTOM = -(BOARD_HEIGHT * CELL_SIZE) // 2
BOARD_RIGHT = BOARD_LEFT + BOARD_WIDTH * CELL_SIZE
BOARD_TOP = BOARD_BOTTOM + BOARD_HEIGHT * CELL_SIZE
START_X = 3
START_Y = BOARD_HEIGHT - 4
INITIAL_DROP_MS = 500
MIN_DROP_MS = 80
DROP_STEP_MS = 40
PREVIEW_CELL = 18


SHAPES = {
    "I": {
        "color": "#00d9ff",
        "states": [
            [(0, 1), (1, 1), (2, 1), (3, 1)],
            [(2, 0), (2, 1), (2, 2), (2, 3)],
            [(0, 2), (1, 2), (2, 2), (3, 2)],
            [(1, 0), (1, 1), (1, 2), (1, 3)],
        ],
    },
    "O": {
        "color": "#ffd84d",
        "states": [
            [(1, 0), (2, 0), (1, 1), (2, 1)],
            [(1, 0), (2, 0), (1, 1), (2, 1)],
            [(1, 0), (2, 0), (1, 1), (2, 1)],
            [(1, 0), (2, 0), (1, 1), (2, 1)],
        ],
    },
    "T": {
        "color": "#b56cff",
        "states": [
            [(1, 0), (0, 1), (1, 1), (2, 1)],
            [(1, 0), (1, 1), (2, 1), (1, 2)],
            [(0, 1), (1, 1), (2, 1), (1, 2)],
            [(1, 0), (0, 1), (1, 1), (1, 2)],
        ],
    },
    "S": {
        "color": "#6bf06b",
        "states": [
            [(1, 0), (2, 0), (0, 1), (1, 1)],
            [(1, 0), (1, 1), (2, 1), (2, 2)],
            [(1, 1), (2, 1), (0, 2), (1, 2)],
            [(0, 0), (0, 1), (1, 1), (1, 2)],
        ],
    },
    "Z": {
        "color": "#ff667a",
        "states": [
            [(0, 0), (1, 0), (1, 1), (2, 1)],
            [(2, 0), (1, 1), (2, 1), (1, 2)],
            [(0, 1), (1, 1), (1, 2), (2, 2)],
            [(1, 0), (0, 1), (1, 1), (0, 2)],
        ],
    },
    "J": {
        "color": "#5d8dff",
        "states": [
            [(0, 0), (0, 1), (1, 1), (2, 1)],
            [(1, 0), (2, 0), (1, 1), (1, 2)],
            [(0, 1), (1, 1), (2, 1), (2, 2)],
            [(1, 0), (1, 1), (0, 2), (1, 2)],
        ],
    },
    "L": {
        "color": "#ff9f43",
        "states": [
            [(2, 0), (0, 1), (1, 1), (2, 1)],
            [(1, 0), (1, 1), (1, 2), (2, 2)],
            [(0, 1), (1, 1), (2, 1), (0, 2)],
            [(0, 0), (1, 0), (1, 1), (1, 2)],
        ],
    },
}


class Piece:
    def __init__(self, name):
        self.name = name
        self.color = SHAPES[name]["color"]
        self.states = SHAPES[name]["states"]
        self.x = START_X
        self.y = START_Y
        self.rotation = 0

    def cells(self, x=None, y=None, rotation=None):
        px = self.x if x is None else x
        py = self.y if y is None else y
        state = self.rotation if rotation is None else rotation
        return [(px + dx, py + dy) for dx, dy in self.states[state % 4]]


class Game:
    def __init__(self):
        self.screen = turtle.Screen()
        self.screen.title("Tetris")
        self.screen.bgcolor("#0f1115")
        self.screen.setup(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.screen.tracer(0)

        self.board = self._empty_board()
        self.score = 0
        self.lines = 0
        self.level = 1
        self.drop_delay = INITIAL_DROP_MS
        self.game_over = False

        self.board_drawer = turtle.Turtle()
        self.board_drawer.hideturtle()
        self.board_drawer.penup()
        self.board_drawer.shape("square")
        self.board_drawer.shapesize(CELL_SIZE / 20, CELL_SIZE / 20)

        self.preview_drawer = turtle.Turtle()
        self.preview_drawer.hideturtle()
        self.preview_drawer.penup()
        self.preview_drawer.shape("square")
        self.preview_drawer.shapesize(PREVIEW_CELL / 20, PREVIEW_CELL / 20)

        self.frame_drawer = turtle.Turtle()
        self.frame_drawer.hideturtle()
        self.frame_drawer.penup()
        self.frame_drawer.color("#2a2f3a")
        self.frame_drawer.pensize(3)

        self.hud = ScoreBoard()

        self.next_piece = self._new_piece()
        self.current_piece = None
        self.spawn_piece()

        self._draw_frame()
        self.screen.listen()
        self.screen.onkeypress(self.move_left, "Left")
        self.screen.onkeypress(self.move_right, "Right")
        self.screen.onkeypress(self.soft_drop, "Down")
        self.screen.onkeypress(self.rotate_piece, "Up")
        self.screen.onkeypress(self.rotate_piece, "x")
        self.screen.onkeypress(self.rotate_piece, "X")
        self.screen.onkeypress(self.hard_drop, "space")
        self.screen.onkeypress(self.reset, "r")
        self.screen.onkeypress(self.reset, "R")

    def _empty_board(self):
        return [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

    def _new_piece(self):
        return Piece(random.choice(list(SHAPES.keys())))

    def _draw_frame(self):
        self.frame_drawer.clear()
        self._draw_rectangle(self.frame_drawer, BOARD_LEFT, BOARD_BOTTOM, BOARD_WIDTH * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE)
        self._draw_rectangle(self.frame_drawer, 180, 20, 105, 100)

    def _draw_rectangle(self, pen, x, y, width, height):
        pen.goto(x, y)
        pen.pendown()
        for _ in range(2):
            pen.forward(width)
            pen.left(90)
            pen.forward(height)
            pen.left(90)
        pen.penup()

    def _is_valid(self, piece, x=None, y=None, rotation=None):
        for cell_x, cell_y in piece.cells(x=x, y=y, rotation=rotation):
            if cell_x < 0 or cell_x >= BOARD_WIDTH:
                return False
            if cell_y < 0 or cell_y >= BOARD_HEIGHT:
                return False
            if self.board[cell_y][cell_x] is not None:
                return False
        return True

    def spawn_piece(self):
        self.current_piece = self.next_piece
        self.current_piece.x = START_X
        self.current_piece.y = START_Y
        self.current_piece.rotation = 0
        self.next_piece = self._new_piece()

        if not self._is_valid(self.current_piece):
            self.game_over = True

    def move_left(self):
        if not self.game_over:
            self._try_move(-1, 0)
            self.render()

    def move_right(self):
        if not self.game_over:
            self._try_move(1, 0)
            self.render()

    def soft_drop(self):
        if self.game_over:
            return
        if not self._try_move(0, -1):
            self.lock_piece()
        self.render()

    def rotate_piece(self):
        if self.game_over or self.current_piece is None:
            return

        next_rotation = (self.current_piece.rotation + 1) % 4
        for shift_x in (0, -1, 1, -2, 2):
            if self._is_valid(
                self.current_piece,
                x=self.current_piece.x + shift_x,
                y=self.current_piece.y,
                rotation=next_rotation,
            ):
                self.current_piece.x += shift_x
                self.current_piece.rotation = next_rotation
                self.render()
                return

    def hard_drop(self):
        if self.game_over:
            return
        while self._try_move(0, -1):
            pass
        self.lock_piece()
        self.render()

    def _try_move(self, dx, dy):
        if self.current_piece is None:
            return False

        new_x = self.current_piece.x + dx
        new_y = self.current_piece.y + dy
        if self._is_valid(self.current_piece, x=new_x, y=new_y):
            self.current_piece.x = new_x
            self.current_piece.y = new_y
            return True
        return False

    def lock_piece(self):
        if self.current_piece is None:
            return

        for cell_x, cell_y in self.current_piece.cells():
            self.board[cell_y][cell_x] = self.current_piece.color

        cleared = self.clear_lines()
        if cleared:
            self.score += self._score_for_lines(cleared)
            self.lines += cleared
            self.level = self.lines // 10 + 1
            self.drop_delay = max(MIN_DROP_MS, INITIAL_DROP_MS - (self.level - 1) * DROP_STEP_MS)

        self.spawn_piece()

    def clear_lines(self):
        cleared = 0
        new_board = []

        for row in self.board:
            if all(cell is not None for cell in row):
                cleared += 1
            else:
                new_board.append(row)

        while len(new_board) < BOARD_HEIGHT:
            new_board.append([None for _ in range(BOARD_WIDTH)])

        self.board = new_board
        return cleared

    def _score_for_lines(self, cleared):
        table = {1: 100, 2: 300, 3: 500, 4: 800}
        return table.get(cleared, cleared * 200) * self.level

    def reset(self):
        self.board = self._empty_board()
        self.score = 0
        self.lines = 0
        self.level = 1
        self.drop_delay = INITIAL_DROP_MS
        self.game_over = False
        self.next_piece = self._new_piece()
        self.spawn_piece()
        self.render()

    def draw_board(self):
        self.board_drawer.clear()
        for y, row in enumerate(self.board):
            for x, color in enumerate(row):
                if color is None:
                    continue
                self._stamp_cell(self.board_drawer, x, y, color)

        if self.current_piece is not None and not self.game_over:
            for x, y in self.current_piece.cells():
                self._stamp_cell(self.board_drawer, x, y, self.current_piece.color)

    def draw_preview(self):
        self.preview_drawer.clear()

        cells = self.next_piece.cells(x=0, y=0, rotation=0)
        min_x = min(x for x, _ in cells)
        max_x = max(x for x, _ in cells)
        min_y = min(y for _, y in cells)
        max_y = max(y for _, y in cells)

        width = max_x - min_x + 1
        height = max_y - min_y + 1
        start_x = 210 - (width * PREVIEW_CELL) / 2 + PREVIEW_CELL / 2
        start_y = 70 - (height * PREVIEW_CELL) / 2 + PREVIEW_CELL / 2

        for x, y in cells:
            draw_x = start_x + (x - min_x) * PREVIEW_CELL
            draw_y = start_y + (y - min_y) * PREVIEW_CELL
            self._stamp_preview_cell(draw_x, draw_y, self.next_piece.color)

    def _stamp_cell(self, pen, grid_x, grid_y, color):
        pen.color(color)
        pen.goto(BOARD_LEFT + grid_x * CELL_SIZE + CELL_SIZE / 2, BOARD_BOTTOM + grid_y * CELL_SIZE + CELL_SIZE / 2)
        pen.stamp()

    def _stamp_preview_cell(self, x, y, color):
        self.preview_drawer.color(color)
        self.preview_drawer.goto(x, y)
        self.preview_drawer.stamp()

    def render(self):
        self.draw_board()
        self.draw_preview()
        self.hud.draw(self.score, self.lines, self.level, self.next_piece.name, self.game_over)
        self.screen.update()

    def game_loop(self):
        if not self.game_over:
            if not self._try_move(0, -1):
                self.lock_piece()

        self.render()
        self.screen.ontimer(self.game_loop, self.drop_delay)

    def run(self):
        self.render()
        self.game_loop()
        turtle.done()
