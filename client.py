# -*- coding: utf-8 -*-
import pygame
import sys
from pygame.locals import *
from collections import Counter
import json
import select
import socket

#界面初始化
screen=pygame.display.set_mode((600,650))
pygame.display.set_caption('五子棋 Player 2')
pygame.init()

#图片导入
img_board=pygame.image.load('img/chess_board.png')
img_bchess=pygame.image.load('img/black_chess.png')
img_wchess=pygame.image.load('img/white_chess.png')

#颜色
white=(255,255,255)
black=(0,0,0)

#用于传送的数据
msg=[]

#棋盘定义
chess_board=[[]]
def set_chess_board():
    x,y=0,0
    while True:
        if x==600:
            x=0
            y+=40
            if y<600:
                chess_board.append([])
        if y==600:
            break
        chess_board[-1].append([x,y])
        x+=40
set_chess_board()

#棋盘格子是否落子
chess_exist=[[0 for i in range(15)]for j in range(15)]
#黑白棋子初始化
black_chess,white_chess=[],[]
#棋子类型
chess_kind=1    #1为黑棋，0为白棋
wcx,wcy,bcx,bcy=[],[],[],[]   #white_chess_x

def draw_board():
    for i in chess_board:
        for j in i:
            screen.blit(img_board,(j[0],j[1]))
            pygame.display.update()

#默认棋子类型为0
def set_chess():
    if event.type==MOUSEBUTTONDOWN:
        pos=pygame.mouse.get_pos()
        for i in range(len(chess_board)):
            for j in range(len(chess_board[i])):
                if chess_board[i][j][0]<pos[0]<chess_board[i][j][0]+40 and chess_board[i][j][1]<pos[1]<chess_board[i][j][1]+40:
                    if chess_exist[i][j]==0:
                        white_chess.append([i,j])
                        wcx.append(white_chess[-1][0])
                        wcy.append(white_chess[-1][1])
                        msg.extend((i,j))
                        chess_exist[i][j]=1
                        pygame.display.update()
                        return 1

def draw_chess():
    for i in white_chess:
        screen.blit(img_wchess,(i[1]*40,i[0]*40))
    for i in black_chess:
        screen.blit(img_bchess,(i[1]*40,i[0]*40))
    pygame.display.update()

def row_column_win(x,m,n,chess):
    for i in x:
        if x[i]>=5:
            xy=[]
            for j in chess:
                if j[m]==i:
                    xy.append(j[n])
            xy.sort()
            count=0
            for j in range(len(xy)-1):
                if xy[j]+1==xy[j+1]:
                    count+=1
                else:
                    count=0
            if count>=4:
                return 1

def xiejiao_win(chess):
    x,y=[],[]
    chess.sort()
    for i in chess:
        x.append(i[0])
        y.append(i[1])
    c,first,last=0,0,0
    for i in range(len(x)-1):
        if x[i+1]!=x[i]:
            if x[i]+1==x[i+1]:
                c+=1
                last=i+1
            else:
                if c<4:
                    first=i+1
                    c=0
                else:
                    last=i
                    print(last)
                    break
        else:
            last=i+1
    if c>=4:
        dis=[]
        for i in range(first,last+1):
            dis.append(x[i]-y[i])
        count=Counter(dis)
        for i in count:
            if count[i]>=5:
                return 1
        dis=[]
        x2=[i*(-1) for i in x]
        for i in range(first,last+1):
            dis.append(x2[i]-y[i])
        count=Counter(dis)
        for i in count:
            if count[i]>=5:
                return 1

def gameover():
    wcx_count,wcy_count,bcx_count,bcy_count=Counter(wcx),Counter(wcy),Counter(bcx),Counter(bcy)
    if row_column_win(wcx_count,0,1,white_chess)==1:
        return 1
    elif row_column_win(bcx_count,0,1,black_chess)==1:
        return 0
    elif row_column_win(wcy_count,1,0,white_chess)==1:
        return 1
    elif row_column_win(bcy_count,1,0,black_chess)==1:
        return 0
    elif xiejiao_win(white_chess)==1:
        return 1
    elif xiejiao_win(black_chess)==1:
        return 0

def draw_text(text,x,y,size):
    pygame.font.init()
    fontObj=pygame.font.SysFont('SimHei',size )
    textSurfaceObj=fontObj.render(text, True, white,black)
    textRectObj=textSurfaceObj.get_rect()
    textRectObj.center=(x,y)
    screen.blit(textSurfaceObj, textRectObj)
    pygame.display.update()

#定义客户端名称
#HOST = '10.203.111.180'
HOST = '127.0.0.1'
PORT = 400
BUFSIZE = 1024
ADDR = (HOST,PORT)

#连接服务器
tcpCliSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
tcpCliSock.connect(ADDR)
inputs=[tcpCliSock]

draw_board()
settable=0
roundcount=0
while True:
    rs,ws,es=select.select(inputs,[],[],0)
    for r in rs:
        if r is tcpCliSock:
            data,addr = r.recvfrom(BUFSIZE)
            roundcount=roundcount+1
            score_text='回合数：' + str(roundcount)
            draw_text(score_text,300,640,15)
            draw_text('你的回合',300,620,15)
            data=json.loads(data)
            settable=1
            black_chess.append(data)
            bcx.append(data[0])
            bcy.append(data[1])
    for event in pygame.event.get():
        if event.type==QUIT:
            tcpCliSock.close()
            pygame.quit()
            sys.exit()
        if settable==1:
            if set_chess()==1:
                roundcount=roundcount+1
                score_text='回合数：' + str(roundcount)
                draw_text(score_text,300,640,15)
                draw_text('对手回合',300,620,15)
                settable=0
                msg1=json.dumps(msg)
                tcpCliSock.sendto(msg1.encode(),ADDR)
                msg=[]
    draw_chess()
    if gameover()==1:
        draw_text('你赢了！',300,620,15)
        while True:
            for event in pygame.event.get():
                if event.type==QUIT:
                    pygame.quit()
                    sys.exit()
    elif gameover()==0:
        draw_text('你输了！',300,620,15)
        while True:
            for event in pygame.event.get():
                if event.type==QUIT:
                    pygame.quit()
                    sys.exit()