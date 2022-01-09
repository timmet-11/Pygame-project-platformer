import pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


# Подключение фото для заднего фона
bg = pygame.image.load('bg.jpg')
bgd = pygame.image.load('bgd.jpg')


# Класс, описывающий поведение главного игрока
class Player(pygame.sprite.Sprite):
    # Изначально игрок смотрит вправо, поэтому эта переменная True
    right = True

    # Методы
    def __init__(self):
        super().__init__()

        # Создаем изображение для игрока
        self.image = pygame.image.load('idle.png')

        self.rect = self.image.get_rect()

        self.change_x = 0
        self.change_y = 0

    def update(self):
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

        self.rect = self.image.get_rect()


# Класс для расстановки платформ на сцене
class Level(object):
    def __init__(self, active_sprite_list, player, level_num):
        # Создаем группу спрайтов (поместим платформы различные сюда)
        self.things_list = pygame.sprite.Group()    ## группа спрайтов, в которой находятся все неподвижные объекты
                                                                                                            ## уровня
        self.active_sprite_list = active_sprite_list
        self.place_door = pygame.sprite.Group()
        # Ссылка на основного игрока
        self.player = player
        self.init_things(level_num, player)

    # Чтение данных из файла, создание платформ и двери (позже здесь могут быть шипы или типа того)
    def init_things(self, level_num, player):
        # Текстовой файл с данными про предметы уровня. Данные в таком формате:
        # ширина, высота, x и y позиция
        level_file = open(level_num, 'r').read().split('\n')
        level_platform = []
        count = 1
        string = level_file[count]
        while not (string == 'Door_'):
            level_platform.append([int(pl) for pl in string.split()])
            count += 1
            string = level_file[count]
        string = level_file[count + 1]
        door_inf = [int(door) for door in string.split()]

        # Перебираем массив и добавляем каждую платформу в группу спрайтов - platform_list
        for platform in level_platform:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.things_list.add(block)

        # то же самое с дверью
        door = Door(door_inf[0], door_inf[1])
        door.rect.x = door_inf[2]
        door.rect.y = door_inf[3]
        self.things_list.add(door)
        self.place_door.add(door)

    # Чтобы все рисовалось, нужно обновлять экран
    # При вызове этого метода обновление будет происходить
    def update(self):
        self.things_list.update()

    # Метод для рисования объектов на сцене
    def draw(self, screen):
        # Рисуем задний фон
        screen.blit(bg, (0, 0))

        # Рисуем все платформы, дверь (потом и шипы и все остальное) из группы спрайтов
        self.things_list.draw(screen)


def start_screen(screen):
    #Текст заставки
    text = ["Правила игры:",
            "Ваша задача дойти до двери.",
            "Опасайтесь всего подозрительного"]

    fon = pygame.transform.scale(bgd, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 0)
    text_coord = 200
    font = pygame.font.SysFont('Arial', 32)
    #Отображение текста на экране
    for line in text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 220
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

        run = True

    #Ожидание готовности
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


# Основная функция прогарммы
def main():
    # Инициализация
    pygame.init()

    # Установка высоты и ширины
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)

    # Название игры
    pygame.display.set_caption("Платформер")
    level_list = ['level_1', 'level_2']

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

    # Цикл будет до тех пор, пока пользователь не нажмет кнопку закрытия
    run = True

    # Используется для управления скоростью обновления экрана
    clock = pygame.time.Clock()

    #Заставка
    start_screen(screen)

    # Основной цикл программы
    while run:
        # Отслеживание действий
        if player.level_won:
            current_level_num += 1
            player.stop()
            player = Player()

            active_sprite_list = pygame.sprite.Group()
            active_sprite_list.add(player)
            current_level = Level(active_sprite_list, player, level_list[current_level_num])
            player.level = current_level
            player.rect.x = 340
            player.rect.y = SCREEN_HEIGHT - player.rect.height
            player.level_won = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Если закрыл программу, то останавливаем цикл
                run = False

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
        active_sprite_list.update()

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
        active_sprite_list.draw(screen)

        # Устанавливаем количество фреймов
        clock.tick(30)

        # Обновляем экран после рисования объектов
        pygame.display.flip()

    # Корректное закртытие программы
    pygame.quit()


main()
