from PyQt5.QtWidgets import QMainWindow
from game_widget import GameWidget

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("2D Shooter")
        self.setFixedSize(800, 600)

        self.game_widget = GameWidget(self)
        self.setCentralWidget(self.game_widget)

        self.show()
