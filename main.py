import pygame
import sys

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

#Присваеваем одной переменной количество всех уровней а другой количество очков
number_of_levels = 4
score = 0



# Подключение фото для заднего фона
bg = pygame.image.load('bg.jpg')
bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
bgd = pygame.image.load('bgd.jpg')


# Класс, описывающий поведение главного игрока
class Player(pygame.sprite.Sprite):
    # Изначально игрок смотрит вправо, поэтому эта переменная True
    right = True

    # Методы
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load('dino.png')
        self.image = pygame.transform.scale(self.image, (45, 70))
        self.rect = self.image.get_rect()

        self.change_x = 0
        self.change_y = 0

    def update(self):
        global this_star
        # В этой функции мы передвигаем игрока
        # Сперва устанавливаем для него гравитацию
        self.calc_grav()

        # Передвигаем его на право/лево
        # change_x будет меняться позже при нажатии на стрелки клавиатуры
        self.rect.x += self.change_x

        # Следим ударяем ли мы какой-то другой объект
        ## с этим можешь не разбираться
        block_hit_list = pygame.sprite.spritecollide(self, self.level.things_list, False)
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                self.rect.left = block.rect.right
            if isinstance(block, Door): # проверка: наткнулся ли игрок на дверь
                self.level_won = True
            if isinstance(block, Trap):
                self.die = True
            if isinstance(block, Chest):
                self.chest = True

        # Передвигаемся вверх/вниз
        self.rect.y += self.change_y

        # То же самое, только для вверх/вниз
        ## с этим тоже
        block_hit_list = pygame.sprite.spritecollide(self, self.level.things_list, False)
        for block in block_hit_list:
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom
            if isinstance(block, Door): # проверка: наткнулся ли игрок на дверь
                self.level_won = True
            if isinstance(block, Trap):
                self.die = True
            if isinstance(block, Chest):
                self.chest = True

            # Останавливаем вертикальное движение
            self.change_y = 0

    def calc_grav(self):
        # Здесь мы вычисляем как быстро объект будет
        # падать на землю под действием гравитации
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += 0.95

        # Если уже на земле, то ставим позицию Y как 0
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def jump(self):
        # Обработка прыжка
        # Нам нужно проверять здесь, контактируем ли мы с чем-либо
        # или другими словами, не находимся ли мы в полете.
        # Для этого опускаемся на 10 единиц, проверем соприкосновение и далее поднимаемся обратно
        self.rect.y += 10
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.things_list, False)
        self.rect.y -= 10

        # Если все в порядке, прыгаем вверх
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -16

    # Передвижение игрока
    def go_left(self):
        # Сами функции будут вызваны позже из основного цикла
        self.change_x = -9  # Двигаем игрока по Х
        if self.right:  # Проверяем куда он смотрит и если что, переворачиваем его
            self.flip()
            self.right = False

    def go_right(self):
        # то же самое, но вправо
        self.change_x = 9
        if not self.right:
            self.flip()
            self.right = True

    def stop(self):  # останавливает игрока
        # вызываем этот метод, когда не нажимаем на клавиши
        self.change_x = 0

    def flip(self):
        # переворот игрока (зеркальное отражение)
        self.image = pygame.transform.flip(self.image, True, False)


class Chest(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.image = pygame.image.load('treasure.png')
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()


class Star(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.image = pygame.image.load('starIcon.png')
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()


class Grey_Star(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.image = pygame.image.load('grey_starIcon.png')
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()


class Trap(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.image = pygame.image.load('trap.png')
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()


# выход на следующий уровень
class Door(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load('Door01.png'), (width, height))
        self.rect = self.image.get_rect()


# Класс для описания платформы
class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height):
        # Конструктор платформ
        super().__init__()
        # Также указываем фото платформы
        self.image = pygame.image.load('platform.png')
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()


# Класс для расстановки платформ на сцене
class Level(object):
    def __init__(self, active_sprite_list, player, level_num):
        # Создаем группу спрайтов (поместим платформы различные сюда)
        self.things_list = pygame.sprite.Group()    ## группа спрайтов, в которой находятся все неподвижные объекты
                                                                                                            ## уровня
        self.active_sprite_list = active_sprite_list
        # Ссылка на основного игрока
        self.player = player
        self.init_things(level_num, player)

    # Чтение данных из файла, создание платформ и двери (позже здесь могут быть шипы или типа того)
    def init_things(self, level_num, player):
        # Текстовой файл с данными про предметы уровня. Данные в таком формате:
        # ширина, высота, x и y позиция
        level_file = open(level_num, 'r').read().split('\n')
        level_platform = []
        level_trap = []
        count = 1
        string = level_file[count]
        while not (string == 'Trap_'):
            level_platform.append([int(pl) for pl in string.split()])
            count += 1
            string = level_file[count]
        string = level_file[count + 1]
        while not (string == 'Chest_'):
            level_trap.append([int(tr) for tr in string.split()])
            count += 1
            string = level_file[count]
        string = level_file[count + 1]
        chest_inf = [int(ch) for ch in string.split()]
        string = level_file[count + 3]
        door_inf = [int(door) for door in string.split()]

        # Перебираем массив и добавляем каждую платформу в группу спрайтов - platform_list
        for platform in level_platform:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.things_list.add(block)

        for trap in level_trap:
            tr = Trap(trap[0], trap[1])
            tr.rect.x = trap[2]
            tr.rect.y = trap[3]
            tr.player = self.player
            self.things_list.add(tr)

        grey_star = Grey_Star(50, 50)
        grey_star.rect.x = 20
        grey_star.rect.y = 20
        self.things_list.add(grey_star)

        chest = Chest(chest_inf[0], chest_inf[1])
        chest.rect.x = chest_inf[2]
        chest.rect.y = chest_inf[3]
        self.things_list.add(chest)

        # то же самое с дверью
        door = Door(door_inf[0], door_inf[1])
        door.rect.x = door_inf[2]
        door.rect.y = door_inf[3]
        self.things_list.add(door)

    # Чтобы все рисовалось, нужно обновлять экран
    # При вызове этого метода обновление будет происходить
    def update(self):
        self.things_list.update()
        self.active_sprite_list.update()

    # Метод для рисования объектов на сцене
    def draw(self, screen):
        # Рисуем задний фон
        screen.blit(bg, (0, 0))

        # Рисуем все платформы, дверь (потом и шипы и все остальное) из группы спрайтов
        self.things_list.draw(screen)
        self.active_sprite_list.draw(screen)



#Заставка
def start_screen(screen):
    #Текст заставки
    text = ["Правила игры:",
            "Ваша задача дойти до двери.",
            "Опасайтесь всего подозрительного"]

    fon = pygame.transform.scale(bgd, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 0)
    text_coord = 40
    font = pygame.font.SysFont('Taraxacum', 32)
    #Отображение текста на экране
    for line in text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 20
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

        run = True

    #Ожидание готовности
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


#Экран окончания уровня
def end_level_screen(screen):
    #Текст
    global score
    s = 'Ваш текущий счет состовляет ' + str(score) + ' очков'
    text = ['Вы прошли уровень',
            s,
            'Для продолжения нажмите на любую кнопку']

    fon = pygame.transform.scale(bgd, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 0)
    text_coord = 40
    font = pygame.font.SysFont('Taraxacum', 32)

    for line in text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 20
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    run = True

    #Ожидание готовности
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


#Экран окончания игры
def end_game_screen(screen):
    #Текст
    global score
    s = 'Ваш финальный счет ' + str(score) + ' очков'
    text = ['Поздравляем',
            'Вы прошли игру',
            s]

    fon = pygame.transform.scale(bgd, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 0)
    text_coord = 40
    font = pygame.font.SysFont('Taraxacum', 32)

    for line in text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 20
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


def die_screen(screen):
    global score
    s = 'Сейчас у вас ' + str(score) + ' очков'
    text = ['Вы проиграли',
            s,
            'Нажимите любую кнопку для продолжения']

    fon = pygame.transform.scale(bgd, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 0)
    text_coord = 40
    font = pygame.font.SysFont('Taraxacum', 32)

    for line in text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 20
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    run = True

    # Ожидание готовности
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()

def music():
    pygame.mixer.music.load("ethernight-club-by-kevin-macleod-from-filmmusic-io.mp3")
    pygame.mixer.music.play(loops=-1, start=0.0, fade_ms=0)
    pygame.mixer.music.set_volume(0.2)


# Основная функция прогарммы
def main():
    # Инициализация
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=512, devicename=None)
    pygame.init()
    music()

    # Установка высоты и ширины
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)

    # Название игры
    pygame.display.set_caption("Платформер")
    level_list = ['level_1', 'level_2', 'level_3', 'level_4', 'level_5']
    number_of_levels = 4

    # Создаем игрока
    player = Player()

    active_sprite_list = pygame.sprite.Group()
    active_sprite_list.add(player)

    # Устанавливаем текущий уровень
    current_level_num = 0
    current_level = Level(active_sprite_list, player, level_list[current_level_num])

    player.level = current_level

    player.rect.x = 340
    player.rect.y = SCREEN_HEIGHT - player.rect.height
    player.level_won = False
    player.die = False
    player.chest = False
    player.chest_now = False
    global score

    # Цикл будет до тех пор, пока пользователь не нажмет кнопку закрытия
    run = True

    # Используется для управления скоростью обновления экрана
    clock = pygame.time.Clock()

    # Заставка
    start_screen(screen)

    # Основной цикл программы
    while run:
        # Отслеживание действий
        if player.level_won:
            score += (current_level_num + 1) * 1500
            if player.chest:
                score += (current_level_num + 1) * 800
            current_level_num += 1
            if current_level_num > number_of_levels:
                end_game_screen(screen)
                sys.exit()
            else:
                end_level_screen(screen)
                player.stop()
                player = Player()

                active_sprite_list = pygame.sprite.Group()
                active_sprite_list.add(player)
                current_level = Level(active_sprite_list, player, level_list[current_level_num])
                player.level = current_level
                player.rect.x = 340
                player.rect.y = SCREEN_HEIGHT - player.rect.height
                player.level_won = False
                player.die = False
                player.chest = False
                player.chest_now = False
        if player.die:
            die_screen(screen)
            player.stop()
            player = Player()

            active_sprite_list = pygame.sprite.Group()
            active_sprite_list.add(player)
            current_level = Level(active_sprite_list, player, level_list[current_level_num])
            player.level = current_level
            player.rect.x = 340
            player.rect.y = SCREEN_HEIGHT - player.rect.height
            player.level_won = False
            player.die = False
            player.chest = False
            player.chest_now = False
        if player.chest and not player.chest_now:
            star = Star(50, 50)
            star.rect.x = 20
            star.rect.y = 20
            active_sprite_list.add(star)
            player.chest_now = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Если закрыл программу, то останавливаем цикл
                sys.exit()

            # Если нажали на стрелки клавиатуры, то двигаем объект
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_UP:
                    player.jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()

        # Обновляем игрока

        # Обновляем объекты на сцене
        current_level.update()

        # Если игрок приблизится к правой стороне, то дальше его не двигаем
        if player.rect.right > SCREEN_WIDTH:
            player.rect.right = SCREEN_WIDTH

        # Если игрок приблизится к левой стороне, то дальше его не двигаем
        if player.rect.left < 0:
            player.rect.left = 0

        # Рисуем объекты на окне
        current_level.draw(screen)

        # Устанавливаем количество фреймов
        clock.tick(30)

        # Обновляем экран после рисования объектов
        pygame.display.flip()


main()
