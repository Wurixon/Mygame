import math
import random
import time
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect
from PyQt5.QtGui import QPainter, QTransform, QPixmap, QCursor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication
from PyQt5 import QtCore



class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.current_x = x
        self.current_y = y
        self.width = 1
        self.height = 2
        self.position = QPoint(x, y)
        self.angle = angle

    def get_bullet_hitbox(bullet_x, bullet_y):
        bullet_width = 1  # Ширина кулі
        bullet_height = 2  # Висота кулі
        return bullet_x, bullet_y, bullet_width, bullet_height

    def move_bullet(self):
        speed = 5  # Швидкість руху кулі
        dx = speed * math.cos(math.radians(self.angle))
        dy = speed * math.sin(math.radians(self.angle))
        dx = int(dx)
        dy = int(dy)
        self.position = QPoint(self.position.x() + dx, self.position.y() + dy)

    def is_out_of_bounds(self):
        # Перевірте, чи куля виходить за межі екрану
        screen_width = QApplication.desktop().screen().width()
        screen_height = QApplication.desktop().screen().height()

        if self.x > screen_width or self.y > screen_height:
            return True
        else:
            return False

class Enemy:
    def __init__(self, x, y, speed):
        self.enemy_health = 100
        self.x = x
        self.y = y
        self.current_x = x
        self.current_y = y
        self.width = 32
        self.height = 32
        self.speed = speed

    def get_enemy_hitbox(enemy_x, enemy_y):
        enemy_width = 32  # Ширина ворога
        enemy_height = 32  # Висота ворога
        return enemy_x, enemy_y, enemy_width, enemy_height

    def update(self, player_x, player_y):
        # Визначення напрямку руху ворога відносно позиції героя
        dx = player_x - self.x
        dy = player_y - self.y

        # Нормалізація вектора напрямку
        magnitude = math.sqrt(dx ** 2 + dy ** 2)
        if magnitude != 0:
            dx /= magnitude
            dy /= magnitude

        # Зміна позиції ворога на основі швидкості та напрямку
        self.x += dx * self.speed
        self.y += dy * self.speed

class DeadEnemy:
    def __init__(self, x, y, texture):
        self.x = x
        self.y = y
        self.texture = texture

class Object:
    def __init__(self, x, y, height, width):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.current_x = x
        self.current_y = y

    def update(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y

        magnitude = math.sqrt(dx ** 2 + dy ** 2)
        if magnitude != 0:
            dx /= magnitude
            dy /= magnitude

    def rotate(self):
        # Поворот паркану на 90 градусів
        self.width, self.height = self.height, self.width

class GameWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.init_ui()

        self.floor_texture = QPixmap("background/floor_texture.png")
        self.bullet_texture = QPixmap("bullet/bullet.png")
        self.player_texture = QPixmap("player/player.png")
        self.enemy_texture = QPixmap("player/enemy.png")
        self.dead_enemy_texture = QPixmap("player/dead_enemy.png")
        self.fence_texture = QPixmap("objects/fence.png")
        self.tent_texture = QPixmap("objects/tent.png")
        self.box_texture = QPixmap("objects/box.png")
        self.snipertower_texture = QPixmap("objects/snipertower.png")
        self.gazebo_texture = QPixmap("objects/gazebo.png")

        self.camera_x = (self.floor_texture.width() - self.width()) // 2
        self.camera_y = (self.floor_texture.height() - self.height()) // 2

        self.player_x = 400
        self.player_y = 300
        self.player_rotation = 0
        self.player_width = 32
        self.player_height = 32

        self.key_pressed = {
            Qt.Key_W: False,
            Qt.Key_S: False,
            Qt.Key_A: False,
            Qt.Key_D: False,
            Qt.Key_Shift: False
        }

        self.bullets = []
        self.enemies = []
        self.fences = []
        self.tents = []
        self.boxes = []
        self.snipertowers = []
        self.gazeboes = []
        self.dead_enemies = []


        self.health = 100

        self.setFocusPolicy(Qt.StrongFocus)
        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.update)
        self.timer.start()

        self.last_shot_time = 0

        for i in range(1,5):
            self.enemy = Enemy(i * 100, 100, 10)
            self.enemies.append(self.enemy)
        for i in range(7):
            self.fence = Object(i * -128, 128, 64, 128)
            self.fences.append(self.fence)
        for i in range(1):
            self.tent = Object(-200, 50, 128, 128)
            self.tents.append(self.tent)
            self.box = Object(-128, 0, 64, 64)
            self.boxes.append(self.box)
            self.snipertower = Object(-400, 0, 96, 102)
            self.snipertowers.append(self.snipertower)
            self.gazebo = Object(-512, 50, 128, 256)
            self.gazeboes.append(self.gazebo)

        self.fireplace_textures = {
            "fireplace": QPixmap("objects/fireplace.png"),
            "fireplace1": QPixmap("objects/fireplace1.png"),
            "fireplace2": QPixmap("objects/fireplace2.png"),
            "fireplace3": QPixmap("objects/fireplace3.png"),
            "fireplace4": QPixmap("objects/fireplace4.png")
        }

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
        bar_width = 402
        bar_height = 42
        bar_x = 0  # Змінна, що визначає початкову позицію по осі X панелі здоров'я
        bar_y = 0  # Змінна, що визначає початкову позицію по осі Y панелі здоров'я

        # Визначення текстури панелі здоров'я на основі значення змінної health
        if self.health > 75:
            health_texture = self.health_textures["100hp"]
        elif self.health > 50:
            health_texture = self.health_textures["75hp"]
        elif self.health > 25:
            health_texture = self.health_textures["50hp"]
        elif self.health > 0:
            health_texture = self.health_textures["25hp"]
        else:
            health_texture = self.health_textures["0hp"]

        # Малювання текстури панелі здоров'я
        painter.drawPixmap(bar_x, bar_y, bar_width, bar_height, health_texture)

    def get_player_health(self):
        return self.health

    def decrease_health(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.game_over()

    def decrease_enemy_health(self, amount, enemy):
        enemy.enemy_health -= amount
        if enemy.enemy_health <= 0:
            self.enemies.remove(enemy)
            # Заміна ворога на текстуру dead_enemy_texture
            self.spawn_dead_enemy(enemy.x, enemy.y)

    def spawn_dead_enemy(self, x, y):
        # Створення об'єкту з текстурою dead_enemy_texture
        dead_enemy = DeadEnemy(x, y, self.dead_enemy_texture)
        self.dead_enemies.append(dead_enemy)

    def game_over(self):
        # Зупинка гри або виконання необхідних дій при завершенні гри
        self.parent().timer.stop()
        self.close()
        print("Гра завершена!")

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            # Обчислення позиції камери, що забезпечує її розташування над персонажем
            camera_x = -self.camera_x - self.player_x + self.width() / 2 - self.player_texture.width() / 2
            camera_y = -self.camera_y - self.player_y + self.height() / 2 - self.player_texture.height() / 2

            for enemy in self.enemies:
                enemy.current_x = -enemy.x - self.player_x + self.width() / 2 - self.player_texture.width() / 2
                enemy.current_y = -enemy.y - self.player_y + self.height() / 2 - self.player_texture.height() / 2

            for fence in self.fences:
                fence.current_x = -fence.x - self.player_x + self.width() / 2 - self.player_texture.width() / 2
                fence.current_y = -fence.y - self.player_y + self.height() / 2 - self.player_texture.height() / 2

            for tent in self.tents:
                tent.current_x = -tent.x - self.player_x + self.width() / 2 - self.player_texture.width() / 2
                tent.current_y = -tent.y - self.player_y + self.height() / 2 - self.player_texture.height() / 2

            for box in self.boxes:
                box.current_x = -box.x - self.player_x + self.width() / 2 - self.player_texture.width() / 2
                box.current_y = -box.y - self.player_y + self.height() / 2 - self.player_texture.height() / 2

            for snipertower in self.snipertowers:
                snipertower.current_x = -snipertower.x - self.player_x + self.width() / 2 - self.player_texture.width() / 2
                snipertower.current_y = -snipertower.y - self.player_y + self.height() / 2 - self.player_texture.height() / 2

            for gazebo in self.gazeboes:
                gazebo.current_x = -gazebo.x - self.player_x + self.width() / 2 - self.player_texture.width() / 2
                gazebo.current_y = -gazebo.y - self.player_y + self.height() / 2 - self.player_texture.height() / 2

            # Зсування малювання на основі позиції камери
            painter.translate(int(camera_x), int(camera_y))

            # Малювання підлоги
            for x in range(-2048, self.width() + self.floor_texture.width() * 16, self.floor_texture.width()):
                for y in range(-2048, self.height() + self.floor_texture.height() * 9, self.floor_texture.height()):
                    painter.drawPixmap(int(x), int(y), self.floor_texture)

            # Малювання полоси здоров'я
            transform = QTransform().translate(10, 750)
            painter.setTransform(transform)
            self.draw_health_bar(painter)

            transform = QTransform().translate(-self.camera_x, -self.camera_y)
            painter.setTransform(transform)

            # Малювання персонажа з оберненням
            transform = QTransform().translate(int(self.player_x), int(self.player_y)).rotate(self.player_rotation)
            painter.setTransform(transform)
            painter.drawPixmap(-self.player_texture.width() // 2, -self.player_texture.height() // 2,
                               self.player_texture)

            # Малювання ворога
            for enemy in self.enemies:
                if self.enemy.enemy_health <= 0:
                    transform = QTransform().translate(enemy.current_x, enemy.current_y)
                    painter.setTransform(transform)
                    painter.drawPixmap(self.dead_enemy_texture.width() // 2, self.dead_enemy_texture.height() // 2, self.dead_enemy_texture)

                else:
                    transform = QTransform().translate(enemy.current_x, enemy.current_y)
                    painter.setTransform(transform)
                    painter.drawPixmap(self.enemy_texture.width() // 2, self.enemy_texture.height() // 2,
                                       self.enemy_texture)

            # Малювання куль
            for bullet in self.bullets:
                transform = QTransform().translate(bullet.position.x(), bullet.position.y()).rotate(bullet.angle)
                painter.setTransform(transform)
                painter.drawPixmap(self.bullet_texture.width() // 2, self.bullet_texture.height() // 2,
                                   self.bullet_texture)

            # Малювання паркану
            for fence in self.fences:
                transform = QTransform().translate(fence.current_x, fence.current_y)
                painter.setTransform(transform)
                painter.drawPixmap(fence.width // 2, fence.height // 2, self.fence_texture)

            # Малювання бесідки
            for gazebo in self.gazeboes:
                transform = QTransform().translate(gazebo.current_x, gazebo.current_y)
                painter.setTransform(transform)
                painter.drawPixmap(self.gazebo_texture.width() // 2, self.gazebo_texture.height() // 2,
                                self.gazebo_texture)

            # Малювання намету
            for tent in self.tents:
                transform = QTransform().translate(tent.current_x, tent.current_y)
                painter.setTransform(transform)
                painter.drawPixmap(self.tent_texture.width() // 2, self.tent_texture.height() // 2,
                                   self.tent_texture)

            # Малювання коробки
            for box in self.boxes:
                transform = QTransform().translate(box.current_x, box.current_y)
                painter.setTransform(transform)
                painter.drawPixmap(self.box_texture.width() // 2, self.box_texture.height() // 2,
                                   self.box_texture)

            # Малювання снайперської вишки
            for snipertower in self.snipertowers:
                transform = QTransform().translate(snipertower.current_x, snipertower.current_y)
                painter.setTransform(transform)
                painter.drawPixmap(self.snipertower_texture.width() // 2, self.snipertower_texture.height() // 2,
                                   self.snipertower_texture)

        except Exception as e:
            # Обробка винятку
            print("Помилка обробки малювання:", str(e))

    def keyPressEvent(self, event):
        try:
            # Код для обробки натискання клавіш
            if event.key() == Qt.Key_W:
                self.key_pressed[Qt.Key_W] = True
            elif event.key() == Qt.Key_S:
                self.key_pressed[Qt.Key_S] = True
            elif event.key() == Qt.Key_A:
                self.key_pressed[Qt.Key_A] = True
            elif event.key() == Qt.Key_D:
                self.key_pressed[Qt.Key_D] = True
            if event.key() == QtCore.Qt.Key_F11:
                if self.isFullScreen():
                    self.showNormal()
                else:
                    self.showFullScreen()

            if event.key() == Qt.Key_Z:
                self.health = self.health - 25
            if event.key() == Qt.Key_X:
                self.decrease_enemy_health(25)

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
                if current_time - self.last_shot_time >= 0.1:  # Перевірка часу затримки
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
        speed = 1  # Швидкість руху персонажа

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

    def get_player_hitbox(self, player_x, player_y):
        player_width = 32  # Ширина гравця
        player_height = 32  # Висота гравця
        return player_x, player_y, player_width, player_height

    def shoot(self):
        bullet = Bullet(self.player_x, self.player_y, self.player_rotation)
        self.bullets.append(bullet)

    def process_shot(self):
        # Реалізуйте логіку обробки кулі
        for bullet in self.bullets:
            bullet.move_bullet()  # Здійсніть рух кулі

            if bullet.is_out_of_bounds():
                self.bullets.remove(bullet)  # Видаліть кулю, якщо вона виходить за межі

    def update_bullets(self):
        # Переміщення та перевірка куль
        bullets_copy = self.bullets.copy()  # Копіюємо список куль
        for bullet in bullets_copy:
            bullet.move_bullet()
            if bullet.is_out_of_bounds():
                self.bullets.remove(bullet)

    def restrict_movement(obj1_x, obj1_y, obj1_width, obj1_height, obj2_x, obj2_y, obj2_width, obj2_height, obj1_dx,
                          obj1_dy):

        obj1_right = obj1_x + obj1_width
        obj1_bottom = obj1_y + obj1_height
        obj2_right = obj2_x + obj2_width
        obj2_bottom = obj2_y + obj2_height

        if obj1_x < obj2_right and obj1_right > obj2_x and obj1_y < obj2_bottom and obj1_bottom > obj2_y:
            # Collision occurred
            # Determine the direction of collision
            dx_collision = obj2_x - (obj1_x + obj1_width) if obj1_dx > 0 else obj2_right - obj1_x
            dy_collision = obj2_y - (obj1_y + obj1_height) if obj1_dy > 0 else obj2_bottom - obj1_y

            # Restrict movement in the direction of collision
            if abs(dx_collision) < abs(dy_collision):
                obj1_dx = 0
            else:
                obj1_dy = 0

        return obj1_dx, obj1_dy

    def is_collide(self, hitbox1, hitbox2):
        # Перевірка зіткнень між двома хітбоксами
        # Повертає True, якщо виявлено зіткнення, інакше False
        player_x = hitbox1[0]
        player_y = hitbox1[1]
        fence_x = hitbox2[0]
        fence_y = hitbox2[1]
        enemy_x = hitbox2[0]
        enemy_y = hitbox2[1]
        player_width = hitbox1[2]
        player_height = hitbox1[3]
        fence_width = hitbox2[2]
        fence_height = hitbox2[3]
        enemy_width = hitbox2[2]
        enemy_height = hitbox2[3]

        if (player_x -32 < enemy_x + enemy_width and
            player_x + player_width > enemy_x and
            player_y -32 < enemy_y + enemy_height and
            player_y + player_height > enemy_y):
            return True
        elif(player_x -32 < fence_x + fence_width and
            player_x + player_width > fence_x and
            player_y -32 < fence_y + fence_height and
            player_y + player_height > fence_y):
            return True
        else:
            return False

    def check_collision(self):
        # Перевірка зіткнень куль з ворогами
        bullets_copy = self.bullets[:]  # Копіюємо список куль
        for bullet in bullets_copy:
            bullet_hitbox = self.get_bullet_hitbox(bullet.position.x(), bullet.position.y())  # Отримуємо хітбокс кулі
            for enemy in self.enemies:
                enemy_hitbox = self.get_enemy_hitbox(enemy.current_x, enemy.current_y)  # Отримуємо хітбокс ворога
                if self.is_collide(bullet_hitbox, enemy_hitbox):  # Оновлений виклик функції
                    self.bullets.remove(bullet)
                    self.decrease_enemy_health(25, enemy)

        # Перевірка зіткнень героя з ворогами
        player_hitbox = self.get_player_hitbox(self.player_x, self.player_y)  # Отримуємо хітбокс гравця
        for enemy in self.enemies:
            hitbox = self.get_enemy_hitbox(enemy.current_x, enemy.current_y)  # Отримуємо оновлений хітбокс ворога
            if self.is_collide(player_hitbox, hitbox):  # Оновлений виклик функції
                    self.decrease_health(random.randint(1, 20))  # Зменшуємо здоров'я гравця
                    self.decrease_enemy_health(random.randint(1, 10), enemy)  # Зменшуємо здоров'я ворога

        # Перевірка зіткнень героя з парканом
        for fence in self.fences:
            fence_hitbox = self.get_fence_hitbox(fence.current_x, fence.current_y)  # Отримуємо хітбокс паркану
            if self.is_collide(player_hitbox, fence_hitbox):  # Оновлений виклик функції
                self.decrease_health(random.randint(0, 1))  # Зменшуємо здоров'я гравцяddd

    def get_bullet_hitbox(self, bullet_x, bullet_y):
        # Код реалізації методу get_bullet_hitbox
        bullet_width = 1  # Ширина кулі
        bullet_height = 2  # Висота кулі
        return bullet_x, bullet_y, bullet_width, bullet_height

    def get_enemy_hitbox(self, enemy_x, enemy_y):
        enemy_width = 32  # Ширина ворога
        enemy_height = 32  # Висота ворога
        return enemy_x, enemy_y, enemy_width, enemy_height

    def get_fence_hitbox(self, fence_x, fence_y):
        fence_width = 128  # Ширина паркану
        fence_height = 64  # Висота паркану
        return fence_x, fence_y, fence_width, fence_height


