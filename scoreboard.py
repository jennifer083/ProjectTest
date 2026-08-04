import turtle


class ScoreBoard(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.hideturtle()
        self.penup()
        self.color("white")

    def draw(self, score, lines, level, next_name, game_over=False):
        self.clear()
        self.goto(210, 300)
        self.write("TETRIS", align="center", font=("Arial", 24, "bold"))

        self.goto(210, 250)
        self.write(f"Score: {score}", align="center", font=("Arial", 16, "normal"))

        self.goto(210, 220)
        self.write(f"Lines:  {lines}", align="center", font=("Arial", 16, "normal"))

        self.goto(210, 190)
        self.write(f"Level:  {level}", align="center", font=("Arial", 16, "normal"))

        self.goto(210, 140)
        self.write("Next piece:", align="center", font=("Arial", 16, "normal"))

        self.goto(210, 115)
        self.write(next_name, align="center", font=("Arial", 18, "bold"))

        self.goto(210, 40)
        self.write(
            "Controls\n"
            "Left/Right: move\n"
            "Down: soft drop\n"
            "Up or X: rotate\n"
            "Space: hard drop\n"
            "R: restart",
            align="center",
            font=("Arial", 12, "normal"),
        )

        if game_over:
            self.goto(0, 0)
            self.write(
                "GAME OVER\nPress R to restart",
                align="center",
                font=("Arial", 20, "bold"),
            )
