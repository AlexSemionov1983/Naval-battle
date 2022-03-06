from random import randint


class BoardException(Exception):                                          # создаем исключения
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return 'Выстрел за доску'


class BoardUsedException(BoardException):
    def __str__(self):
        return 'Сюда уже стреляли'


class BoardWrongShipException(BoardException):                            # игрок не видит, компьютер просто
    pass                                                                  # делает еще одну попытку


class Dot:                                                                # Точка на поле
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):                                              # понадобится для сравнения
        return self.x == other.x and self.y == other.y

    def __repr__(self):                                                   # возвращает написание точки
        return f'Dot({self.x}, {self.y})'


class Ship:                                                               # корабль
    def __init__(self, length, bow, direction):
        self.length = length
        self.bow = bow                                                    # bow coord
        self.direction = direction                                        # 1-vert, 0-horiz
        self.lives = length

    @property
    def dots(self):                                                       # точки, которые занимает корабль
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x                                            # текущие координаты х и у
            cur_y = self.bow.y
            if self.direction == 0:                                       # вертикально/горизонтально
                cur_y += i
            else:
                cur_x += i
            ship_dots.append(Dot(cur_x, cur_y))                           # добавляем новую точку
        return ship_dots

    def hit(self, shot):                                                # попал/не попал
        return shot in self.dots


class Board:                                                              # игровое поле
    def __init__(self, hidden=False, size=6):
        self.hidden = hidden                                              # известно/не известно
        self.size = size
        self.count = 0                                                    # количество подбитых кораблей
        self.field = [['0'] * size for i in range(self.size)]
        self.busy = []                                                    # что-то здесь есть
        self.ships = []                                                   # корабли в игре

    def __str__(self):                                                    # рисуем поле на экране
        res = ''
        res += '   0 | 1 | 2 | 3 | 4 | 5 |'
        for i, row in enumerate(self.field):
            res += f'\n{i}| ' + ' | '.join(row) + ' |'
        if self.hidden:                                                   # если еще не известно
            res = res.replace('■', ' 0')                                  # меняем точку корабля на 0
        return res

    def out(self, d):                                                     # вне поля
        return not((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):                                  # обводим корабли по контуру
    # в итоге добавляем все точки вокруг корабля в список Board.busy
        near = [                                                          # все клетки вокруг точки
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:                                               # для каждой точки корабля
            for dx, dy in near:                                           # для каждой смежной точки
                cur = Dot(d.x + dx, d.y + dy)                             # новая точка на проверку
#                self.field[cur.x][cur.y] = '+'                           # для теста
                if not (self.out(cur)) and cur not in self.busy:          # не за рамками поля и не занята
                    if verb:                                              #
                        self.field[cur.x][cur.y] = '.'                    # меняем 0 на .
                    self.busy.append(cur)                                 # добавляем к занятым

    def add_ship(self, ship, verb=False):                                 # добавляем корабль
        for d in ship.dots:                                               # на каждую его точку
            if self.out(d) or d in self.busy:                             # если вне поля или занято
                raise BoardWrongShipException                             # выдаем исключение
        for d in ship.dots:
            self.field[d.x][d.y] = '■'                                    # помечаем точку корабля на поле
            self.busy.append(d)                                           # заносим точку в список звнятых
        self.ships.append(ship)                                           # добавить корабль в список
        self.contour(ship)                                                # добавляем все точки корабля и вокруг в busy

    def shoot(self, d):                                                   # стреляем по доске, d = Dot()
        if self.out(d):                                                   # если мимо доски
            raise BoardOutException                                       # выдает исключение
        if d in self.busy:                                                # попадает куда стрелять не надо
            raise BoardUsedException                                      # выдает исключение
        self.busy.append(d)                                               # добавляет выстрел в busy
        for ship in self.ships:                                           # проходим по всем кораблям
            if d in ship.dots:                                            # если попали в любую точку на корабле
                ship.lives -= 1                                           # количество жизней уменьшается
                self.field[d.x][d.y] = 'X'
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print('Корабль уничтожен!')
                    return False
                else:
                    print('Корабль ранен!')
                    return True
        self.field[d.x][d.y] = '.'
        print('Мимо!')
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход компьютера: {d.x}{d.y}')
        return d



b = Board()
s = Ship(3, Dot(3, 1), 0)
b.contour(s)
print(b)
