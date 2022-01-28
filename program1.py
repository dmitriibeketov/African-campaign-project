import pygame
from random import uniform
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel
from PyQt5.QtGui import QFont
import sys
import sip
import os

pygame.init()
WIDTH, HEIGHT = 800, 400
tile_width, tile_height = 80, 80
italian_reinforcement = (7000, 100, 210, 140, 300)
british_reinforcement = (20000, 700, 750, 500, 0)
german_reinforcement = (3500, 100, 105, 70, 0)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
all_squads = pygame.sprite.Group()
all_tiles = pygame.sprite.Group()
global event


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


images = {"desert": load_image("desert.JPG"), "minefield": load_image("minefield.JPG"),
          "mountains": load_image("mountains.JPG"), "river": load_image("river.JPG"),
          "Britishers": load_image("tank_matilda.JPG"), "Germans": load_image("tiger.JPG"),
          "Italians": load_image("Italian_tank.JPG"), "British_gunners": load_image("Britishers.JPG"),
          "German_gunners": load_image("Germans.JPG"), "Italian_gunners": load_image("Italians.JPG")}
gunners_dictionary = {"Britishers": "British_gunners", "Germans": "German_gunners", "Italians": "Italian_gunners"}
flags_dictionary = {"Britishers": "British_flag.JPG", "Italians": "Italian_flag.JPG", "Germans": "German_flag.JPG"}
initiation = {"Germans": 1, "Britishers": 2, "Italians": 3}
national_coefficient = {"Germans": 4, "French": 2, "Americans": 1.5, "Britishers": 1, "Italians": 0.3}
dictionary = {"Germans": 0, "Italians": 0, "Britishers": 1}


class Transmitter:
    def __init__(self):
        self.list = []
        self.force = (0, 0, 0, 0, 0)
        self.action = None
        self.italian_forces = (0, 0, 0, 0, 0)
        self.british_forces = (0, 0, 0, 0, 0)
        self.german_forces = (0, 0, 0, 0, 0)
        self.italian_losses = (0, 0, 0, 0, 0)
        self.british_losses = (0, 0, 0, 0, 0)
        self.german_losses = (0, 0, 0, 0, 0)
        self.running = False
        self.result = 0


transmitter = Transmitter()


class Example(QWidget):
    def __init__(self, force, transmitter):
        super().__init__()
        self.setGeometry(300, 300, 250, 300)
        self.setWindowTitle('divide squad')
        self.force = force
        self.transmitter = transmitter
        self.transmitter.force = (0, 0, 0, 0, 0)
        self.label = QLabel(self)
        self.label.setText("Не возможно разделить отряд таким образом!")
        self.label.move(0, 240)
        self.label.hide()

        self.labels = []
        self.edits = []
        for i in ["G", "T", "C", "A", "Tr"]:
            self.labels.append(QLabel(self))
            self.labels[-1].setText(f"{i} = ")
            self.labels[-1].move(0, 40 * ["G", "T", "C", "A", "Tr"].index(i) + 3)
            self.edits.append(QLineEdit(self))
            self.edits[-1].move(25, 40 * ["G", "T", "C", "A", "Tr"].index(i))
        self.button = QPushButton('divide', self)
        self.button.move(0, 200)
        self.button.clicked.connect(self.divide)

    def divide(self):
        flag = True
        flag1 = 0
        for i in self.edits:
            try:
                if int(i.text()) > self.force[self.edits.index(i)] or int(i.text()) < 0:
                    flag = False
                elif int(i.text()) == self.force[self.edits.index(i)]:
                    flag1 += 1
            except ValueError:
                flag = False
        if flag and flag1 < 5:
            self.transmitter.force = (int(self.edits[0].text()), int(self.edits[1].text()), int(self.edits[2].text()),
                                      int(self.edits[3].text()), int(self.edits[4].text()))
            sip.delete(self)
        else:
            self.label.show()


class Example1(QWidget):
    def __init__(self, transmitter):
        super().__init__()
        self.transmitter = transmitter
        self.setGeometry(300, 300, 30, 70)
        self.setWindowTitle('chose action')

        self.button1 = QPushButton('mining', self)
        self.button1.move(0, 0)
        self.button1.clicked.connect(self.answer)
        self.button2 = QPushButton('demining', self)
        self.button2.move(0, 40)
        self.button2.clicked.connect(self.answer)

    def answer(self):
        self.transmitter.action = self.sender().text()
        sip.delete(self)


class Start(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(500, 30, 1000, 1000)

        self.label = QLabel(self)
        file = open("data/regulations.txt")
        self.label.setText(file.read())
        self.label.move(0, 0)

        self.button = QPushButton("Begin!", self)
        self.button.clicked.connect(self.begin)
        self.button.move(400, 970)

        self.button1 = QPushButton("Escape", self)
        self.button1.clicked.connect(sys.exit)
        self.button1.move(500, 970)

    def begin(self):
        sip.delete(self)


class Outcome(QWidget):
    def __init__(self, losses, survived, result, end):
        super().__init__()
        self.setGeometry(300, 300, 600, 250)

        self.label = QLabel(self)
        self.label.setText(f"Потери англичан:\n{losses[0][0]} gunners\n{losses[0][1]} tanks\n{losses[0][2]} "
                           f"cannons\n{losses[0][3]} anti tank guns\n{losses[0][4]} means of transport")
        self.label.move(0, 0)
        self.label1 = QLabel(self)
        self.label1.setText(f"Потери итальянцев:\n{losses[1][0]} gunners\n{losses[1][1]} tanks\n{losses[1][2]} "
                            f"cannons\n{losses[1][3]} anti tank guns\n{losses[1][4]} means of transport")
        self.label1.move(200, 0)
        self.label2 = QLabel(self)
        self.label2.setText(f"Потери немцев:\n{losses[2][0]} gunners\n{losses[2][1]} tanks\n{losses[2][2]} "
                            f"cannons\n{losses[2][3]} anti tank guns\n{losses[2][4]} means of transport")
        self.label2.move(400, 0)

        self.label3 = QLabel(self)
        self.label3.setText(f"Уцелевшие английские войска:\n{survived[0][0]} gunners\n{survived[0][1]} tanks\n"
                            f"{survived[0][2]} cannons\n{survived[0][3]} "
                            f"anti tank guns\n{survived[0][4]} means of transport")
        self.label3.move(0, 100)
        self.label4 = QLabel(self)
        self.label4.setText(f"Уцелевшие итальянские войска:\n{survived[1][0]} gunners\n{survived[1][1]} tanks\n"
                            f"{survived[1][2]} cannons\n{survived[1][3]} "
                            f"anti tank guns\n{survived[1][4]} means of transport")
        self.label4.move(200, 100)
        self.label5 = QLabel(self)
        self.label5.setText(f"Уцелевшие немецкие войска:\n{survived[2][0]} gunners\n{survived[2][1]} tanks\n"
                            f"{survived[2][2]} cannons\n{survived[2][3]} "
                            f"anti tank guns\n{survived[2][4]} means of transport")
        self.label5.move(400, 100)

        self.label6 = QLabel(self)
        victory = {0: "германо-итальянской армии", 2: "английской армии"}
        self.label6.setText(f"Итог: победа {victory[result]}")
        self.label6.move(200, 200)

        self.button = QPushButton({0: "Next battle", 1: "Finish"}[end], self)
        self.button.clicked.connect(self.next_battle)
        self.button.move(200, 220)

        self.button1 = QPushButton("Escape", self)
        self.button1.clicked.connect(sys.exit)
        self.button1.move(300, 220)

    def next_battle(self):
        sip.delete(self)


class Finish(QWidget):
    def __init__(self, result):
        super().__init__()
        self.setGeometry(510, 400, 900, 100)
        self.label = QLabel(self)
        self.label.setFont(QFont("Times", 23))
        self.label.setText(
            "Полная и окончательная победа " + {0: "Германо-итальянской", 2: "английской"}[result] + " армии!")

        self.button1 = QPushButton("Finish", self)
        self.button1.clicked.connect(sys.exit)
        self.button1.move(400, 50)


def load_level(filename):
    filename = "data/" + filename
    map1 = []
    force = []
    for i in open(filename, 'r'):
        if i[0].isdigit():
            force.append(i.strip())
        else:
            map1.append(i.strip())
    return map1, force


def movements_accounting(acting, action):
    transmitter.list = sorted(all_squads.sprites(), key=lambda sprite: (
        initiation[sprite.nationality], -sprite.speed, sprite.tanks > 0,
        sprite.gunners / (sprite.tanks * 9 + 10 ** -10)))

    if action == "begin":
        acting = transmitter.list[0]
        acting.movements += 10
    elif action == "stop":
        acting = list(filter(lambda squad: squad.movements > 0, transmitter.list))[0]
        acting.movements = 0
    elif action == "move":
        acting.movements -= (10 / acting.speed)
    elif action == "attack":
        acting.movements -= 1
    elif action == "fortify":
        movement = acting.movements - max([0, acting.movements - 1])
        acting.movements = max([0, acting.movements - 1])
    elif type(action) == tuple:
        movement = min([action[1].mines * 3000 / (acting.gunners * national_coefficient[acting.nationality] * 1.25),
                        acting.movements - max([0, acting.movements - 1])])
        acting.movements -= movement
    elif action == "unite":
        squad1, squad2, new_squad = acting
        acting = squad2
        if transmitter.list.index(squad2) < transmitter.list.index(new_squad) < transmitter.list.index(squad1):
            new_squad.movements = min([squad2.movements - (10 + 10 / acting.speed), squad1.movements])
        elif transmitter.list.index(squad2) < transmitter.list.index(squad1) < transmitter.list.index(new_squad):
            new_squad.movements = min([squad2.movements - (10 + 10 / acting.speed), squad1.movements])
        elif transmitter.list.index(new_squad) < transmitter.list.index(squad2) < transmitter.list.index(squad1):
            new_squad.movements = min([squad2.movements - 10 / acting.speed, squad1.movements + 10])
            for i in transmitter.list[(transmitter.list.index(new_squad) + 1):transmitter.list.index(squad2)]:
                i.movements -= 10
            acting = new_squad
        elif transmitter.list.index(squad1) < transmitter.list.index(squad2) < transmitter.list.index(new_squad):
            new_squad.movements = -10
    elif action == "divide":
        squad, new_squad2, new_squad = acting
        if transmitter.list.index(new_squad2) < transmitter.list.index(new_squad) < transmitter.list.index(squad):
            new_squad2.movements = squad.movements
            new_squad.movements = squad.movements - 10 / new_squad.speed
            for i in transmitter.list[(transmitter.list.index(new_squad2) + 1):transmitter.list.index(squad)]:
                i.movements -= 10
            acting = new_squad2
        elif transmitter.list.index(new_squad) < transmitter.list.index(new_squad2) < transmitter.list.index(squad):
            new_squad2.movements = squad.movements
            new_squad.movements = squad.movements - 10 / new_squad.speed
            for i in transmitter.list[(transmitter.list.index(new_squad) + 1):transmitter.list.index(squad)]:
                i.movements -= 10
            acting = new_squad
        elif transmitter.list.index(new_squad2) < transmitter.list.index(squad):
            new_squad2.movements = squad.movements
            new_squad.movements = squad.movements - (10 + 10 / new_squad.speed)
            for j in transmitter.list[(transmitter.list.index(new_squad2) + 1):transmitter.list.index(squad)]:
                j.movements -= 10
            acting = new_squad2
        elif transmitter.list.index(new_squad) < transmitter.list.index(squad):
            new_squad.movements = squad.movements - 10 / new_squad.speed
            new_squad2.movements = squad.movements - 10
            for j in transmitter.list[(transmitter.list.index(new_squad) + 1):transmitter.list.index(squad)]:
                j.movements -= 10
            acting = new_squad
        else:
            new_squad.movements = squad.movements - (10 + 10 / new_squad.speed)
            new_squad.movements = squad.movements - 10
            acting = squad
    while acting.movements <= 0 or ((action == "unite") and (acting in [squad1, squad2])) or \
            ((action == "divide") and (acting == squad)):
        acting = transmitter.list[(transmitter.list.index(acting) + 1) % len(transmitter.list)]
        acting.movements += 10

    if action == "fortify" or type(action) == tuple:
        return movement


def damage(attacking, attacked):
    def damage_distribution(damage, objects, proportion):
        damage, objects, proportion = damage, objects, proportion
        if damage == 0 or sum(objects) == 0:
            return objects

        min_distribution = sorted([objects[i] / (damage * proportion[i]) for i in range(3) if proportion[i]] + [1])[0]
        objects = [round(objects[i] - min_distribution * proportion[i] * damage, 7) for i in range(len(objects))]
        damage -= (min_distribution * damage)
        total = 0
        for i in range(len(objects)):
            if objects[i] == 0:
                total += proportion[i]
                proportion[i] = 0
        proportion = [i / (1 - total) for i in proportion if total != 1]

        return damage_distribution(damage, objects, proportion)

    def force(object, army_type, subject, fortifications=0):
        object_next_enemies = 0
        for i in [(80, 0), (-160, 0), (80, 80), (0, -160), (0, 80)]:
            object.rect.x += i[0]
            object.rect.y += i[1]
            if list(filter(lambda squad: dictionary[squad.nationality] != dictionary[object.nationality],
                           pygame.sprite.spritecollide(object, all_squads, False))):
                object_next_enemies += 1
        subject_next_enemies = 0
        for i in [(80, 0), (-160, 0), (80, 80), (0, -160), (0, 80)]:
            subject.rect.x += i[0]
            subject.rect.y += i[1]
            if list(filter(lambda squad: dictionary[squad.nationality] != dictionary[subject.nationality],
                           pygame.sprite.spritecollide(subject, all_squads, False))):
                subject_next_enemies += 1
        answer = 0.05 * uniform(0.7, 1.3) * army_type * national_coefficient[object.nationality]
        answer *= (object.ammunition * (1.125 - object_next_enemies * 0.125) / (1.125 - subject_next_enemies * 0.125))
        answer /= ((1 + fortifications) * national_coefficient[subject.nationality] * subject.ammunition)
        return answer

    if not attacked.ammunition:
        all_squads.remove(attacked)
    if not attacking.ammunition:
        all_squads.remove(attacking)

    gunners, tanks, cannons, anti_tank_guns = \
        attacked.gunners, attacked.tanks, attacked.cannons, attacked.anti_tank_guns
    fortifications = pygame.sprite.spritecollide(attacked, all_tiles, False)[0].fortifications

    attacked.gunners, attacked.cannons, attacked.anti_tank_guns = damage_distribution(
        force(attacking, attacking.gunners, attacked, fortifications),
        [attacked.gunners, attacked.cannons, attacked.anti_tank_guns], [0.8, 0.1, 0.1])
    attacked.gunners, attacked.tanks, attacked.anti_tank_guns = damage_distribution(
        force(attacking, attacking.tanks, attacked, fortifications) * 2.5,
        [attacked.gunners, attacked.tanks, attacked.anti_tank_guns], [0.33, 0.5, 0.17])
    attacked.gunners, attacked.cannons, attacked.anti_tank_guns = damage_distribution(
        force(attacking, attacking.cannons, attacked, fortifications),
        [attacked.gunners, attacked.cannons, attacked.anti_tank_guns], [0.8, 0.1, 0.1])
    attacked.tanks = damage_distribution(
        force(attacking, attacking.anti_tank_guns, attacked, fortifications), [attacked.tanks, 0, 0], [1, 0, 0])[0]

    attacking.gunners, attacking.cannons, attacking.anti_tank_guns = damage_distribution(
        force(attacked, gunners, attacking), [attacking.gunners, attacking.cannons, attacking.anti_tank_guns],
        [0.8, 0.1, 0.1])
    attacking.gunners, attacking.tanks, attacking.anti_tank_guns = damage_distribution(
        force(attacked, tanks, attacking) * 2.5, [attacking.gunners, attacking.tanks, attacking.anti_tank_guns],
        [0.33, 0.5, 0.17])
    attacking.gunners, attacking.cannons, attacking.anti_tank_guns = damage_distribution(
        force(attacked, cannons, attacking), [attacking.gunners, attacking.cannons, attacking.anti_tank_guns],
        [0.8, 0.1, 0.1])
    attacking.tanks = damage_distribution(force(attacked, anti_tank_guns, attacking), [attacking.tanks, 0, 0],
                                          [1, 0, 0])[0]

    if attacked.surrounded:
        attacked.ammunition = round(attacked.ammunition - 0.1, 2)
    if attacking.surrounded:
        attacking.ammunition = round(attacking.ammunition - 0.1, 2)

    if attacked.gunners == attacked.tanks == attacked.cannons == attacked.anti_tank_guns == 0:
        all_squads.remove(attacked)
    if attacking.gunners == attacking.tanks == attacking.cannons == attacking.anti_tank_guns == 0:
        movements_accounting(attacking, "stop")
        all_squads.remove(attacking)

    if not ((list(filter(lambda squad: squad.nationality in ["Italians", "Germans"], all_squads))) and
            list(filter(lambda squad: squad.nationality == "Britishers", all_squads))):
        german_forces = [0, 0, 0, 0, 0]
        british_forces = [0, 0, 0, 0, 0]
        italian_forces = [0, 0, 0, 0, 0]
        for squad in list(filter(lambda squad: squad.nationality == "Germans", all_squads)):
            german_forces[0] += squad.gunners
            german_forces[1] += squad.tanks
            german_forces[2] += squad.cannons
            german_forces[3] += squad.anti_tank_guns
            german_forces[4] += squad.means_of_transport
        for squad in list(filter(lambda squad: squad.nationality == "Britishers", all_squads)):
            british_forces[0] += squad.gunners
            british_forces[1] += squad.tanks
            british_forces[2] += squad.cannons
            british_forces[3] += squad.anti_tank_guns
            british_forces[4] += squad.means_of_transport
        for squad in list(filter(lambda squad: squad.nationality == "Italians", all_squads)):
            italian_forces[0] += squad.gunners
            italian_forces[1] += squad.tanks
            italian_forces[2] += squad.cannons
            italian_forces[3] += squad.anti_tank_guns
            italian_forces[4] += squad.means_of_transport

        german_losses, british_losses, italian_losses = \
            list(transmitter.german_forces), list(transmitter.british_forces), list(transmitter.italian_forces)
        for i in range(5):
            german_losses[i] -= german_forces[i]
            british_losses[i] -= british_forces[i]
            italian_losses[i] -= italian_forces[i]
        transmitter.german_losses, transmitter.british_losses, transmitter.italian_losses = \
            tuple(german_losses), tuple(british_losses), tuple(italian_losses)

        transmitter.german_forces, transmitter.british_forces, transmitter.italian_forces = \
            tuple(german_forces), tuple(british_forces), tuple(italian_forces)
        transmitter.running = False
        all_squads.empty()
        all_tiles.empty()
        if not (any(transmitter.german_forces) or any(transmitter.italian_forces)):
            transmitter.result = 2
        else:
            transmitter.result = 0


def unite_squads(squad1, squad2):
    new_squad = Squad(squad1.nationality, squad1.rect.x // tile_width, (squad1.rect.y - 0.25 * tile_height) //
                      tile_height, (f"{squad1.gunners + squad2.gunners}, {squad1.tanks + squad2.tanks}, "
                                    f"{squad1.cannons + squad2.cannons}, "
                                    f"{squad1.anti_tank_guns + squad2.anti_tank_guns}, "
                                    f"{squad1.means_of_transport + squad2.means_of_transport}"))

    movements_accounting((squad1, squad2, new_squad), "unite")

    all_squads.remove(squad1)
    all_squads.remove(squad2)


def divide_squad(squad, new_x, new_y, new_force):
    new_squad = Squad(squad.nationality, new_x, new_y, new_force)
    force = (f"{squad.gunners - new_squad.gunners}, {squad.tanks - new_squad.tanks}, "
             f"{squad.cannons - new_squad.cannons}, {squad.anti_tank_guns - new_squad.anti_tank_guns}, "
             f"{squad.means_of_transport - new_squad.means_of_transport}")
    new_squad2 = Squad(squad.nationality, squad.rect.x // tile_width,
                       (squad.rect.y - 0.25 * tile_height) // tile_height, force)
    movements_accounting((squad, new_squad2, new_squad), "divide")
    all_squads.remove(squad)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(all_tiles)
        self.tile_type = tile_type
        self.image = images[self.tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.fortifications = 0
        self.mines = 0
        self.length = -1

    def update(self):
        if self.mines:
            self.image = images["minefield"]
        else:
            self.image = images[self.tile_type]
        font = pygame.font.Font(None, 12)
        if self.fortifications:
            screen.blit(font.render(f"F = {round(self.fortifications, 2)}", True, (0, 0, 0)),
                        (self.rect.x + 0.75 * tile_width, self.rect.y))
        if self.mines:
            screen.blit(font.render(f"M = {round(self.mines, 2)}", True, (0, 0, 0)),
                        (self.rect.x + tile_width * 0.6, self.rect.y))


class Squad(pygame.sprite.Sprite):
    def __init__(self, nationality, x, y, force):
        super().__init__(all_squads)
        self.nationality = nationality
        self.movements = 0
        self.surrounded = False
        self.ammunition = 1
        self.chosen = False
        self.down = self.down1 = False
        self.up = self.up1 = False

        force = [float(i) for i in force.split(", ")]
        self.gunners = force[0]
        self.tanks = force[1]
        self.cannons = force[2]
        self.anti_tank_guns = force[3]
        self.means_of_transport = force[4]
        if not (self.gunners or self.cannons or self.anti_tank_guns):
            self.speed = 5
        elif not self.means_of_transport:
            self.speed = 2
        else:
            self.speed = 2 + min([self.means_of_transport * 27 / (self.gunners + 18 * self.cannons +
                                                                  18 * self.anti_tank_guns), 3])

        if self.tanks * 9 > self.gunners:
            self.image = images[self.nationality]
        else:
            self.image = images[gunners_dictionary[self.nationality]]
        self.rect = self.image.get_rect().move(tile_width * x, tile_height * y + tile_height * 0.25)

    def check(self, args, chosen_button=1):
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos) and \
                args[0].button == chosen_button:
            self.down = True
        if args and args[0].type == pygame.MOUSEBUTTONUP and self.rect.collidepoint(args[0].pos) and \
                args[0].button == chosen_button:
            self.up = True
        if self.up and self.down:
            self.up = self.down = False
            self.chosen = True

        if args and args[0].type == pygame.MOUSEBUTTONDOWN and not self.rect.collidepoint(args[0].pos) and self.chosen \
                and args[0].button == chosen_button:
            self.down1 = True
        if args and args[0].type == pygame.MOUSEBUTTONUP and not self.rect.collidepoint(args[0].pos) and self.chosen \
                and args[0].button == chosen_button:
            self.up1 = True

        if self.up1 and self.down1 and self.chosen:
            self.up1 = self.down1 = self.chosen = False
            x, y = args[0].pos[0] // tile_width, (args[0].pos[1] - tile_height * 0.25) // tile_height
            if x == self.rect.x // tile_width and abs(y - (self.rect.y - tile_height * 0.25) // tile_height) == 1 or \
                    abs(x - self.rect.x // tile_width) == 1 and y == (self.rect.y - tile_height * 0.25) // tile_height:
                return True

    def check_collide(self):
        global event
        last_x, last_y = self.rect.x, self.rect.y
        self.rect.x = event.pos[0] // tile_width * tile_width
        self.rect.y = event.pos[1] // tile_height * tile_height + tile_height * 0.25
        tile = pygame.sprite.spritecollide(self, all_tiles, False)[0]
        answer = ("move", tile)
        enemies = list(filter(lambda x: dictionary[x.nationality] != dictionary[self.nationality],
                              pygame.sprite.spritecollide(self, all_squads, False)))
        allies = list(filter(lambda x: dictionary[x.nationality] == dictionary[self.nationality] and x != self,
                             pygame.sprite.spritecollide(self, all_squads, False)))
        if pygame.sprite.spritecollide(self, all_tiles, False)[0].image in [images["mountains"], images["river"]]:
            answer = ("stop",)
        if self.movements < 1:
            answer = ("stop", tile)
        elif enemies:
            answer = ("attack", enemies[0])
        elif allies:
            if allies[0].nationality == self.nationality:
                answer = ("unite", allies[0])
            else:
                answer = ("stop",)
        elif self.speed * self.movements < 10 or tile.mines:
            answer = ("stop", tile)
        self.rect.x, self.rect.y = last_x, last_y
        return answer

    def write(self):
        font = pygame.font.Font(None, 12)
        screen.blit(font.render(f"G = {round(self.gunners, 2)}", True, (0, 0, 0)),
                    (self.rect.x, self.rect.y - 0.25 * tile_height))
        screen.blit(font.render(f"T = {round(self.tanks, 2)}", True, (0, 0, 0)),
                    (self.rect.x, self.rect.y - 0.125 * tile_height))
        screen.blit(font.render(f"C = {round(self.cannons, 2)}", True, (0, 0, 0)),
                    (self.rect.x, self.rect.y + 0.5 * tile_height))
        screen.blit(font.render(f"A = {round(self.anti_tank_guns, 2)}", True, (0, 0, 0)),
                    (self.rect.x, self.rect.y + 0.625 * tile_height))
        screen.blit(font.render(f"I = {transmitter.list.index(self) + 1}", True, (0, 0, 0)),
                    (self.rect.x + 0.5 * tile_width, self.rect.y - 0.25 * tile_height))
        screen.blit(font.render(f"M = {max([round(self.movements, 2), 0])}", True, (0, 0, 0)),
                    (self.rect.x + 0.5 * tile_width, self.rect.y - 0.125 * tile_height))
        screen.blit(font.render(f"Sp = {round(self.speed, 2)}", True, (0, 0, 0)),
                    (self.rect.x + 0.5 * tile_height, self.rect.y + 0.5 * tile_height))
        screen.blit(font.render(f"Tr = {self.means_of_transport}", True, (0, 0, 0)),
                    (self.rect.x + 0.5 * tile_width, self.rect.y + 0.625 * tile_height))

    def update(self, *args):
        global event
        if self.check(args):
            if self.check_collide()[0] == "move":
                self.rect.x = event.pos[0] // tile_width * tile_width
                self.rect.y = event.pos[1] // tile_height * tile_height + tile_height * 0.25
                movements_accounting(self, "move")
            elif self.check_collide()[0] == "unite":
                unite_squads(self.check_collide()[1], self)
            elif self.check_collide()[0] == "attack":
                damage(self, self.check_collide()[1])
                if self in all_squads.sprites():
                    movements_accounting(self, "attack")
        if self.check(args, chosen_button=3) and self.check_collide()[0] == "move":
            app = QApplication(sys.argv)
            ex = Example((self.gunners, self.tanks, self.cannons, self.anti_tank_guns, self.means_of_transport),
                         transmitter)
            ex.show()
            app.exec()
            force = transmitter.force
            if force != (0, 0, 0, 0, 0):
                divide_squad(self, event.pos[0] // tile_width, (event.pos[1] - tile_height * 0.25) // tile_height,
                              f"{force[0]}, {force[1]}, {force[2]}, {force[3]}, {force[4]}")
            transmitter.force = (0, 0, 0, 0, 0)

        if self.check(args, chosen_button=2) and self.check_collide()[0] in ["move", "stop"] and \
                len(self.check_collide()) == 2:
            app = QApplication(sys.argv)
            ex = Example1(transmitter)
            ex.show()
            app.exec()
            if transmitter.action:
                tile = self.check_collide()[1]
            if transmitter.action == "mining":
                move = movements_accounting(self, "fortify") * self. \
                    gunners / 3000 * national_coefficient[self.nationality]
                tile.mines = min([tile.mines + move * 0.25, 10])
            elif transmitter.action == "demining":
                move = movements_accounting(self, ("demining", tile)) * self. \
                    gunners / 3000 * national_coefficient[self.nationality]
                tile.mines = round(tile.mines - move * 1.25, 2)
            transmitter.action = None

        number_tiles((dictionary[self.nationality] + 1) % 2)
        if self in all_squads and pygame.sprite.spritecollide(self, all_tiles, False)[0].length == -1:
            self.surrounded = True
        else:
            self.surrounded = False
            self.ammunition = 1

        transmitter.list = sorted(all_squads.sprites(), key=lambda sprite: (
            initiation[sprite.nationality], -sprite.speed, sprite.tanks > 0,
            sprite.gunners / (sprite.tanks * 9 + 10 ** -10)))
        if self in transmitter.list:
            self.write()


def generate_level(level):
    for y in range(len(level[0])):
        for x in range(len(level[0][y])):
            if level[0][y][x] == '.':
                Tile('desert', x, y)
            elif level[0][y][x] == '#':
                Tile("mountains", x, y)
            elif level[0][y][x] == '@':
                Tile("river", x, y)
            elif level[0][y][x] == '+':
                Tile('desert', x, y)
                Squad('Britishers', x, y, level[1].pop(0))
            elif level[0][y][x] == '-':
                Tile('desert', x, y)
                Squad('Italians', x, y, level[1].pop(0))
            elif level[0][y][x] == '!':
                Tile('desert', x, y)
                Squad('Germans', x, y, level[1].pop(0))
    movements_accounting(None, "begin")


def number_tiles(number):
    tiles = list(filter(lambda tile1: tile1.tile_type == "desert", all_tiles.sprites()))
    ephemeral_tiles = tiles.copy()
    for tile in ephemeral_tiles:
        if list(filter(lambda squad: dictionary[squad.nationality] == number,
                       pygame.sprite.spritecollide(tile, all_squads, False))) or tile.mines:
            tiles.remove(tile)
    for tile in tiles:
        tile.length = -1
    for tile in tiles:
        tile.rect.y -= [-80, 80][number]
        if len(pygame.sprite.spritecollide(tile, all_tiles, False)) == 1:
            tile.length = 0
        tile.rect.y += [-80, 80][number]

    unnumbered_tiles = list(filter(lambda tile2: tile2.length == -1, tiles))
    flag = True
    while unnumbered_tiles and flag:
        for tile in unnumbered_tiles:
            adjacent_numbers = []
            for i in [(5, 0), (-10, 0), (5, 5), (0, -10), (0, 5)]:
                tile.rect.x += i[0]
                tile.rect.y += i[1]
                collide_list = list(filter(lambda tile1: tile1 != tile,
                                           pygame.sprite.spritecollide(tile, tiles, False)))
                if collide_list:
                    adjacent_numbers.append(collide_list[0].length)
            adjacent_numbers = list(filter(lambda length: length != -1, adjacent_numbers))
            if adjacent_numbers:
                tile.length = min(adjacent_numbers) + 1
        if unnumbered_tiles == list(filter(lambda tile2: tile2.length == -1, tiles)):
            flag = False
        unnumbered_tiles = list(filter(lambda tile2: tile2.length == -1, tiles))


def forces_generator(map1):
    i, b, g = [], [], []
    for j in range(5):
        i.append(int(transmitter.italian_forces[j] + italian_reinforcement[j] * uniform(0.5, 2.0)))
        b.append(int(transmitter.british_forces[j] + british_reinforcement[j] * uniform(0.5, 2.0)))
        g.append(int(transmitter.german_forces[j] + german_reinforcement[j] * uniform(0.5, 2.0)))
    b[4], g[4] = b[0] // 9 + (b[2] + b[3]) * 2 + 1, g[0] // 9 + (g[2] + g[3]) * 2 + 1
    transmitter.italian_forces, transmitter.british_forces, transmitter.german_forces = tuple(i), tuple(b), tuple(g)

    file = open(map1, "r")
    file1 = ""
    for line in file:
        if line[0].isdigit():
            file1 = file1[:-1]
            break
        else:
            file1 += line
    file.close()

    file = open(map1, "w")
    file.write(file1)
    file.write("\n" + ", ".join([str(j) for j in g]))
    file.write("\n" + ", ".join([str(j) for j in i]))
    file.write("\n" + ", ".join([str(j) for j in b]))
    file.close()


def level(map1):
    pygame.display.set_caption("Battle")
    forces_generator(f"data/{map1}")
    generate_level(load_level(map1))
    transmitter.running = True
    while transmitter.running:
        global event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                movements_accounting(None, "stop")
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_f, pygame.K_d]:
                acting = list(filter(lambda squad: squad.movements > 0, transmitter.list))[0]
                fort = pygame.sprite.spritecollide(acting, all_tiles, False)[0].fortifications
                move = movements_accounting(acting, "fortify") * acting. \
                    gunners / 3000 * national_coefficient[acting.nationality]
                if event.key == pygame.K_f:
                    pygame.sprite.spritecollide(acting, all_tiles, False)[0].fortifications = \
                        min([2, (fort + 0.05 * move)])
                else:
                    pygame.sprite.spritecollide(acting, all_tiles, False)[0].fortifications = \
                        max([0, fort - 0.25 * move])

        screen.fill((0, 0, 0))
        all_tiles.draw(screen)
        all_tiles.update()
        all_squads.update(event)
        all_squads.draw(screen)
        pygame.display.flip()


def Outcome_window(end):
    app = QApplication([])
    ex = Outcome([transmitter.british_losses, transmitter.italian_losses, transmitter.german_losses],
                 [transmitter.british_forces, transmitter.italian_forces, transmitter.german_forces],
                 transmitter.result, end)
    ex.show()
    app.exec()


def splash_screen():
    app = QApplication([])
    ex = Start()
    ex.show()
    app.exec()


def final():
    app = QApplication([])
    ex = Finish(transmitter.result)
    ex.show()
    app.exec()


splash_screen()
for i in range(3):
    level(f'map{i + 1}.txt')
    Outcome_window(i // 2)
final()
