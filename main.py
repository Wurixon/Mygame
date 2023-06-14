import sys
from PyQt5.QtWidgets import QApplication
from game_window import GameWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game_window = GameWindow()
    sys.exit(app.exec_())
