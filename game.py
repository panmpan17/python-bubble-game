import pygame
from color import Color
from pprint import pprint
from random import randint

class Blocks(list):
    def addblock(self, pos1, pos2):
        b = pos1
        b += (pos2[0] - pos1[0], pos2[1] - pos1[1])
        self.append(b)

    def draw(self, window):
        for b in self:
            pygame.draw.rect(window, Color.red, b, 2)

class Image(list):
    def __init__(self, path):
        super(Image, self).__init__()
        with open(path) as file:
            r = file.read()
            l = r.split("|")
            for i in l:
                x, y = i.split(",")
                self.append((int(x), int(y)))

        self.findborderpoints()

    def findborderpoints(self):
        equations = []
        pos1 = None
        pos2 = self[-1]
        for n, p in enumerate(self):
            pos1 = pos2
            pos2 = p

            equations.append(((pos1, pos2, self.a(pos1, pos2))))

        test = set()
        for e in equations:
            ny, m, n = e[2]
            if ny == 0:
                step = 1
                if e[1][1] < e[0][1]:
                    step = -1
                x = int(n / -m)
                for y in range(e[0][1], e[1][1], step):
                    test.add((x, y))
            elif m == 0:
                step = 1
                if e[1][0] < e[0][0]:
                    step = -1
                y = n
                for x in range(e[0][0], e[1][0], step):
                    test.add((x, y))
            else:
                step = 1
                if e[1][1] < e[0][1]:
                    step = -1
                for y in range(e[0][1], e[1][1], step):
                    x = int((n - y) / -m)
                    test.add((x, y))

        self.points = test

    def a(self, pos1, pos2):
        ny, m, n = None, None, None
        if pos1[0] == pos2[0]:
            ny = 0
            m = -1
            n = pos1[0]
            return ny, m, n
        else:
            ny = 1

            dis_x = pos2[0] - pos1[0]
            dis_y = pos2[1] - pos1[1]
            m = dis_y / dis_x

            n = pos1[1] - m * pos1[0]
            return ny, m, n

class Sprite:
    def __init__(self, img, pos, size, border, color):
        self.img = img
        self.x, self.y = pos
        self.size = size
        self.border = border
        self.color = color
        self.xrestrict = None
        self.yrestrict = None
        self.id = str(randint(1, 1000))
        self.detect = {"x": None, "y": None}

    def loadimg(self, img):
        self.img = img

    def draw(self, window, color=None):
        if len(self.img) > 0:
            points = []
            for p in self.img:
                x = int(p[0] * (self.size / 400) + self.x)
                y = int(p[1] * (self.size / 400) + self.y)
                points.append((x, y))
            if color != None:
                pygame.draw.polygon(window, color, points, self.border)
                return 
            pygame.draw.polygon(window, self.color, points, self.border)

    def setsize(self, size):
        self.size = size

    def setpos(self, pos):
        x, y = pos
        if self.xrestrict:
            if x < self.xrestrict[0]:
                x = self.xrestrict[0]
            if x + self.size > self.xrestrict[1]:
                x = self.xrestrict[1] - self.size

        if self.yrestrict:
            if y < self.yrestrict[0]:
                y = self.yrestrict[0]
            if y + self.size > self.yrestrict[1]:
                y = self.yrestrict[1] - self.size

        self.x, self.y = x, y

    def set_restrict(self, xrestrict=None, yrestrict=None):
        if xrestrict:
            self.xrestrict = xrestrict
        if yrestrict:
            self.yrestrict = yrestrict

    def move(self, vecter):
        if vecter[0] > 0:
            self.facing = 1
        elif vecter[0] < 0:
            self.facing = -1
        x = self.x + vecter[0]
        y = self.y + vecter[1]

        self.setpos((x, y))

    def detectcollision(self, sprites):
        for s in sprites:
            dis_x = (s.x - self.x) ** 2
            dis_y = (s.y - self.y) ** 2
            dis = (dis_x + dis_y) ** 0.5
            if dis < self.size + s.size:
                if self.detect["x"] != self.x or self.detect["y"] != self.y:
                    self.detect.clear()
                    self.detect["x"] = self.x
                    self.detect["y"] = self.y
                    for p in self.img.points:
                        x = int(p[0] * (self.size / 400) + self.x)
                        y = int(p[1] * (self.size / 400) + self.y)
                        if (x, y) not in self.detect:
                            self.detect[(x, y)] = 1
                for s in sprites:
                    if (s.id not in self.detect):
                        self.detect[s.id + "x"] = s.x
                        self.detect[s.id + "y"] = s.y
                        for p in s.img.points:
                            x = int(p[0] * (s.size / 400) + s.x)
                            y = int(p[1] * (s.size / 400) + s.y)
                            if (x, y) in self.detect:
                                self.detect[s.id] = s.id
                                return s.id
                        self.detect[s.id] = False
                        return False

                    if self.detect[s.id + "x"] != s.x or self.detect[s.id + "y"] != s.y:
                        self.detect[s.id + "x"] = s.x
                        self.detect[s.id + "y"] = s.y
                        for p in s.img.points:
                            x = int(p[0] * (s.size / 400) + s.x)
                            y = int(p[1] * (s.size / 400) + s.y)
                            if (x, y) in self.detect:
                                self.detect[s.id] = s.id
                                return s.id
                        self.detect[s.id] = False
                        return False

                    return self.detect[s.id]

class Bubble(Sprite):
    def __init__(self, direction, img=[], pos=(0, 0), size=400, border=0):
        super(Bubble, self).__init__(img, pos, size, border, Color.random(minc=50, maxc=220))

        self.direction = direction
        self.shoot = 20
        self.stay = 200
        self.set_restrict(xrestrict=(0, 500), yrestrict=(0, 500))

    def draw(self, window):
        if self.shoot:
            self.move((self.direction * 9, 0))
            self.shoot -= 1
            if self.shoot < 0:
                self.shoot = False
        else:
            self.move((0, -5))
            self.stay -= 1

        super(Bubble, self).draw(window)

class Role(Sprite):
    def __init__(self, blocks=[], img=[], pos=(0, 0), size=400, border=0, color=Color.white, gravityaffect=True, live=3):
        super(Role, self).__init__(img, pos, size, border, color)

        self.blocks = blocks
        self.live = live
        self.facing = 1
        self.gravity = 0
        self.invincible = 0
        self.gravityaffect = gravityaffect

    def move(self, vecter):
        super(Role, self).move(vecter)

        touched = self.is_touchground()
        if touched:
            self.y = touched
            self.gravity = 0

    def draw(self, window, tick=30):
        if self.gravityaffect:
            self.gravity += 0.098 / (1 / tick)
            self.move((0, self.gravity))

        if self.invincible > 0:
            super(Role, self).draw(window, color=Color.gray)
            self.invincible -= 1
            return 

        super(Role, self).draw(window)

    def is_touchground(self):
        footy = self.y + self.size
        
        if self.yrestrict:
            if footy >= self.yrestrict[1]:
                return self.yrestrict[1] - self.size

        for b in self.blocks:
            if footy >= b[1] and footy <= b[1] + b[3]:
                if self.x >= b[0] and self.x <= b[0] + b[2]:
                    return b[1] - self.size

                bodyside = self.x + self.size
                if bodyside >= b[0] and bodyside <= b[0] + b[2]:
                    return b[1] - self.size
        return False

    def die(self):
        if self.invincible == 0:
            self.live -= 1
            if self.live < 0 and self.invincible == 0:
                print("dead")
            self.invincible = 150

class Enemy(Role):
    def __init__(self, blocks=[], img=[], pos=(0, 0), size=400, border=0, color=Color.white, gravityaffect=True):
        super(Enemy, self).__init__(blocks=blocks, img=img, pos=pos, size=size, border=border, color=color, gravityaffect=gravityaffect)

        self.v = 1
        self.jump = 40
        self.live = 0
        self.wraped = 0
        self.bubble = []

    def draw(self, window):
        self.chaseplayer()

        super(Enemy, self).draw(window)

    def chaseplayer(self):
        if self.x <= self.xrestrict[0] + 5:
            self.v = 1
        elif self.x + self.size  >= self.xrestrict[1] - 5:
            self.v = -1

        self.move((self.v * 4, 0))

    def wrapup(self):
        self.wraped += 150
        self.gravity = 0
        self.gravityaffect = False
        self.bubble = Image("bubble.pgi")

    def is_touchground(self):
        footy = self.y + self.size
        
        if self.yrestrict:
            if footy >= self.yrestrict[1]:
                return self.yrestrict[1] - self.size

        if self.wraped == 0:
            for b in self.blocks:
                if footy >= b[1] and footy <= b[1] + b[3]:
                    if self.x >= b[0] and self.x <= b[0] + b[2]:
                        return b[1] - self.size

                    bodyside = self.x + self.size
                    if bodyside >= b[0] and bodyside <= b[0] + b[2]:
                        return b[1] - self.size
        return False

    def draw_bubble(self, window):
        self.wraped -= 1
        self.move((0, -5))

        if self.wraped == 0:
            self.gravityaffect = True
            return

        if len(self.bubble) > 0:
            points = []
            for p in self.bubble:
                x = int(p[0] * (self.size / 400) + self.x)
                y = int(p[1] * (self.size / 400) + self.y)
                points.append((x, y))
            pygame.draw.polygon(window, Color.red, points, self.border)
        
        if len(self.img) > 0:
            points = []
            for p in self.img:
                x = int(p[0] * ((self.size - 20) / 400) + self.x + 10)
                y = int(p[1] * ((self.size - 20) / 400) + self.y + 10)
                points.append((x, y))
            pygame.draw.polygon(window, self.color, points, self.border)

class App:
    def __init__(self):
        self.images = {
            "player": Image("role.pgi"),
            "bubble": Image("bubble.pgi"),
            "enemy": Image("enemy.pgi"),
            }

        self.blocks = Blocks()
        self.blocks.addblock((0, 400), (200, 430))
        self.blocks.addblock((300, 300), (500, 330))
        self.blocks.addblock((300, 200), (500, 230))
        self.blocks.addblock((300, 100), (500, 130))

        self.player = Role(img=self.images["player"], blocks=self.blocks, size=50, border=5, color=Color.orange)
        self.player.set_restrict(xrestrict=(0, 500), yrestrict=(0, 500))

        self.enemys = []
        self.enemys.append(Enemy(img=self.images["enemy"], blocks=self.blocks, size=50, border=0, color=Color.white, pos=(450, 10)))
        self.enemys[-1].set_restrict(xrestrict=(0, 500), yrestrict=(0, 500))

    def run(self):
        pygame.init()

        self.window = pygame.display.set_mode((500, 500))
        pygame.display.set_caption(" Game ")
        clock = pygame.time.Clock()
        pygame.key.set_repeat(1, 2)

        self.bubbles = []
        self.keycoldown = {}
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if (keys[pygame.K_LMETA] or keys[pygame.K_LCTRL]) and keys[pygame.K_q]:
                        self.stop()

                    self.handle_player_control(keys)

            if len(self.keycoldown) != 0:
                for k in list(self.keycoldown.keys()):
                    self.keycoldown[k] -= 1
                    if self.keycoldown[k] == -1:
                        self.keycoldown.pop(k)

            d = self.player.detectcollision(self.enemys)
            if d:
                for e in self.enemys:
                    if e.wraped == 0:
                        self.player.die()
                    else:
                        self.enemys.remove(e)

            self.window.fill(Color.black)

            self.handle_enemy()
            self.handle_bubble()
            self.blocks.draw(self.window)
            self.player.draw(self.window)
            pygame.display.flip()

            clock.tick(30)

    def handle_player_control(self, keys):
        if keys[pygame.K_a]:
            self.player.move((-9, 0))
        elif keys[pygame.K_d]:
            self.player.move((9, 0))

        if keys[pygame.K_w]:
            if pygame.K_w not in self.keycoldown:
                self.keycoldown[pygame.K_w] = 20
                self.player.gravity = -30

        if keys[pygame.K_SPACE]:
            if pygame.K_SPACE not in self.keycoldown:
                self.keycoldown[pygame.K_SPACE] = 6
                if len(self.bubbles) < 20:
                    x, y = self.player.x, self.player.y
                    self.bubbles.append(Bubble(self.player.facing, img=self.images["bubble"], pos=(x, y), size=30))
                    self.bubbles[-1].set_restrict(xrestrict=(0, 500), yrestrict=(0, 500))

    def handle_bubble(self):
        for b in self.bubbles:
            b.draw(self.window)
            if b.stay < 0:
                self.bubbles.remove(b)
            if b.shoot > 0:
                enemys = [e for e in self.enemys if e.wraped == 0]
                d = b.detectcollision(enemys)
                if d:
                    self.bubbles.remove(b)
                    for e in self.enemys:
                        if e.id == d:
                            e.wrapup()
                            break

    def handle_enemy(self):
        for e in self.enemys:
            if e.wraped > 0:
                e.draw_bubble(self.window)
                continue
            e.draw(self.window)

    def stop(self):
        pygame.quit()
        exit()

if __name__ == "__main__":
    app = App()
    app.run()


