import random
import pygame
import sys

pygame.init() #游戏初始化

pygame.display.set_caption("PlaneGame_v2.0")

SCORE = 0 #游戏分数
HIGH_SCORE = 0 #游戏最高分

SCREEN_RECT = pygame.Rect(0, 0, 480, 700) #游戏屏幕

color_blue = (30, 144, 255)
color_green = (0, 255, 0)
color_red = (255, 0, 0)
color_purple = (148, 0, 211)
color_gray = (251, 255, 242)

FRAME_PER_SEC = 60 #刷新频率

#自定义事件
CREATE_ENEMY_EVENT = pygame.USEREVENT
HERO_FIRE_EVENT = pygame.USEREVENT + 1
BUFF1_SHOW_UP = pygame.USEREVENT + 2
BUFF2_SHOW_UP = pygame.USEREVENT + 3
ENEMY_FIRE_EVENT = pygame.USEREVENT + 4
BOMB_THROW = pygame.USEREVENT + 5


class GameScore(object): #游戏分数
    global SCORE

    def __init__(self):
        self.score = 0

    def getvalue(self):
        self.score = SCORE
        return self.score


class GameSprite(pygame.sprite.Sprite): #飞机大战游戏精灵
    
    def __init__(self, image_name, speedy=1, speedx=0): #初始化
        super().__init__() #调用父类的初始化方法

        self.image = pygame.image.load(image_name) #加载图片
        self.rect = self.image.get_rect() #获取图片尺寸
        self.speedy = speedy #垂直移动距离
        self.speedx = speedx #水平移动距离
        self.injury = 1 #伤害量
        self.index = 0 #程序控制指数
        self.bar = bloodline(color_blue, self.rect.x, self.rect.y - 10, self.rect.width) #精灵血量

    def update(self):
        self.rect.y += self.speedy #更新精灵垂直位置
        self.rect.x += self.speedx #更新精灵水平位置
        self.bar.y = self.rect.y - 10 #更新血条垂直位置
        self.bar.x = self.rect.x #更新血条水平位置


class Background(GameSprite): #背景游戏精灵
    
    def __init__(self, is_alt=False):

        super().__init__("./images/background.png")

        if is_alt: #初始化背景位置
            self.rect.y = -self.rect.height

    def update(self):

        super().update()

        if self.rect.y >= SCREEN_RECT.height: #判断是否需要重置背景位置
            self.rect.y = -self.rect.height


class Boss(GameSprite): #Boss游戏精灵

    def __init__(self):
        super().__init__("./images/enemy3_n1.png", 0, 1)
        self.music_boom = pygame.mixer.Sound("./music/enemy3_down.wav") #加载Boss爆炸音乐
        self.music_fly = pygame.mixer.Sound("./music/enemy3_flying.wav") #加载Boss飞行音乐
        self.music_fly.set_volume(0.1) #设置音乐音量
        self.rect.centerx = 240 #初始化位置
        self.y = 200
        self.isboom = False #中弹状态
        self.number = 3 #敌机类型编号
        self.index1 = 1
        self.index2 = 0
        self.index3 = 0
        self.index4 = 0
        self.injury = 1
        self.bar = bloodline(color_purple, 0, 0, 480, 8, 200)
        self.bullets = pygame.sprite.Group() #初始化子弹精灵组

    def fire(self): #发射子弹
            for j in range(2, 7):
                bullet = Bullet(0, 1)
                bullet.injury = 1
                bullet.rect.centerx = self.rect.centerx
                bullet.rect.y = self.rect.bottom
                if j == 2: #控制子弹是否水平移动
                    bullet.speedx = 0
                else:
                    bullet.speedx = (-1) ** j * ((j - 1) // 2) * 1

                self.bullets.add(bullet) #加入子弹精灵组

    def update(self):
        self.music_fly.play() #播放飞行音乐
        global SCORE
        if self.index4 % 2 == 0: #控制飞行距离
            if self.index3 % 50 == 0 and (self.index3 // 50) % 2 == 1: #控制飞行方向
                self.speedx = -self.speedx
            self.rect.x += self.speedx
            self.index3 += 1
        self.index4 += 1

        self.image = pygame.image.load("./images/enemy3_n" + str((self.index1 // 6) % 2 + 1) + ".png") #发电动画
        self.index1 += 1

        if self.isboom:
            self.bar.length -= self.injury * self.bar.weight #血量减少
            if self.bar.length <= 0: #Boss死亡
                self.music_fly.stop() #Boss飞行音乐暂停
                if self.index2 == 0:
                    self.music_boom.play() #Boss爆炸音乐响一次
                if self.index2 < 29:
                    self.image = pygame.image.load("./images/enemy3_down" + str(self.index2 // 7) + ".png") #播放爆炸动画
                    self.index2 += 1
                else:
                    self.kill() #清除Boss
                    SCORE += self.bar.value * 10 #分数增加
            else:
                self.isboom = False


class Enemy(GameSprite): #敌机游戏精灵

    def __init__(self, num=1):
        self.number = num #敌机类型编号
        super().__init__("./images/enemy" + str(num) + ".png")

        if num == 1: #加载不同类型敌机爆炸音乐
            self.music_boom = pygame.mixer.Sound("./music/enemy1_down.wav")
        else:
            self.music_boom = pygame.mixer.Sound("./music/enemy2_down.wav")
        self.speedy = random.randint(1, 3) #随机初始化垂直移动距离

        self.rect.bottom = 0
        max_x = SCREEN_RECT.width - self.rect.width
        self.rect.x = random.randint(0, max_x) #随机初始化位置

        self.isboom = False
        self.index = 0

        if self.number == 1: #不同类型敌机血量不同
            self.bar = bloodline(color_blue, self.rect.x, self.rect.y, self.rect.width)
        else:
            self.bar = bloodline(color_blue, self.rect.x, self.rect.y, self.rect.width, 3, 4)

        self.bullets = pygame.sprite.Group()

    def fire(self):
        for i in range(0, 2):
            bullet = Bullet(0, random.randint(self.speedy + 1, self.speedy + 3))
            bullet.rect.bottom = self.rect.bottom + i * 20 #使子弹位置有先后顺序
            bullet.rect.centerx = self.rect.centerx

            self.bullets.add(bullet)

    def update(self):
        global SCORE
        super().update()

        if self.rect.y > SCREEN_RECT.height: #飞出屏幕范围，直接删除
            self.kill()
            self.bar.length = 0

        if self.isboom:
            self.bar.length -= self.bar.weight * self.injury
            if self.bar.length <= 0:
                if self.index == 0:
                    self.music_boom.play()
                if self.index < 17:
                    self.image = pygame.image.load(
                        "./images/enemy" + str(self.number) + "_down" + str(self.index // 4) + ".png")
                    self.index += 1
                else:
                    self.kill()
                    SCORE += self.bar.value * 10
            else:
                self.isboom = False


class Hero(GameSprite): #英雄游戏精灵

    def __init__(self):
        super().__init__("./images/me1.png")
        self.music_down = pygame.mixer.Sound("./music/me_down.wav")
        self.music_upgrade = pygame.mixer.Sound("./music/upgrade.wav")
        self.music_degrade = pygame.mixer.Sound("./music/supply.wav")

        self.number = 0 #英雄精灵编号
        self.rect.centerx = SCREEN_RECT.centerx
        self.rect.bottom = SCREEN_RECT.bottom - 120

        self.bullets = pygame.sprite.Group()
        self.isboom = False
        self.index1 = 1
        self.index2 = 0
        self.buff1_num = 0 #子弹buff数量
        self.bar = bloodline(color_green, 0, 700, 480, 8, 10)
        self.bomb = 0 #全屏炸弹数量

    def update(self):

        self.rect.y += self.speedy
        self.rect.x += self.speedx

        if self.rect.x < 0: #控制英雄位置不能超出屏幕
            self.rect.x = 0
        elif self.rect.right > SCREEN_RECT.right:
            self.rect.right = SCREEN_RECT.right
        elif self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.bottom > SCREEN_RECT.bottom:
            self.rect.bottom = SCREEN_RECT.bottom

        self.image = pygame.image.load("./images/me" + str((self.index1 // 6) % 2 + 1) + ".png") #喷气动画
        self.index1 += 1

        if self.isboom:
            self.bar.length -= self.injury * self.bar.weight
            if self.bar.length <= 0:
                if self.index2 == 0:
                    self.music_down.play()
                if self.index2 < 17:
                    self.image = pygame.image.load("./images/me_destroy_" + str(self.index2 // 4) + ".png") #控制动画播放速度
                    self.index2 += 1
                else:
                    self.kill()
            else:
                self.isboom = False

    def fire(self): #根据子弹buff数量发射不同数量和不同类型的子弹
        if self.buff1_num == 0:
            for i in range(0, 1):
                bullet = Bullet()

                bullet.rect.bottom = self.rect.y - i * 20
                bullet.rect.centerx = self.rect.centerx

                self.bullets.add(bullet)
        elif self.buff1_num <= 4:
            for i in range(0, 1):
                for j in range(2, self.buff1_num + 3):
                    bullet = Bullet(2, -3)
                    bullet.rect.bottom = self.rect.y - i * 20
                    if (self.buff1_num % 2 == 1):
                        bullet.rect.centerx = self.rect.centerx + (-1) ** j * 15 * (j // 2)
                    if (self.buff1_num % 2 == 0):
                        if j == 2:
                            bullet.rect.centerx = self.rect.centerx
                        else:
                            bullet.rect.centerx = self.rect.centerx + (-1) ** j * 15 * ((j - 1) // 2)
                    self.bullets.add(bullet)
        elif self.buff1_num >= 5:
            for i in range(0, 1):
                for j in range(2, 5):
                    bullet = Bullet(3, -3)
                    bullet.injury = 2
                    bullet.rect.bottom = self.rect.y
                    if j == 2:
                        bullet.rect.centerx = self.rect.centerx
                    else:
                        bullet.rect.centerx = self.rect.centerx + (-1) ** j * (30 + 5 * i)
                        bullet.speedx = (-1) ** j * (i + 1)
                    self.bullets.add(bullet)


class Heromate(Hero): #附加英雄精灵
    def __init__(self, num):
        super().__init__()
        self.image = pygame.image.load("./images/life.png")
        self.number = num

    def update(self):

        if self.rect.right > SCREEN_RECT.right:
            self.rect.right = SCREEN_RECT.right
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.bottom > SCREEN_RECT.bottom:
            self.rect.bottom = SCREEN_RECT.bottom

    def fire(self):
        for i in range(0, 1, 2):
            bullet = Bullet()
            bullet.rect.bottom = self.rect.y - i * 20
            bullet.rect.centerx = self.rect.centerx
            self.bullets.add(bullet)


class Bullet(GameSprite): #子弹精灵

    def __init__(self, color=1, speedy=-2, speedx=0):
        self.hity = color
        self.music_shoot = pygame.mixer.Sound("./music/bullet.wav")
        self.music_shoot.set_volume(0.4)
        if color > 0:
            self.music_shoot.play()
        super().__init__("./images/bullet" + str(color) + ".png", speedy, speedx)

    def update(self):
        super().update()

        if self.rect.bottom < 0 or self.rect.y > 700:
            self.kill()


class Buff1(GameSprite): #子弹Buff精灵
    def __init__(self):
        super().__init__("./images/bullet_supply.png", 1)
        self.music_get = pygame.mixer.Sound("./music/get_bullet.wav")
        self.rect.bottom = 0
        max_x = SCREEN_RECT.width - self.rect.width
        self.rect.x = random.randint(0, max_x)

    def update(self):
        super().update()
        if self.rect.bottom < 0:
            self.kill()


class Buff2(GameSprite): #炸弹Buff精灵
    def __init__(self):
        super().__init__("./images/bomb_supply.png", 2)
        self.music_get = pygame.mixer.Sound("./music/get_bomb.wav")
        self.rect.bottom = random.randint(0, 700)
        max_x = SCREEN_RECT.width - self.rect.width
        self.rect.x = random.randint(0, max_x)
        self.ran = random.randint(60, 180)

    def update(self):
        super().update()
        if self.rect.bottom < 0 or self.index == self.ran:
            self.kill()
        self.index += 1

class Buff3(Buff2): #加血Buff精灵
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("./images/buff3.png")
        self.speedy=3


class bloodline(object): #血条游戏精灵
    def __init__(self, color, x, y, length, width=2, value=2):
        self.color = color #血条颜色
        self.x = x
        self.y = y
        self.length = length #血条长度
        self.width = width #血条宽度
        self.value = value * 1.0 #浮点数表示血量
        self.weight = length / value #1滴血表示的长度
        self.color_init = color #血条初始颜色

    def update(self, canvas):
        if self.length <= self.value * self.weight / 2: #血量小于警戒值
            self.color = color_red
        else:
            self.color = self.color_init
        self.bar_rect = pygame.draw.line(canvas, self.color, (self.x, self.y), (self.x + self.length, self.y),
                                         self.width) #显示血条


class CanvasOver(): #结束页类
    def __init__(self, screen):
        self.img_again = pygame.image.load("./images/again.png")
        self.img_over = pygame.image.load("./images/gameover.png")
        self.rect_again = self.img_again.get_rect()
        self.rect_over = self.img_over.get_rect()
        self.rect_again.centerx = self.rect_over.centerx = SCREEN_RECT.centerx
        self.rect_again.bottom = SCREEN_RECT.centery
        self.rect_over.y = self.rect_again.bottom + 20
        self.screen = screen #显示屏幕

    def event_handler(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN: #鼠标按键判断
            pos = pygame.mouse.get_pos()
            if self.rect_again.left < pos[0] < self.rect_again.right and \
                    self.rect_again.top < pos[1] < self.rect_again.bottom:
                return 1 #重新开始
            elif self.rect_over.left < pos[0] < self.rect_over.right and \
                    self.rect_over.top < pos[1] < self.rect_over.bottom:
                return 0 #结束游戏

    def update(self):
        global HIGH_SCORE
        
        if HIGH_SCORE < SCORE:
            HIGH_SCORE = SCORE
        self.screen.blit(self.img_again, self.rect_again)
        self.screen.blit(self.img_over, self.rect_over)
        score_font = pygame.font.Font("./typeface.ttf", 50)
        image = score_font.render("SCORE:" + str(int(SCORE)), True, color_gray) #创建分数
        rect = image.get_rect()
        high_image = score_font.render("HIGH SCORE:" + str(int(HIGH_SCORE)), True, color_gray) #创建游戏最高分
        high_rect = high_image.get_rect()
        rect.centerx, rect.bottom = SCREEN_RECT.centerx, self.rect_again.top - 20
        self.screen.blit(image, rect) #显示分数
        high_rect.centerx, high_rect.bottom = SCREEN_RECT.centerx, rect.top - 20
        self.screen.blit(high_image, high_rect) #显示游戏最高分
                    

class PlaneGame(object): #飞机大战主程序类

    def __init__(self):

        self.screen = pygame.display.set_mode(SCREEN_RECT.size)
        self.canvas_over = CanvasOver(self.screen)
        self.clock = pygame.time.Clock() #计算程序运行时间
        self.__create_sprites() #创建各种精灵和精灵组
        self.score = GameScore()
        self.index = 0
        pygame.mixer.music.load("./music/game_music.ogg") #背景音乐
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1) #循环播放
        self.paused = False #停止状态
        self.game_over = False #结束状态
        self.pause_nor_image = pygame.image.load("images/pause_nor.png")
        self.pause_pressed_image = pygame.image.load("images/pause_pressed.png")
        self.resume_nor_image = pygame.image.load("images/resume_nor.png")
        self.resume_pressed_image = pygame.image.load("images/resume_pressed.png")
        self.pause_rect = self.pause_nor_image.get_rect()
        self.pause_rect.left, self.pause_rect.top = SCREEN_RECT.width - self.pause_rect.width - 10, 10
        self.pause_image = self.pause_nor_image
        
        pygame.time.set_timer(CREATE_ENEMY_EVENT, random.randint(1000, 2000)) #设置事件发生时间
        self.enemy_speed_up = True
        pygame.time.set_timer(HERO_FIRE_EVENT, 400)
        pygame.time.set_timer(BUFF1_SHOW_UP, random.randint(10000, 20000))
        pygame.time.set_timer(BUFF2_SHOW_UP, random.randint(20000, 40000))
        pygame.time.set_timer(ENEMY_FIRE_EVENT, 2000)

    def __create_sprites(self): #创建各种精灵和精灵组

        bg1 = Background()
        bg2 = Background(True)

        self.back_group = pygame.sprite.Group(bg1, bg2)

        self.enemy_group = pygame.sprite.Group()

        self.hero = Hero()
        self.hero_group = pygame.sprite.Group(self.hero)

        self.enemy_bullet_group = pygame.sprite.Group()

        self.bars = []
        self.bars.append(self.hero.bar)

        self.buff1_group = pygame.sprite.Group()

        self.enemy_boom = pygame.sprite.Group()

        self.bombs = []

    def start_game(self): #开始游戏
        while True:
            if self.paused: #判断是否暂停
                pygame.mixer.music.pause() #暂停背景音乐
                pygame.mixer.stop() #暂停所有音乐
            else:
                pygame.mixer.music.unpause() #播放背景音乐
            
            self.clock.tick(FRAME_PER_SEC) #设置刷新频率
            self.__event_handler() #事件监测
            self.__check_collide() #碰撞检测
            self.__update_sprites() #更新各个精灵和精灵组

            if self.game_over:
                self.canvas_over.update() #游戏结束更新

            pygame.display.update() #刷新屏幕

    def __event_handler(self): #事件监测

        if self.score.getvalue() > 2000+5000*self.index: #Boss出现
            self.boss = Boss()
            self.enemy_group.add(self.boss)
            self.bars.append(self.boss.bar)
            self.index += 1

        if self.score.getvalue() > 1000 and self.enemy_speed_up: #敌机增多
                pygame.time.set_timer(CREATE_ENEMY_EVENT, random.randint(500, 1000))
                self.enemy_speed_up = False
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #退出游戏
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.pause_rect.collidepoint(event.pos): #暂停游戏
                    self.paused = not self.paused
            elif event.type == pygame.MOUSEMOTION:
                if self.pause_rect.collidepoint(event.pos):
                    if self.paused:
                        self.pause_image = self.resume_pressed_image
                    else:
                        self.pause_image = self.pause_pressed_image
                else:
                    if self.paused:
                        self.pause_image = self.resume_nor_image
                    else:
                        self.pause_image = self.pause_nor_image
            if not self.paused:
                if event.type == CREATE_ENEMY_EVENT: #创建敌机
                    if self.score.getvalue() < 200:
                        enemy = Enemy()
                    else:
                        if random.randint(0, 100) % 4:
                            enemy = Enemy()
                        else:
                            enemy = Enemy(2)

                    self.enemy_group.add(enemy)
                    self.bars.append(enemy.bar)

                elif event.type == HERO_FIRE_EVENT: #英雄开火
                    for hero in self.hero_group:
                        hero.fire()
                elif event.type == BUFF1_SHOW_UP: #子弹buff出现
                    buff1 = Buff1()
                    self.buff1_group.add(buff1)
                elif event.type == BUFF2_SHOW_UP: #根据情况出现炸弹buff或者加血buff
                    if self.hero.bar.color == color_red:
                        buff = Buff3()
                    else:
                        buff= Buff2()
                    self.buff1_group.add(buff)
                elif event.type == ENEMY_FIRE_EVENT: #敌机开火
                    for enemy in self.enemy_group:
                        if enemy.number >= 2:
                            enemy.fire()
                            for bullet in enemy.bullets:
                                self.enemy_bullet_group.add(bullet)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: #发射全屏炸弹
                    self.bomb_throw()
                else:
                    if self.game_over == True:
                        flag = self.canvas_over.event_handler(event) #判断是否结束游戏
                        if flag == 1:
                            self.__start__()
                        elif flag == 0:
                            pygame.quit()
                            sys.exit()
                        
                keys_pressed = pygame.key.get_pressed() #监测键盘按键状态
                if keys_pressed[pygame.K_RIGHT]:
                    self.heros_move(5)
                elif keys_pressed[pygame.K_LEFT]:
                    self.heros_move(-5)
                elif keys_pressed[pygame.K_UP]:
                    self.heros_move(0, -5)
                elif keys_pressed[pygame.K_DOWN]:
                    self.heros_move(0, 5)
                else:
                    self.heros_move(0, 0)

    def heros_move(self, x=0, y=0): #英雄移动距离
        self.hero.speedx = x
        self.hero.speedy = y

    def bomb_throw(self): #全屏炸弹爆炸
        music_use_bomb = pygame.mixer.Sound("./music/use_bomb.wav")
        if self.hero.bomb > 0:
            music_use_bomb.play()
            self.hero.bomb -= 1
            self.bombs.pop()
            for enemy in self.enemy_group:
                if enemy.number < 3:
                    enemy.bar.length = 0
                    enemy.isboom = True
                else:
                    enemy.injury = 20
                    enemy.isboom = True

    def __check_collide(self): #碰撞检测
        if not self.paused:
            for enemy in self.enemy_group:
                for hero in self.hero_group:
                    for bullet in hero.bullets:
                        if pygame.sprite.collide_mask(bullet, enemy): #子弹敌机碰撞
                            bullet.kill()
                            enemy.injury = bullet.hity
                            enemy.isboom = True
                            if enemy.bar.length <= 0:
                                self.enemy_group.remove(enemy)
                                self.enemy_boom.add(enemy)

            for enemy in self.enemy_group:
                if pygame.sprite.collide_mask(self.hero, enemy): #英雄敌机碰撞
                    if enemy.number < 3:
                        enemy.bar.length = 0
                        self.hero.injury = self.hero.bar.value / 4
                        if self.hero.buff1_num > 0:
                            self.hero.buff1_num -= 1
                            self.hero.music_degrade.play()
                        self.enemy_group.remove(enemy)
                        self.enemy_boom.add(enemy)
                        enemy.isboom = True
                    else:
                        self.hero.bar.length = 0
                    self.hero.isboom = True

            for bullet in self.enemy_bullet_group:
                if pygame.sprite.collide_mask(self.hero, bullet): #英雄子弹碰撞
                    bullet.kill()
                    self.hero.injury = 1
                    if self.hero.buff1_num > 0:
                        self.hero.music_degrade.play()
                        if self.hero.buff1_num == 6: #删除附加英雄
                            self.mate1.kill()
                            self.mate2.kill()
                        self.hero.buff1_num -= 1

                    self.hero.isboom = True

            if not self.hero.alive(): #英雄死亡
                self.hero.rect.right = -10
                if self.hero.buff1_num == 6:
                    self.mate1.rect.right = -10
                    self.mate2.rect.right = -10
                self.game_over = True

            for buff in self.buff1_group: #根据buff增强效果
                if pygame.sprite.collide_mask(self.hero, buff): #英雄吸收buff
                    buff.music_get.play()
                    if buff.speedy == 1:
                        if self.hero.buff1_num < 7:
                            self.hero.buff1_num += 1
                            self.hero.music_upgrade.play()
                            if self.hero.buff1_num == 6:
                                self.team_show()

                    elif buff.speedy==2:
                        self.hero.bomb += 1
                        image = pygame.image.load("./images/bomb.png")
                        self.bombs.append(image)
                    elif buff.speedy==3:
                        if self.hero.bar.length < self.hero.bar.weight*self.hero.bar.value:
                            self.hero.bar.length += self.hero.bar.weight*self.hero.bar.value
                    buff.kill()

    def team_show(self): #创建附加英雄
        self.mate1 = Heromate(-1)
        self.mate2 = Heromate(1)
        self.mate1.image = pygame.image.load("./images/life.png")
        self.mate1.rect = self.mate1.image.get_rect()
        self.mate2.image = pygame.image.load("./images/life.png")
        self.mate2.rect = self.mate2.image.get_rect()
        self.hero_group.add(self.mate1)
        self.hero_group.add(self.mate2)

    def __update_sprites(self): #各种更新
        
        self.back_group.draw(self.screen)
        self.pause_show()
        
        if not self.paused:
            self.back_group.update()
            
            self.enemy_group.update()
            self.enemy_group.draw(self.screen)

            self.enemy_boom.update()
            self.enemy_boom.draw(self.screen)

            self.heros_update()
            self.hero_group.draw(self.screen)

            for hero in self.hero_group:
                hero.bullets.update()
                hero.bullets.draw(self.screen)

            self.buff1_group.update()
            self.buff1_group.draw(self.screen)

            self.bars_update()
            self.bombs_update()

            self.enemy_bullet_group.update()
            self.enemy_bullet_group.draw(self.screen)
            
            self.score_show()

    def heros_update(self): #英雄更新
        for hero in self.hero_group:
            if hero.number == 1:
                hero.rect.bottom = self.hero.rect.bottom
                hero.rect.left = self.hero.rect.right
            if hero.number == -1:
                hero.rect.bottom = self.hero.rect.bottom
                hero.rect.right = self.hero.rect.left
            hero.update()

    def bars_update(self): #血条更新
        for bar in self.bars:
            if bar.length > 0:
                bar.update(self.screen)
            else:
                self.bars.remove(bar)

    def bombs_update(self): #炸弹更新
        i = 1
        for bomb in self.bombs:
            self.screen.blit(bomb, (0, 700 - (bomb.get_rect().height) * i))
            i += 1

    def score_show(self): #显示分数
        score_font = pygame.font.Font("./typeface.ttf", 33)
        image = score_font.render("SCORE:" + str(int(self.score.getvalue())), True, color_gray)
        rect = image.get_rect()
        rect.top, rect.left = 0, 0
        self.screen.blit(image, rect)

    def pause_show(self): #显示暂停
        pause_font = pygame.font.Font("./typeface.ttf", 60)
        image = pause_font.render("Pausing...", True, color_gray)
        rect = image.get_rect()
        rect.centerx, rect.bottom = SCREEN_RECT.centerx, 350
        if self.paused and not self.game_over:
            self.screen.blit(image, rect)
        self.screen.blit(self.pause_image, self.pause_rect)

    def __start__(self): #启动游戏
        global SCORE
        SCORE = 0

        self.__init__()
        self.start_game()


if __name__ == '__main__':
    planegame = PlaneGame() #初始化对象
    planegame.__start__()
