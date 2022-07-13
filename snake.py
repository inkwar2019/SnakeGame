import sys
import random
from typing import Counter
from PIL import Image, ImageTk
from tkinter import Tk, Frame, Canvas, ALL, NW, StringVar
from random import randint

#Setting
DOT_SIZE = 10
GRID_WIDTH = 75
GRID_HEIGHT = 50
BOARD_WIDTH = GRID_WIDTH * DOT_SIZE
BOARD_HEIGHT = GRID_HEIGHT * DOT_SIZE
DELAY = 100
MAX_RAND_POS = 27

#themes
LIGHT = {"bg":"white","body":"gray","head":"black","text":"blue"}
DARK = {"bg":"black","body":"red","head":"white","text":"blue"}
CURRENT_THEME = LIGHT

#Global variable
IN_GAME = False
GAMEOVER = False
PAUSE = False
LENGTH = 3
BODY = []
ENEMY_NUM = 0
FOOD_NUM = 1
FOOD = []
ENEMY = []
DIR = (1,0)
BACKUP_DIR = DIR
HEART = 0
COUNTER = 0
FALL_DOWN_COUNTER = 0
FALL_DOWN_COUNTER_POS = (0,0)

#Global Object
root = None
board = None
score = 0
last_score = 0
the_text = f'''
            Press Enter for "PLAY"
            Press Backspace for "EXIT"
            Press Left, Right, Up, Down for "MOVEMENT"
            Press Space for "PAUSE" and "RESUME"
            '''

class Cell:
    def __init__(self,pos):
        self.pos_x,self.pos_y = pos
    def pos(self):
        return (self.pos_x,self.pos_y)
    def set_pos(self,pos):
        self.pos_x,self.pos_y = pos


def onKeyPressed(e):
    global IN_GAME,DIR,PAUSE,root,CURRENT_THEME,LIGHT,DARK,BACKUP_DIR,GAMEOVER
    key = e.keysym
    if key == "Left" and IN_GAME and not PAUSE and DIR != (1,0):
        DIR = (-1,0)
    if key == "Right" and IN_GAME and not PAUSE and DIR != (-1,0):
        DIR = (1,0)
    if key == "Up" and IN_GAME and not PAUSE and DIR != (0,1):
        DIR = (0,-1)
    if key == "Down" and IN_GAME and not PAUSE and DIR != (0,-1):
        DIR = (0,1)
    if key == "space" and IN_GAME:
        if GAMEOVER:
            GAMEOVER = False
            game_initialize()
            PAUSE = False
            return
        if PAUSE:
            PAUSE = False
            DIR = BACKUP_DIR
        else:
            BACKUP_DIR = DIR
            DIR = (0,0)
            PAUSE = True
    if key == "Return":
        if not IN_GAME:
            IN_GAME = True
            game_initialize()
            gaming()
            board.delete('t')
    if key == "BackSpace":
        if not IN_GAME:
            root.destroy()
        if IN_GAME:
            IN_GAME = False
    if key == "t" and False:
        CURRENT_THEME = DARK
        root.configure(background=CURRENT_THEME["bg"])


def forwarding(pos):
    global DIR
    return (x if(x>=0) else y for x,y in zip((p if(p<q) else 0 for p,q in zip(tuple(i+j*DOT_SIZE for i,j in zip(pos,DIR)),(BOARD_WIDTH,BOARD_HEIGHT))),(BOARD_WIDTH,BOARD_HEIGHT)))


def moving():
    global BODY,FALL_DOWN_COUNTER_POS
    FALL_DOWN_COUNTER_POS = BODY[-1].pos()
    for i in reversed(range(LENGTH-1)):
        BODY[i+1].set_pos(BODY[i].pos())
    BODY[0].set_pos(forwarding(BODY[0].pos()))
    

def increament():
    global BODY,LENGTH,FOOD,FOOD_NUM
    BODY.append(Cell(BODY[LENGTH-1].pos()))
    LENGTH = LENGTH + 1


def check_collision():
    global FOOD,BODY,ENEMY,ENEMY_NUM,FOOD_NUM,IN_GAME,PAUSE,BACKUP_DIR,DIR,GAMEOVER,score,FALL_DOWN_COUNTER
    for i in range(ENEMY_NUM):
        if ENEMY[i].pos() == BODY[0].pos():
            PAUSE = True
            BACKUP_DIR = (1,0)
            DIR = (0,0)
            GAMEOVER = True
    for i in range(FOOD_NUM):
        if FOOD[i].pos() == BODY[0].pos():
            FALL_DOWN_COUNTER = 0
            FOOD[i].set_pos(random_pos())
            increament()
            ENEMY[i].set_pos(random_pos())
            score = score + 1

def gaming():
    global BODY,board,CURRENT_THEME,score,last_score,PAUSE,DIR,DOT_SIZE,FOOD_NUM,FOOD,ENEMY_NUM,ENEMY,GAMEOVER,HEART,COUNTER,FALL_DOWN_COUNTER,LENGTH

    board.delete('all')
    moving()
    check_collision()
    if not GAMEOVER:
        for i in range(LENGTH):
            board.create_polygon(pos_to_cor(BODY[i].pos()), outline=CURRENT_THEME["head"],fill=CURRENT_THEME["head"] if i==0 else CURRENT_THEME["body"], width=2)
        for i in range(FOOD_NUM):
            board.create_polygon(pos_to_cor(FOOD[i].pos()), outline=CURRENT_THEME["head"],fill="green", width=2-HEART)
        for i in range(ENEMY_NUM):
            board.create_polygon(pos_to_cor(ENEMY[i].pos()), outline=CURRENT_THEME["head"],fill="red", width=2-HEART)

    if not IN_GAME:
        last_score = score
        initial()
        return
    if PAUSE:
        board.create_text(BOARD_WIDTH/2,DOT_SIZE*10,fill=CURRENT_THEME["text"],font="Times 50 bold",
                        text="GameOver" if(GAMEOVER) else "Paused",tag="p")
        board.create_text(BOARD_WIDTH/2,BOARD_HEIGHT/2,fill=CURRENT_THEME["text"],font="Times 50 bold",
                        text=str(score),tag="p")
    else:
        board.create_text((BODY[0].pos()[0]+5,BODY[0].pos()[1]+DOT_SIZE*(2 if(DIR[1]==1) else -1)) if(DIR[0]==0) else ((BODY[0].pos()[0]+5,BODY[0].pos()[1]-DOT_SIZE) if(BODY[0].pos()[1]>BOARD_HEIGHT/2) else (BODY[0].pos()[0]+5,BODY[0].pos()[1]+DOT_SIZE*2)),fill=CURRENT_THEME["text"],font="Times 10 bold",
                        text=str(score),tag="p") 
    if COUNTER%5 == 0:
        HEART = 2 if(HEART==0) else 0
    if COUNTER%15 == 0 and not PAUSE:
        FALL_DOWN_COUNTER += 1
    if LENGTH>3 and not PAUSE and not GAMEOVER:
        board.create_text(FALL_DOWN_COUNTER_POS[0]+5,FALL_DOWN_COUNTER_POS[1]+6,fill="red",font="Times 10 bold",
                        text=FALL_DOWN_COUNTER,tag="q")
    if LENGTH>3 and FALL_DOWN_COUNTER >= 10:
        FALL_DOWN_COUNTER = 0
        BODY.pop()
        LENGTH -= 1
    COUNTER = COUNTER + 1
    board.after(DELAY,gaming)

def game_initialize():
    global BODY,score,DIR,PAUSE,LENGTH,ENEMY_NUM,ENEMY,FOOD_NUM,FOOD,COUNTER
    score = 0
    BODY = []
    FOOD = []
    ENEMY = []
    DIR = (1,0)
    PAUSE = False
    LENGTH = 3
    ENEMY_NUM = 1
    FOOD_NUM = 1
    COUNTER = 0
    for i in range(LENGTH):
        BODY.append(Cell((i*DOT_SIZE,0)))
    for i in range(ENEMY_NUM):
        ENEMY.append(Cell(random_pos()))
    for i in range(FOOD_NUM):
        FOOD.append(Cell(random_pos()))

def initial():
    global CURRENT_THEME
    board.delete('all')
    board.create_text(BOARD_WIDTH/2,DOT_SIZE*5,fill=CURRENT_THEME["text"],font="Times 14 bold",text="Welcome to Snake Game",tag="t")
    board.create_text(BOARD_WIDTH/2,BOARD_HEIGHT/2,fill=CURRENT_THEME["text"],font="Times 10 bold",text=the_text,tag="t")

def pos_to_cor(pos):
    x,y = pos
    return (x,y,x+DOT_SIZE,y,x+DOT_SIZE,y+DOT_SIZE,x,y+DOT_SIZE)

def random_pos():
    global DOT_SIZE,GRID_WIDTH,GRID_HEIGHT
    return (randint(1,GRID_WIDTH-1)*DOT_SIZE,randint(1,GRID_HEIGHT-1)*DOT_SIZE)


def main():
    global root,board,DELAY,CURRENT_THEME
    root = Tk()
    root.title("SankeGame")
    board = Canvas(root,width=BOARD_WIDTH,height=BOARD_HEIGHT,background=CURRENT_THEME["bg"],highlightthickness=0)
    board.bind_all("<Key>", onKeyPressed)
    initial()
    board.pack()
    root.mainloop()


if __name__ == '__main__':
    main()