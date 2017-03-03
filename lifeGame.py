#coding: utf-8
import pygame
from pygame.locals import *
import random
import sys
import os
import codecs
from PIL import Image
import numpy as np

SCR_RECT = Rect(0, 0, 480, 760) # screen size
CS = 10 # cell size
NUM_ROW = (SCR_RECT.height-100) / CS # the number of the cell in the field's row
NUM_COL = SCR_RECT.width / CS # the number of the cell in the field's column
DEAD, ALIVE, STAY = 0, 1, 2 # status for live, stay or dead
RAND_LIFE = 0.1

img = np.array(Image.open('data4LifeGame/font.png').convert('L'))

class LifeGame:
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption(u"Conway's Game of Life")
        self.font = pygame.font.SysFont(None, 16)

        # Field and color of its cells that has size of NUM_ROW * NUM_ROL
        # Init with DEAD status
        self.field = [[DEAD for x in range(NUM_COL)] for y in range(NUM_ROW)]
        self.color = [[DEAD for x in range(NUM_COL)] for y in range(NUM_ROW)]

        self.generation = 0 # the number of generation

        self.time = 100

        self.run = False # run or not

        self.cursor = [NUM_COL/2, NUM_ROW/2] # the position of carsor

        # Initiate the life game
        self.clear()

        # main loop
        clock = pygame.time.Clock()
        msg_engine = MessageEngine()
        input_wnd = InputWindow(Rect(0,SCR_RECT.height-100,SCR_RECT.width,100), msg_engine)
        letter = input_wnd.ask(screen, "INPUT A LETTER!")
        while(len(letter) != 1):
            letter = input_wnd.ask(screen, "INPUT A LETTER!")

        input_wnd.draw(screen, "GOOD TO SEE YA! " + letter) 

        self.draw_char(letter)

        while True:
            clock.tick(30)
            self.update()
            self.draw(screen)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    # move cursor by key
                    elif event.key == K_LEFT:
                        self.cursor[0] -= 1
                        if self.cursor[0] < 0: self.cursor[0] = 0
                    elif event.key == K_RIGHT:
                        self.cursor[0] += 1
                        if self.cursor[0] > NUM_COL-1: self.cursor[0] = NUM_COL-1
                    elif event.key == K_UP:
                        self.cursor[1] -= 1
                        if self.cursor[1] < 0: self.cursor[1] = 0
                    elif event.key == K_DOWN:
                        self.cursor[1] += 1
                        if self.cursor[1] > NUM_ROW-1: self.cursor[1] = NUM_ROW-1
                    # turn a cell when pushing space key
                    elif event.key == K_SPACE:
                        x, y = self.cursor
                        if self.field[y][x] == DEAD:
                            self.field[y][x] = ALIVE
                            self.color[y][x] = ALIVE
                        elif self.field[y][x] == ALIVE:
                            self.field[y][x] = DEAD
                    # start simulation when pushing 's' key
                    elif event.key == K_s:
                        self.run = not self.run
                    # progress just one generation by pushing 'n'
                    elif event.key == K_n:
                        self.step()
                    # clear by pushing 'c'
                    elif event.key == K_c:
                        self.clear()
                        self.run = False
                    # add a alive cell randomly by pushing 'r'
                    elif event.key == K_r:
                        self.rand()
                    # Enter a character by pushing 'l'
                    elif event.key == K_l:
                        self.clear()
                        self.run = False
                        letter = input_wnd.ask(screen, "INPUT A LETTER")
                        while(len(letter) != 1):
                            letter = input_wnd.ask(screen, "INPUT A LETTER")
                        input_wnd.draw(screen, "GOOD TO SEE YA! " + letter) 
                        self.draw_char(letter)

                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    # turn a cell by pushing left click
                    px, py = event.pos
                    x, y = px/CS, py/CS
                    self.cursor = [x, y]
                    if self.field[y][x] == DEAD:
                        self.field[y][x] = ALIVE
                        self.color[y][x] = ALIVE
                    elif self.field[y][x] == ALIVE:
                        self.field[y][x] = DEAD
                elif event.type == MOUSEMOTION and event.buttons == (1,0,0):
                    px, py = event.pos
                    x, y = px/CS, py/CS
                    if self.field[y][x] == DEAD:
                        self.field[y][x] = ALIVE
                        self.color[y][x] = ALIVE
                    elif self.field[y][x] == ALIVE:
                        self.field[y][x] = DEAD

    def clear(self):
        """Initiate a game"""
        self.generation = 0
        for y in range(NUM_ROW):
            for x in range(NUM_COL):
                self.field[y][x] = DEAD
    def rand(self):
        """Add a alive cell randomly"""
        for y in range(NUM_ROW):
            for x in range(NUM_COL):
                if random.random() < RAND_LIFE:
                    self.field[y][x] = ALIVE
                    self.color[y][x] = ALIVE
    def update(self):
        pygame.time.wait(200)
        """Update the field"""
        if self.run:
            self.step() # Progress one step
    def step(self):
        """Progress one generation"""
        # next field
        next_field = [[False for x in range(NUM_COL)] for y in range(NUM_ROW)]
        # Set the field by following the rule of life game
        sum_alive_cells = 0
        for y in range(NUM_ROW):
            for x in range(NUM_COL):
                num_alive_cells = self.around(x, y)
                if num_alive_cells == 2:
                    # keep a cell if 2 cells around the cell are alive
                    next_field[y][x] = self.field[y][x]
                    self.color[y][x] = STAY
                    sum_alive_cells += 1
                elif num_alive_cells == 3:
                    # born a cell if 3 cells around the cell are alive
                    next_field[y][x] = ALIVE
                    self.color[y][x] = ALIVE
                    sum_alive_cells += 1
                else:
                    # other cells are dead
                    next_field[y][x] = DEAD
                    self.color[y][x] = DEAD
        self.field = next_field
        self.generation += 1

    def draw(self, screen):
        """Draw the field"""
        # Paint cells
        for y in range(NUM_ROW):
            for x in range(NUM_COL):
                if self.field[y][x] == ALIVE:
                    if(self.color[y][x] == ALIVE):
                        pygame.draw.rect(screen, (255,255,0), Rect(x*CS,y*CS,CS,CS))
                    elif(self.color[y][x] == STAY):
                        pygame.draw.rect(screen, (255,0,255),Rect(x*CS,y*CS,CS,CS))
                elif self.field[y][x] == DEAD:
                    pygame.draw.rect(screen, (0,255,255), Rect(x*CS,y*CS,CS,CS))
                # Draw glid
                pygame.draw.rect(screen, (150,150,150), Rect(x*CS,y*CS,CS,CS), 1)
        # Draw center line
        pygame.draw.line(screen, (255,0,0),(0,(SCR_RECT.height-100)/2),(SCR_RECT.width,(SCR_RECT.height-100)/2))
        pygame.draw.line(screen, (255,0,0),(SCR_RECT.width/2,0),(SCR_RECT.width/2,SCR_RECT.height-100))
        # Draw cursor
        pygame.draw.rect(screen, (0,0,255), Rect(self.cursor[0]*CS,self.cursor[1]*CS,CS,CS), 1)
        # Draw the information of the game
        screen.blit(self.font.render("generation:%d" % self.generation, True, (0,0,0)), (0,0))
        screen.blit(self.font.render("space : birth/kill",True,(0,0,0,)),(0,12))
        screen.blit(self.font.render("s : start/stop",True,(0,0,0)),(0,24))
        screen.blit(self.font.render("n : next",True,(0,0,0)),(0,36))
        screen.blit(self.font.render("r : random",True,(0,0,0)),(0,48))
    
    def around(self, x, y):
        """Return the number of the alive cells around (x,y)"""
        if x == 0 or x == NUM_COL-1 or y == 0 or y == NUM_ROW-1:
            return 0
        sum = 0
        sum += self.field[y-1][x-1] # cell at the upper left
        sum += self.field[y-1][x]   # cell at upper side
        sum += self.field[y-1][x+1] # cell at the upper right
        sum += self.field[y][x-1]   # cell at the left
        sum += self.field[y][x+1]   # cell at the right
        sum += self.field[y+1][x-1] # cell at the lower left 
        sum += self.field[y+1][x]   # cell at the lower side 
        sum += self.field[y+1][x+1] # cell at the lower right
        return sum

    def draw_char(self,ch):
        msgEng = MessageEngine()
        x = msgEng.kana2rect[ch].x
        y = msgEng.kana2rect[ch].y
        width = msgEng.kana2rect[ch].width
        height = msgEng.kana2rect[ch].height
        for i in range(x,x+width):
            for j in range(y,y+height):
                if img[j][i] > 10:
                    for k in range((i-x)*3,(i-x)*3+3):
                        for l in range((j-y)*3-12,(j-y)*3+3-12):
                            self.field[l][k] = ALIVE
                            self.color[l][k] = ALIVE

# The word written in this window turn into cells(drawing)
class Window:
    """The basic class of window"""
    EDGE_WIDTH = 2 # Width of white edge line
    def __init__(self, rect):
        self.rect = rect # white rectangle
        # Inner black rectangle
        self.inner_rect = self.rect.inflate(-self.EDGE_WIDTH*2,
                                            -self.EDGE_WIDTH*2)
        self.is_visible = False # Window is visible or not
    def draw(self, screen):
        """Draw Window"""
        if self.is_visible == False: return
        pygame.draw.rect(screen, (255,255,255), self.rect, 0)
        pygame.draw.rect(screen, (0,0,0), self.inner_rect, 0)
    def show(self):
        """Show window"""
        self.is_visible = True
    def hide(self):
        """Hide window"""
        self.is_visible = False

class InputWindow(Window):
    def __init__(self, rect, msg_engine):
        Window.__init__(self, rect)
        self.msg_engine = msg_engine
    def get_key(self):
        """キー入力を読み取る"""
        while True:
            event = pygame.event.poll()
            if event.type == KEYDOWN:
                return event.key
            else:
                pass
    def draw(self, screen, message):
        Window.draw(self, screen)
        if len(message) != 0:
            self.msg_engine.draw_string(screen, self.inner_rect.topleft, message)
            pygame.display.flip()
    def ask(self, screen, question):
        cur_str = []
        self.show()
        self.draw(screen, question)
        while True:
            key = self.get_key()
            if key == K_BACKSPACE:
                cur_str = cur_str[0:-1]
            elif key == K_ESCAPE:
                return None
            elif key == K_RETURN:
                break
            elif K_0 <= key <= K_9 or K_a <= key <= K_z:
                cur_str.append(chr(key).upper())
            self.draw(screen, question + u" " + "".join(cur_str))
        return "".join(cur_str)

class MessageEngine:
    FONT_WIDTH = 16
    FONT_HEIGHT = 22
    WHITE, RED, GREEN, BLUE = 0, 160, 320, 480
    def __init__(self):
        self.image = load_image("font.png", -1)
        self.color = self.WHITE
        self.kana2rect = {}
        self.create_hash()
    def set_color(self, color):
        """Set the color of characters"""
        self.color = color
        # Make the color white, if the color was strange
        if not self.color in [self.WHITE,self.RED,self.GREEN,self.BLUE]:
            self.color = self.WHITE
    def draw_character(self, screen, pos, ch):
        """Draw only one character"""
        x, y = pos
        try:
            rect = self.kana2rect[ch]
            screen.blit(self.image, (x,y),
                (rect.x+self.color,rect.y,rect.width,rect.height))
        except KeyError:
            #print "There is the character that cannot be drawn:%s" % ch
            return
    def draw_string(self, screen, pos, string):
        """Draw a string"""
        x,y = pos
        for i, ch in enumerate(string):
            dx = x + self.FONT_WIDTH * i
            self.draw_character(screen, (dx,y) , ch)
    def create_hash(self):
        """Create a dictionary from character to position"""
        filepath = os.path.join("data4LifeGame","kana2rect.dat")
        fp = codecs.open(filepath, "r", "utf-8")
        for line in fp.readlines():
            line = line.rstrip()
            d = line.split(" ")
            kana, x, y, w, h = d[0], int(d[1]), int(d[2]), int(d[3]), int(d[4])
            self.kana2rect[kana] = Rect(x, y, w, h)
        fp.close()

def load_image(filename, colorkey=None):
    filename = os.path.join("data4LifeGame", filename)
    try:
        image = pygame.image.load(filename)
    except pygame.error, message:
        print "Cannot load image:", filename
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey,   RLEACCEL)
    return image

if __name__ == "__main__":
    LifeGame()
