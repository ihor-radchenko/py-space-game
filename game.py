# Space shooter
#Ihor Radchenko
#art: https://opengameart.org by Kenney.nl
#sound: https://opengameart.org; http://www.bfxr.net; Freelancer

import pygame, sys, random, math

MAX_X = 400
MAX_Y = 650
FPS = 60
POWER_UP_TIME = 5000  # Время действия усилителя в мс. (5сек)

# Цвета ( R  , G ,  B )
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

pygame.init()

clock = pygame.time.Clock()
pygame.mixer.init()
screen = pygame.display.set_mode((MAX_X, MAX_Y))
pygame.display.set_caption('SpaceGame')
pygame.mouse.set_visible(0)

#Группы спрайтов
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
meteors = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
power_ups = pygame.sprite.Group()
cursors = pygame.sprite.Group()
ufos = pygame.sprite.Group()

#Загрузка графики
icon = pygame.image.load('img/icon.png').convert_alpha()
pygame.display.set_icon(icon)
background = pygame.image.load('img/bg.jpg').convert()
background = pygame.transform.scale(background, (520, 650))
background_rect = background.get_rect()
ufo_img = pygame.image.load('img/ufoRed.png').convert_alpha()
ship_img = pygame.image.load('img/player/playerShip.png').convert_alpha()
player_life_img = pygame.image.load('img/player/playerLife1_red.png').convert_alpha()
shield_img = pygame.image.load('img/player/shield1.png').convert_alpha()
bullet_img = [pygame.image.load('img/bullets/laserRed01.png').convert_alpha(),
              pygame.image.load('img/bullets/laserRed16.png').convert_alpha(),
              pygame.image.load('img/bullets/laserBlue01.png').convert_alpha(),
              pygame.image.load('img/bullets/laserBlue16.png').convert_alpha()]
meteor_img = [pygame.image.load('img/meteor/meteorBrown_big1.png').convert_alpha(),
              pygame.image.load('img/meteor/meteorBrown_big2.png').convert_alpha(),
              pygame.image.load('img/meteor/meteorBrown_big3.png').convert_alpha(),
              pygame.image.load('img/meteor/meteorBrown_big4.png').convert_alpha(),
              pygame.image.load('img/meteor/meteorBrown_med1.png').convert_alpha(),
              pygame.image.load('img/meteor/meteorBrown_med3.png').convert_alpha(),
              pygame.image.load('img/meteor/meteorBrown_small1.png').convert_alpha(),
              pygame.image.load('img/meteor/meteorBrown_small2.png').convert_alpha(),
              pygame.image.load('img/meteor/meteorBrown_tiny1.png').convert_alpha(),
              pygame.image.load('img/meteor/meteorBrown_tiny2.png').convert_alpha()]
enemies_img = pygame.image.load('img/Enemies/ufoBlue.png').convert_alpha()
numbers = []
for i in range(10):
    f = 'img/number/numeral{}.png'.format(i)
    num = pygame.image.load(f).convert_alpha()
    numbers.append(num)
explosion_anim = {}
explosion_anim['large'] = []
explosion_anim['small'] = []
explosion_anim['player_death'] = []
explosion_anim['boss_death'] = []
for i in range(9):
    f = 'img/explosion/regularExplosion0{}.png'.format(i)
    img = pygame.image.load(f).convert_alpha()
    img_large = pygame.transform.scale(img, (75, 75))
    explosion_anim['large'].append(img_large)
    img_small = pygame.transform.scale(img, (32, 32))
    explosion_anim['small'].append(img_small)
    f = 'img/explosion_player/sonicExplosion0{}.png'.format(i)
    img_player_death = pygame.image.load(f).convert_alpha()
    explosion_anim['player_death'].append(img_player_death)
    img_boss_death = pygame.transform.scale(img_player_death, (250, 250))
    explosion_anim['boss_death'].append(img_boss_death)
power_up_images = {'bolt': pygame.image.load('img/power_ups/bolt_gold.png').convert_alpha(),
                   'pill': pygame.image.load('img/power_ups/pill_red.png').convert_alpha(),
                   'shield': pygame.image.load('img/power_ups/shield_gold.png').convert_alpha(),
                   'star': pygame.image.load('img/power_ups/star_gold.png').convert_alpha(),
                   'things': pygame.image.load('img/power_ups/things_gold.png').convert_alpha()}
ui_img = {'red': pygame.image.load('img/UI/buttonRed.png').convert_alpha(),
          'blue': pygame.image.load('img/UI/buttonBlue.png').convert_alpha(),
          'green': pygame.image.load('img/UI/buttonGreen.png').convert_alpha(),
          'yellow': pygame.image.load('img/UI/buttonYellow.png').convert_alpha(),
          'cursor': pygame.image.load('img/UI/cursor.png').convert_alpha(),}
ui_act_img = {'red': pygame.image.load('img/UI/buttonRed_active.png').convert_alpha(),
              'blue': pygame.image.load('img/UI/buttonBlue_active.png').convert_alpha(),
              'green': pygame.image.load('img/UI/buttonGreen_active.png').convert_alpha(),
              'yellow': pygame.image.load('img/UI/buttonYellow_active.png').convert_alpha()}

# Загрузка звука
bg1_sound = 'sound/background.mp3'
pygame.mixer.music.load(bg1_sound)
pygame.mixer.music.play(-1, 0.0)
laser_shot = pygame.mixer.Sound('sound/fire_laser1.wav')
power_up_sound = pygame.mixer.Sound('sound/powerUp.ogg')
explosion_sound = []
for i in range(0, 3):
    s = 'sound/explosion/Explosion{}.wav'.format(i)
    exp_sound = pygame.mixer.Sound(s)
    explosion_sound.append(exp_sound)

class Ship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(ship_img, (50, 37))
        self.rect = self.image.get_rect()
        self.rect.centerx = MAX_X / 2
        self.rect.bottom = MAX_Y
        self.mask = pygame.mask.from_surface(self.image)
        self.fire_rate = 200  #---milisecond
        self.fire_tick = pygame.time.get_ticks()
        self.max_hp = 100
        self.hp = self.max_hp
        self.life = 3
        self.turret = 1
        self.gun = 1
        self.shield = 1
        self.damage = 25

    def update(self):
        # Когда подобран "щит"
        if self.shield >= 2 and pygame.time.get_ticks() - self.shield_tick >= POWER_UP_TIME:
            self.shield = 1
            self.image = pygame.transform.scale(ship_img, (50, 37))
            self.rect = self.image.get_rect()
            self.rect.bottom = MAX_Y
            self.shield_tick = pygame.time.get_ticks()
        # Когда подобраны патроны
        if self.turret >= 2 and pygame.time.get_ticks() - self.turret_tick >= POWER_UP_TIME:
            self.turret = 1
            self.turret_tick = pygame.time.get_ticks()
        # Когда подобрана "молния"
        if self.gun >= 2 and pygame.time.get_ticks() - self.gun_tick >= POWER_UP_TIME:
            self.gun = 1
            self.fire_rate = 200
            self.damage = 25
            self.gun_tick = pygame.time.get_ticks()
        self.new_fire_tick = pygame.time.get_ticks()
        # Управление мышкой
        self.rect.centerx = pygame.mouse.get_pos()[0]
        # Нормальное перемещение
        if self.shield == 1:
            if self.rect.left <= 0:
                self.rect.left = 0
            if self.rect.right >= MAX_X:
                self.rect.right = MAX_X
        # Перемещение когда подобран щит
        if self.shield >= 2:
            if self.rect.left - 8 <= 0:
                self.rect.left = -8
            if self.rect.right + 8 >= MAX_X:
                self.rect.right = MAX_X + 8
        # Стрельба мышкой
        if pygame.mouse.get_pressed()[0]:
            if self.new_fire_tick - self.fire_tick >= self.fire_rate:
                self.fire_tick = self.new_fire_tick
                self.shoot()

    def shoot(self):
        if self.turret == 1 and self.gun == 1:
            b = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(b)
            bullets.add(b)
            laser_shot.play()
        if self.gun >= 2:
            b = Bullet(self.rect.centerx, self.rect.top)
            b.image = bullet_img[1]
            all_sprites.add(b)
            bullets.add(b)
            laser_shot.play()
        if self.turret >= 2:
            b1 = Bullet(self.rect.left, self.rect.centery)
            b2 = Bullet(self.rect.right, self.rect.centery)
            all_sprites.add(b1)
            all_sprites.add(b2)
            bullets.add(b1)
            bullets.add(b2)
            laser_shot.play()
            laser_shot.play()

    def turret_power(self):
        self.turret += 1
        self.turret_tick = pygame.time.get_ticks()

    def gun_power(self):
        self.gun += 1
        self.damage = 40
        self.fire_rate = 150
        self.gun_tick = pygame.time.get_ticks()

    def shield_power(self):
        self.shield += 1
        self.image = pygame.transform.scale(shield_img, (66, 54))
        self.rect = self.image.get_rect()
        self.rect.bottom = MAX_Y + 8.5
        self.shield_tick = pygame.time.get_ticks()

class Enemies(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemies_img
        self.rect = self.image.get_rect()
        self.rect.center = (MAX_X / 2, 0 - 110)
        self.mask = pygame.mask.from_surface(self.image)
        self.dx = 0
        self.dy = 0
        self.shoot_tick = pygame.time.get_ticks()
        self.fire_rate = 300
        self.max_hp = 1000
        self.hp = self.max_hp
        self.damage = 45
        self.berz = 0
        self.position = 'hide'

    def update(self):
        if self.position == 'hide':
            self.rect.center = (MAX_X / 2, 0 - 110)
            self.dx = 0
            self.dy = 0
            self.hp = self.max_hp
        # Если начинается бой с боссом начинаем движение
        if level == 'boss' and self.position == 'hide':
            self.position = 'move'
        if self.position == 'move':
            self.dy = 4
        if self.position != 'hide':
            # Перемещение
            self.rect.centerx += self.dx
            self.rect.centery += self.dy
        if self.rect.top >= MAX_Y * .25 and self.position == 'move':
            self.position = 'start_position'
        if self.position == 'start_position':
            self.position = 'start_fight'
            self.dx = random.choice([-4, 4])
            self.dy = random.choice([-4, 4])
        if self.position == 'start_position' or self.position == 'start_fight':
            # Границы движения
            if self.rect.top <= MAX_Y * .11 or self.rect.bottom >= MAX_Y * .65 or random.randrange(150) == 1:
                self.dy = -self.dy
            if self.rect.left <= 0 or self.rect.right >= MAX_X or random.randrange(150) == 1:
                self.dx = -self.dx
        if self.position == 'start_fight':
            # Стрельба
            if pygame.time.get_ticks() - self.shoot_tick >= self.fire_rate:
                self.shoot()
                self.shoot_tick = pygame.time.get_ticks()

        # Переход в раш
        self.berzerc()

    def shoot(self):
        enemy_bullet = Bullet(self.rect.centerx, self.rect.bottom + 110)
        if self.berz >= 1:
            enemy_bullet.image = pygame.transform.rotate(bullet_img[3], 180)
        else:
            enemy_bullet.image = pygame.transform.rotate(bullet_img[2], 180)
        if self.berz == 2:
            enemy_bullet.dy = 12
        else:
            enemy_bullet.dy = 10
        all_sprites.add(enemy_bullet)
        enemy_bullets.add(enemy_bullet)

    def berzerc(self):
        if self.hp <= self.max_hp * .66:
            self.berz = 1
            self.damage = 70
        if self.hp <= self.max_hp * .33:
            self.berz = 2
            self.fire_rate = 225

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        self.image = bullet_img[0]
        self.rect = self.image.get_rect()
        self.rect.bottom = y_pos
        self.rect.centerx = x_pos
        self.mask = pygame.mask.from_surface(self.image)
        self.dy = -15

    def update(self):
        self.rect.centery += self.dy
        if self.rect.bottom <= 0 or self.rect.top >= MAX_Y:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image_orig = random.choice(meteor_img)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.bottom = 0
        self.rect.centerx = random.randrange(self.rect.width // 2, MAX_X - self.rect.width // 2)
        self.mask = pygame.mask.from_surface(self.image)
        self.dx = random.randrange(-4, 4)
        self.dy = random.randrange(1, 8)
        self.damage = math.sqrt(self.rect.width * self.rect.height)   # Расчет наносимого урона кораблю
        self.cost = math.ceil(100 / math.sqrt(self.rect.width * self.rect.height)) # Расчет получаемых очков
        self.takeaway_cost = math.ceil(100 / self.cost)
        self.rot = 0
        self.angle = random.randrange(-8, 8)
        self.tick_rot = pygame.time.get_ticks()

    def update(self):
        self.rotate()
        self.rect.centerx += self.dx
        self.rect.centery += self.dy
        if self.rect.top >= MAX_Y or self.rect.right <= 0 or self.rect.left >= MAX_X:
            self.kill()
            spawn_meteor()

    def rotate(self):
        self.new_tick_rot = pygame.time.get_ticks()
        if self.new_tick_rot - self.tick_rot >= FPS:
            self.tick_rot = self.new_tick_rot
            self.rot = (self.rot + self.angle) % 360
            self.image = pygame.transform.rotate(self.image_orig, self.rot)
            self.rect = self.image.get_rect(center=self.rect.center)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, type):
        super().__init__()
        self.type = type
        self.image = explosion_anim[self.type][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.tick_delay = pygame.time.get_ticks()

    def update(self):
        self.now = pygame.time.get_ticks()
        if self.now - self.tick_delay >= FPS:
            self.tick_delay = self.now
            self.frame += 1
            if self.frame == len(explosion_anim[self.type]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.type][self.frame]
                self.rect.center = center

class PowerUps(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.type = random.choice(['bolt', 'pill', 'shield', 'star', 'things'])
        self.image = power_up_images[self.type]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.mask = pygame.mask.from_surface(self.image)
        self.dy = 5

    def update(self):
        self.rect.centery += self.dy
        if self.rect.top >= MAX_Y:
            self.kill()

class Ufo(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image_orig = pygame.transform.scale(ufo_img, (182, 182))
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (MAX_X * .8, MAX_Y * .6)
        self.angle = random.choice([-5, 5])
        self.rot = 0
        self.tick_rot = pygame.time.get_ticks()

    def update(self):
        self.rotate()

    def rotate(self):
        self.new_tick_rot = pygame.time.get_ticks()
        if self.new_tick_rot - self.tick_rot >= FPS:
            self.tick_rot = self.new_tick_rot
            self.rot = (self.rot + self.angle) % 360
            self.image = pygame.transform.rotate(self.image_orig, self.rot)
            self.rect = self.image.get_rect(center=self.rect.center)

class Cursor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = ui_img['cursor']
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.x = pygame.mouse.get_pos()[0] - 5
        self.rect.y = pygame.mouse.get_pos()[1] - 5

def pause():

    loop = True

    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    all_sprites.empty()
                    meteors.empty()
                    main_menu()
                if event.key == pygame.K_ESCAPE:
                    loop = False

        msg_to_screen(screen, 'ПАУЗА', MAX_X // 2, MAX_Y // 2 - 50, 75, RED)
        msg_to_screen(screen, 'Чтобы продолжить нажми [ESC]', MAX_X // 2, MAX_Y // 2 + 40, 25, WHITE)
        msg_to_screen(screen, 'в главное меню - [Q]', MAX_X // 2, MAX_Y // 2 + 70, 25, WHITE)
        pygame.display.update()

def draw_button(text, x_pos, y_pos, color_button, action=None):
    button = ui_img[color_button]
    button_rect = button.get_rect()
    button_rect.center = (x_pos, y_pos)
    mouse_x = pygame.mouse.get_pos()[0]
    mouse_y = pygame.mouse.get_pos()[1]
    if mouse_x >= button_rect.left and mouse_x <= button_rect.right and mouse_y >= button_rect.top and mouse_y <= button_rect.bottom:
        button = ui_act_img[color_button]
        if pygame.mouse.get_pressed()[0] and action != None:
            if action == 'start_game':
                all_sprites.empty()
                meteors.empty()
                run_game()
            if action == 'controls':
                window_control()
            if action == 'author':
                about_author()
            if action == 'main':
                main_menu()
            if action == 'quit':
                pygame.quit()
                sys.exit()
    else:
        button = ui_img[color_button]
    screen.blit(button, button_rect)
    msg_to_screen(screen, text, button_rect.centerx, button_rect.centery, button_rect.height - 9)

def msg_to_screen(surf, message, x_pos, y_pos, size = 50, color = BLACK):
    font = pygame.font.SysFont("Calibri", size)
    text = font.render(message, True, color)
    text_rect = text.get_rect()
    text_rect.center = (x_pos, y_pos)
    surf.blit(text, text_rect)

def spawn_meteor():
    if level == 'meteor':
        while len(meteors) < 8:
            m = Meteor()
            all_sprites.add(m)
            meteors.add(m)

def draw_boss_hp_bar(x_pos, y_pos, scale, max_quantity):
    rect_width = 300
    if scale <= 0:
        scale = 0
    percent = scale / max_quantity
    pygame.draw.rect(screen, RED, (x_pos, y_pos, rect_width * percent, 20))
    pygame.draw.rect(screen, WHITE, (x_pos, y_pos, rect_width, 20), 2)

def draw_hp_bar(x_pos, y_pos, scale, max_quantity):
    rect_width = 100
    if scale <= 0:
        scale = 0
    percent = scale / max_quantity
    if percent >= .75:
        color_hp = GREEN
    elif .25 <= percent < .75:
        color_hp = YELLOW
    else:
        color_hp = RED
    pygame.draw.rect(screen, color_hp, (x_pos, y_pos, rect_width * percent, 15))
    pygame.draw.rect(screen, WHITE, (x_pos, y_pos, rect_width, 15), 2)

def draw_player_life(x_pos, y_pos, lifes):
    life_rect = player_life_img.get_rect()
    for i in range(lifes):
        x = x_pos + life_rect.width * i
        screen.blit(player_life_img, (x, y_pos))

def draw_score(x_pos, y_pos, score):
    count_number = 5
    score = str(score)
    numb_rect = numbers[0].get_rect()
    result = []
    for i in range(len(score)):
        if score[i] == '0':
            result.append(numbers[0])
        elif score[i] == '1':
            result.append(numbers[1])
        elif score[i] == '2':
            result.append(numbers[2])
        elif score[i] == '3':
            result.append(numbers[3])
        elif score[i] == '4':
            result.append(numbers[4])
        elif score[i] == '5':
            result.append(numbers[5])
        elif score[i] == '6':
            result.append(numbers[6])
        elif score[i] == '7':
            result.append(numbers[7])
        elif score[i] == '8':
            result.append(numbers[8])
        elif score[i] == '9':
            result.append(numbers[9])
        result_surf = pygame.Surface((count_number * numb_rect.width, numb_rect.height))
        result_surf_rect = result_surf.get_rect()
        result_surf_rect.center = (x_pos, y_pos)
        result_surf.set_colorkey(BLACK)
        for j in range(len(result)):
            first_pos = (count_number - len(result)) // 2
            x = numb_rect.width * j + first_pos
            result_surf.blit(result[j], (x, 0))
        screen.blit(result_surf, result_surf_rect)

def game_over():

    all_sprites.empty()
    enemies.empty()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        cursors.update()
        screen.blit(background, background_rect)
        draw_button('Еще раз', MAX_X / 2, MAX_Y * .6, 'green', 'start_game')
        draw_button('Выйти', MAX_X / 2, MAX_Y * .7, 'red', 'quit')
        msg_to_screen(screen, 'Вы проиграли', MAX_X / 2, MAX_Y * .15, 60, WHITE)
        msg_to_screen(screen, 'ваш счет: ' + str(score) + ' очков', MAX_X / 2, MAX_Y * .25, 40, WHITE)
        msg_to_screen(screen, 'Желаете выйти?', MAX_X / 2, MAX_Y * .35, 40, WHITE)
        msg_to_screen(screen, 'или сыграете еще?', MAX_X / 2, MAX_Y * .45, 40, WHITE)
        cursors.draw(screen)
        pygame.display.update()
        clock.tick(FPS)

def about_author():

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        all_sprites.update()
        ufos.update()
        cursors.update()
        screen.blit(background, background_rect)
        all_sprites.draw(screen)
        ufos.draw(screen)
        draw_button('Главное меню', MAX_X / 3, MAX_Y * .5, 'blue', 'main')
        draw_button('Выход', MAX_X / 3, MAX_Y * .9, 'red', 'quit')
        msg_to_screen(screen, 'dev-r:', MAX_X * .1, MAX_Y * .20, 25, WHITE)
        msg_to_screen(screen, 'Ihor Radchenko', MAX_X * .6, MAX_Y * .19, 50, WHITE)
        msg_to_screen(screen, 'art:', MAX_X * .05, MAX_Y * .26, 25, WHITE)
        msg_to_screen(screen, 'opengameart.org', MAX_X * .55, MAX_Y * .25, 50, WHITE)
        msg_to_screen(screen, 'by Keney.nl', MAX_X / 2, MAX_Y * .31, 50, WHITE)
        cursors.draw(screen)
        pygame.display.update()
        clock.tick(FPS)

def window_control():

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        all_sprites.update()
        ufos.update()
        cursors.update()
        screen.blit(background, background_rect)
        all_sprites.draw(screen)
        ufos.draw(screen)
        draw_button('Главное меню', MAX_X / 3, MAX_Y * .5, 'yellow', 'main')
        draw_button('Выход', MAX_X / 3, MAX_Y * .9, 'red', 'quit')
        msg_to_screen(screen, 'Управление:', MAX_X / 2, MAX_Y * .1, 60, WHITE)
        msg_to_screen(screen, 'перемещение мыщью', MAX_X / 2, MAX_Y * .25, 40, WHITE)
        msg_to_screen(screen, 'стрельба [ЛКМ]', MAX_X / 2, MAX_Y * .3, 40, WHITE)
        msg_to_screen(screen, '[ESC] - пауза', MAX_X / 2, MAX_Y * .35, 40, WHITE)
        cursors.draw(screen)
        pygame.display.update()
        clock.tick(FPS)

def main_menu():

    spawn_meteor()
    ufo = Ufo()
    ufos.add(ufo)
    cursor = Cursor()
    cursors.add(cursor)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        all_sprites.update()
        ufos.update()
        cursors.update()
        screen.blit(background, background_rect)
        all_sprites.draw(screen)
        ufos.draw(screen)
        draw_button('Играть', MAX_X / 3, MAX_Y * .6, 'green', 'start_game')
        draw_button('Управление', MAX_X / 3, MAX_Y * .7, 'yellow', 'controls')
        draw_button('Автор', MAX_X / 3, MAX_Y * .8, 'blue', 'author')
        draw_button('Выход', MAX_X / 3, MAX_Y * .9, 'red', 'quit')
        msg_to_screen(screen, 'SPACE', MAX_X / 2, MAX_Y * .15, 90, WHITE)
        msg_to_screen(screen, 'SCHOOTER', MAX_X / 2, MAX_Y * .25, 90, WHITE)
        msg_to_screen(screen, 'ver. 1.1', MAX_X - 25, MAX_Y - 5, 15, WHITE)
        cursors.draw(screen)
        pygame.display.update()
        clock.tick(FPS)

def run_game():

    global score
    global level
    score = 1
    level = 'meteor'
    ship = Ship()
    enemy = Enemies()
    all_sprites.add(ship)
    spawn_meteor()

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause()

        # Начало битвы с боссом
        if 14000 <= score % 15000:
            # Битва с боссом
            level = 'boss'
            enemies.add(enemy)
            all_sprites.add(enemy)

        # Попадание игрока по врагу
        hits = pygame.sprite.spritecollide(enemy, bullets, True, pygame.sprite.collide_mask)
        for hit in hits:
            explosion = Explosion(hit.rect.center, 'small')
            random.choice(explosion_sound).play()
            all_sprites.add(explosion)
            if enemy.position == 'start_fight':
                enemy.hp -= ship.damage
                score += 1
                if enemy.hp <= 0:
                    score += 3000
                    enemy.position = 'hide'
                    random.choice(explosion_sound).play()
                    explosion_enemy = Explosion(enemy.rect.center, 'boss_death')
                    all_sprites.add(explosion_enemy)
                    enemy.rect.center = (MAX_X / 2, 0 - 110)
                    level = 'meteor'
                    spawn_meteor()
                # Вероятность появления усилителя
                if random.randint(1, 100) >= 75:
                    power_up = PowerUps(hit.rect.center)
                    all_sprites.add(power_up)
                    power_ups.add(power_up)
        # Попадание врага по игроку
        hits = pygame.sprite.spritecollide(ship, enemy_bullets, True, pygame.sprite.collide_mask)
        for hit in hits:
            explosion = Explosion(hit.rect.center, 'small')
            random.choice(explosion_sound).play()
            all_sprites.add(explosion)
            if ship.shield == 1:
                ship.hp -= enemy.damage
                score -= 1
                if ship.hp <= 0:
                    ship.life -= 1
                    ship.hp = ship.max_hp
                    if ship.life == 0:
                        random.choice(explosion_sound).play()
                        explosion_player = Explosion(ship.rect.center, 'player_death')
                        all_sprites.add(explosion_player)
                        ship.kill()
        # Столкновение игрока с метеоритом
        hits = pygame.sprite.spritecollide(ship, meteors, True, pygame.sprite.collide_mask)
        for hit in hits:
            explosion = Explosion(hit.rect.center, 'small')
            random.choice(explosion_sound).play()
            all_sprites.add(explosion)
            if ship.shield == 1:
                ship.hp -= hit.damage
                if ship.hp <= 0:
                    ship.life -= 1
                    ship.hp = ship.max_hp
                    ship.hide = True
                if ship.life == 0:
                    random.choice(explosion_sound).play()
                    explosion_player = Explosion(ship.rect.center, 'player_death')
                    all_sprites.add(explosion_player)
                    ship.kill()
                score -= hit.takeaway_cost
                if score <= 0:
                    score = 0
            if ship.shield >= 2:
                score += hit.cost
            spawn_meteor()
        # Попадание снаряда в метеорит
        hits = pygame.sprite.groupcollide(meteors, bullets, True, True)
        for hit in hits:
            score += hit.cost
            explosion = Explosion(hit.rect.center, 'large')
            random.choice(explosion_sound).play()
            all_sprites.add(explosion)
            spawn_meteor()
            # Вероятность появления усилителя
            if random.randint(1, 100) >= 90:
                power_up = PowerUps(hit.rect.center)
                all_sprites.add(power_up)
                power_ups.add(power_up)
        # Подбор усилителя игроком
        hits = pygame.sprite.spritecollide(ship, power_ups, True)
        for hit in hits:
            power_up_sound.play()
            if hit.type == 'shield':
                ship.shield_power()
            if hit.type == 'bolt':
                ship.gun_power()
            if hit.type == 'things':
                ship.turret_power()
            if hit.type == 'star':
                score += 500
            if hit.type == 'pill':
                ship.hp += random.randint(10, 25)
                if ship.hp >= ship.max_hp:
                    ship.hp = ship.max_hp

        # Если игрок погиб и анимация смерти завершилась:
        if not ship.alive() and not explosion_player.alive():
            game_over()

        all_sprites.update()
        screen.blit(background, background_rect)
        all_sprites.draw(screen)
        draw_hp_bar(MAX_X * .7, MAX_Y * .03, ship.hp, ship.max_hp)
        draw_player_life(MAX_X * .05, MAX_Y * .02, ship.life)
        if level == 'boss' and enemy.position != 'hide':
            draw_boss_hp_bar(MAX_X * .15, MAX_Y * .08, enemy.hp, enemy.max_hp)
        draw_score(MAX_X / 2, MAX_Y * .035, score)
        pygame.display.update()
        clock.tick(FPS)

score = 0
level = 'meteor'
main_menu()
