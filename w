import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
import random

class Character:
    def __init__(self):
        self.x = 200
        self.y = 300
        self.width = 50
        self.height = 50

    def move_left(self):
        self.x -= 5

    def move_right(self):
        self.x += 5


class Target:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 25
        self.height = 25
        self.speed = 3

    def update(self):
        self.y += self.speed
        if self.y > 600:
            self.y = -self.height
            self.x = random.randint(0, 750)


class GameWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.character = Character()
        self.targets = []
        self.score = 0  # Лічильник очків
        self.init_ui()


    def init_ui(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Моя 2D гра")

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.character.move_left()
        elif event.key() == Qt.Key_Right:
            self.character.move_right()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Малюємо персонажа
        painter.setBrush(QBrush(Qt.white))
        painter.drawRect(self.character.x, self.character.y, self.character.width, self.character.height)

        # Малюємо об'єкти
        for target in self.targets:
            painter.setBrush(QBrush(Qt.white))
            painter.drawRect(target.x, target.y, target.width, target.height)

        # Відображення лічильника очків
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 16))
        painter.drawText(10, 20, f"Score: {self.score}")

    def update_game(self):
        # ...

        # Перевірка зіткнення з об'єктами
        for target in self.targets:
            if self.check_collision(self.character, target):
                self.score += 1
                self.targets.remove(target)

        self.update()

    def check_collision(self, character, target):
        character_rect = QRect(character.x, character.y, character.width, character.height)
        target_rect = QRect(target.x, target.y, target.width, target.height)
        return character_rect.intersects(target_rect)

        self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    game = GameWindow()
    window.setCentralWidget(game)
    window.show()
    sys.exit(app.exec_())
