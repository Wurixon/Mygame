import math
import time
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QTransform, QPixmap, QCursor
from PyQt5.QtWidgets import QWidget

class GameWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.game_widget = None
        self.floor_texture = QPixmap("background/floor_texture.png")
        self.bullet_texture = QPixmap("bullet/bullet.png")
        self.player_texture = QPixmap("player/player.png")

        self.camera_x = 0
        self.camera_y = 0

        self.player_x = 400
        self.player_y = 300
        self.player_rotation = 0

        self.key_pressed = {
            Qt.Key_W: False,
            Qt.Key_S: False,
            Qt.Key_A: False,
            Qt.Key_D: False
        }

        self.bullets = []

        self.health = 100

        self.setFocusPolicy(Qt.StrongFocus)
        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.update)
        self.timer.start()

        self.last_shot_time = 0

        self.health_textures = {
            "100hp": QPixmap("player/100hp.png"),
            "75hp": QPixmap("player/75hp.png"),
            "50hp": QPixmap("player/50hp.png"),
            "25hp": QPixmap("player/25hp.png"),
            "0hp": QPixmap("player/0hp.png")
        }

    def draw_health_bar(self, painter: QPainter):
        # Код для малювання панелі здоров'я
        # Визначення параметрів панелі здоров'я
        bar_width = 100
        bar_height = 10
        bar_x = (self.width() - bar_width) / 2
        bar_y = self.height() - bar_height - 10

    def decrease_health(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.game_over()

    def game_over(self):
        # Зупинка гри або виконання необхідних дій при завершенні гри
        self.parent().timer.stop()
        print("Гра завершена!")

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            # Очищення екрану
            painter.fillRect(0, 0, self.width(), self.height(), Qt.black)

            # Обчислення позиції камери, що забезпечує її розташування над персонажем
            camera_x = self.width() / 2 - self.player_x - self.player_texture.width() / 2
            camera_y = self.height() / 2 - self.player_y - self.player_texture.height() / 2

            # Зсування малювання на основі позиції камери
            painter.translate(int(camera_x), int(camera_y))

            # Малювання підлоги
            for x in range(0, self.width(), self.floor_texture.width()):
                for y in range(0, self.height(), self.floor_texture.height()):
                    painter.drawPixmap(int(x), int(y), self.floor_texture)

            transform = QTransform().translate(-self.camera_x, -self.camera_y)
            painter.setTransform(transform)

            # Малювання персонажа з оберненням
            transform = QTransform().translate(int(self.player_x), int(self.player_y)).rotate(self.player_rotation)
            painter.setTransform(transform)
            painter.drawPixmap(-self.player_texture.width() // 2, -self.player_texture.height() // 2,
                               self.player_texture)

    def keyPressEvent(self, event):
        try:
            # Код для обробки натискання клавіш
            if event.key() == Qt.Key_W:
                self.game_widget.key_pressed[Qt.Key_W] = True
            elif event.key() == Qt.Key_S:
                self.game_widget.key_pressed[Qt.Key_S] = True
            elif event.key() == Qt.Key_A:
                self.game_widget.key_pressed[Qt.Key_A] = True
            elif event.key() == Qt.Key_D:
                self.game_widget.key_pressed[Qt.Key_D] = True

            if event.key() == Qt.Key_Q:
                self.game_widget.player_rotation -= 10
            elif event.key() == Qt.Key_E:
                self.game_widget.player_rotation += 10
        except Exception as e:
            # Обробка винятку
            print("Помилка обробки натискання клавіш:", str(e))

    def keyReleaseEvent(self, event):
        try:
            # Обробка відпускання клавіш
            if event.key() == Qt.Key_W:
                self.key_pressed[Qt.Key_W] = False
            elif event.key() == Qt.Key_S:
                self.key_pressed[Qt.Key_S] = False
            elif event.key() == Qt.Key_A:
                self.key_pressed[Qt.Key_A] = False
            elif event.key() == Qt.Key_D:
                self.key_pressed[Qt.Key_D] = False
        except Exception as e:
            # Обробка винятку
            print("Помилка обробки відпускання клавіш:", str(e))

    def mousePressEvent(self, event):
        try:
            # Обробка натискання лівої клавіші миші
            if event.button() == Qt.LeftButton:
                current_time = time.time()
                if current_time - self.last_shot_time >= 1:  # Перевірка часу затримки
                    self.shoot()
                    self.last_shot_time = current_time
        except Exception as e:
            # Обробка винятку
            print("Помилка обробки натискання миші:", str(e))

    def update(self):
        # Оновлення стану гри
        self.move_player()
        self.check_collision()
        self.update_bullets()

        # Перемалювання екрану
        self.repaint()

    def move_player(self):
        speed = 5  # Швидкість руху персонажа

        if self.key_pressed[Qt.Key_W]:
            self.player_y -= speed
        elif self.key_pressed[Qt.Key_S]:
            self.player_y += speed
        if self.key_pressed[Qt.Key_A]:
            self.player_x -= speed
        elif self.key_pressed[Qt.Key_D]:
            self.player_x += speed

        # Обмежуємо позицію персонажа в межах екрану
        max_x = self.width() + self.camera_x
        max_y = self.height() + self.camera_y
        self.player_x = max(0, min(self.player_x, max_x))
        self.player_y = max(0, min(self.player_y, max_y))

        # Отримання позиції вказівника миші
        mouse_pos = self.mapFromGlobal(QCursor.pos())

        # Отримання кута між персонажем і вказівником миші
        dx = mouse_pos.x() - self.player_x
        dy = mouse_pos.y() - self.player_y
        self.player_rotation = math.degrees(math.atan2(dy, dx))

        if self.health <= 0:
            self.game_over()

    def shoot(self):
        # Виконати дії, які потрібно виконати при пострілі
        print("Постріл")

    def process_shot(self):
        # Код для обробки пострілу
        print("Обробка пострілу")

    def update_bullets(self):
        # Оновлення стану куль
        pass

    def game_over(self):
        # Зупинка гри або виконання необхідних дій при завершенні гри
        self.timer.stop()
        print("Гра завершена!")
