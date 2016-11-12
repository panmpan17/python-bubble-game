import pygame
from color import Color

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
        pos1 = None
        pos2 = self[-1]
        for n, p in enumerate(self):
            pos1 = pos2
            pos2 = p

            ny, m, n = self.a(pos1, pos2)
            f = "{}y = {}x + {}"
            print(f.format(ny, m, n))
        print()

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

    def loadimg(self, img):
        self.img = img

    def draw(self, window):
        if len(self.img) > 0:
            points = []
            for p in self.img:
                points.append((p[0] * (self.size / 400) + self.x, p[1] * (self.size / 400) + self.y))
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
    def __init__(self, blocks=[], img=[], pos=(0, 0), size=400, border=0, color=Color.white, gravityaffect=True):
        super(Role, self).__init__(img, pos, size, border, color)

        self.blocks = blocks
        self.facing = 1
        self.gravity = 0
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

class Enemy(Role):
    def __init__(self, blocks=[], img=[], pos=(0, 0), size=400, border=0, color=Color.white, gravityaffect=True):
        super(Enemy, self).__init__(blocks=blocks, img=img, pos=pos, size=size, border=border, color=color, gravityaffect=gravityaffect)

        self.v = 1
        self.jump = 40

    def draw(self, window):

        if self.x <= self.xrestrict[0] + 5:
            self.v = 1
        elif self.x + self.size  >= self.xrestrict[1] - 5:
            self.v = -1

        self.move((self.v * 6, 0))

        self.jump -= 1

        if self.jump < 0:
            self.gravity = -30
            self.jump = 40

        super(Enemy, self).draw(window)

class App:
    def __init__(self):
        pass

    def run(self):
        pygame.init()

        self.window = pygame.display.set_mode((500, 500))
        pygame.display.set_caption(" Game ")
        clock = pygame.time.Clock()
        pygame.key.set_repeat(1, 2)

        images = {
            "role": Image("role.pgi"),
            "bubble": Image("bubble.pgi"),
            "enemy": Image("enemy.pgi"),
            }

        blocks = Blocks()
        blocks.addblock((0, 400), (200, 430))
        blocks.addblock((300, 300), (500, 330))
        blocks.addblock((0, 200), (200, 230))
        blocks.addblock((300, 100), (500, 130))

        role = Role(img=images["role"], blocks=blocks, size=50, border=5, color=Color.orange)
        role.set_restrict(xrestrict=(0, 500), yrestrict=(0, 500))

        enemy = Enemy(img=images["enemy"], blocks=blocks, size=50, border=0, color=Color.white, pos=(450, 0))
        enemy.set_restrict(xrestrict=(0, 500), yrestrict=(0, 500))

        bubbles = []
        keycoldown = {}
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()

                    if (keys[pygame.K_LMETA] or keys[pygame.K_LCTRL]) and keys[pygame.K_q]:
                        self.stop()

                    if keys[pygame.K_a]:
                        role.move((-9, 0))
                    elif keys[pygame.K_d]:
                        role.move((9, 0))
                    if keys[pygame.K_w]:
                        if pygame.K_w not in keycoldown:
                            keycoldown[pygame.K_w] = 30
                            role.gravity = -30

                    if keys[pygame.K_SPACE]:
                        if pygame.K_SPACE not in keycoldown:
                            keycoldown[pygame.K_SPACE] = 6
                            if len(bubbles) < 20:
                                x, y = role.x, role.y
                                bubbles.append(Bubble(role.facing, img=images["bubble"], pos=(x, y), size=30))
                                bubbles[-1].set_restrict(xrestrict=(0, 500), yrestrict=(0, 500))

            if len(keycoldown) != 0:
                for k in list(keycoldown.keys()):
                    keycoldown[k] -= 1
                    if keycoldown[k] == -1:
                        keycoldown.pop(k)

            self.window.fill(Color.black)
            for b in bubbles:
                b.draw(self.window)
                if b.stay < 0:
                    bubbles.remove(b)
            enemy.draw(self.window)
            blocks.draw(self.window)
            role.draw(self.window)
            pygame.display.flip()

            clock.tick(30)

    def stop(self):
        pygame.quit()
        exit()

if __name__ == "__main__":
    app = App()
    app.run()


