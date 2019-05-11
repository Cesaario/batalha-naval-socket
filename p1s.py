import socket
from os import system
import numpy as np
import re
import math

HOST = '127.0.0.1'
PORT = 32000

matrizP1 = np.zeros((5,5))
visaoP2 = np.zeros((5,5))

def posicaoValida(pos, tam):
    s = re.sub('\d', '$', pos)
    padrao = s.replace('v', '%').replace('h', '%')
    valido = True
    if(padrao == '$,$%'):
        x = int(pos[0])
        y = int(pos[2])
        orientacao = pos[3]
        lados = math.floor(tam/2)
        if(orientacao=='h' and (x-lados < 0 or x+lados > 4)):
            return False
        if(orientacao=='v' and (y-lados < 0 or y+lados > 4)):
            return False
        if(orientacao=='h'):
            for i in range(x-lados, x+lados+1):
                if(matrizP1[y][i] == 1):
                    valido = False
        if(orientacao=='v'):
            for i in range(y-lados, y+lados+1):
                if(matrizP1[i][x] == 1):
                    valido = False
    else:
        valido = False
    #print(valido)
    #return False
    return valido

def adicionarBarco(pos, tam):
    x = int(pos[0])
    y = int(pos[2])
    orientacao = pos[3]
    lados = math.floor(tam/2)
    if(orientacao == 'h'):
        for i in range(x-lados, x+lados+1):
            matrizP1[y][i] = 1
    if(orientacao == 'v'):
        for i in range(y-lados, y+lados+1):
            matrizP1[i][x] = 1


def clear():
    system('cls')

def renderizar():
    for i in range(16):
        print('---', end='')
    print('\n')
    print("       SEU CAMPO           CAMPO DO OPONENTE")
    for i in range(5):
        print('|',end='')
        for j in range(5):
            if(matrizP1[i,j] == 0):
                print('--- ', end='')
            if(matrizP1[i,j] == 1):
                print('OOO ', end='')
        print('|  |', end='')
        for j in range(5):
            if(visaoP2[i,j] == 0):
                print('--- ', end='')
            if(visaoP2[i,j] == 1): #Errou
                print('ooo ', end='')
            if(visaoP2[i,j] == 2): #Acertou
                print('XXX ', end='')
        print('|',end='')
        print('\n')
    for i in range(16):
        print('---', end='')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Esperando conexão do segundo jogador")
    conn, addr = s.accept()
    with conn:
        clear()
        print("Digite a posição central do seu primeiro barco 3x1 seguida da orientação.")
        print("Exemplo: 1,0h para posicionar o centro do barco na posição (1,0) na horizontal.")
        print("Obs: O índice de posições começa no 0")
        entrada = input()
        #entrada = '1,1v'
        while(not posicaoValida(entrada, 3)):
            print('Posição inválida, por favor tente outra')
            entrada = input()
        adicionarBarco(entrada, 3)
        conn.sendall('p1a1'.encode())

        clear()
        print("Esperando o Jogador 2 definir sua primeira posição...")
        data = conn.recv(1024).decode()
        if(not (data=='p2a1')):
            quit()

        clear()
        print("Digite a posição central do seu segundo barco 5x1 seguida da orientação.")
        print("Exemplo: 2,2v para posicionar o centro do barco na posição (2,2) na vertical.")
        print("Obs: O índice de posições começa no 0")
        entrada = input()
        #entrada = '4,2v'
        while(not posicaoValida(entrada, 5)):
            print('Posição inválida, por favor tente outra')
            entrada = input()
        adicionarBarco(entrada, 5)
        conn.sendall('p1a2'.encode())

        clear()
        print("Esperando o Jogador 2 definir sua segunda posição...")
        data = conn.recv(1024).decode()
        if(not (data=='p2a2')):
            quit()

        conn.sendall('ok'.encode())

        clear()

        print('COMEÇOU')
        print(matrizP1)
        renderizar()