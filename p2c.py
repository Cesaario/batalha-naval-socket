import socket
from os import system
import numpy as np
import re
import math

HOST = '186.213.68.128'
PORT = 32000

matrizP2 = np.zeros((5,5))
visaoP1 = np.zeros((5,5))
acertos = 0

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
                if(matrizP2[y][i] == 1):
                    valido = False
        if(orientacao=='v'):
            for i in range(y-lados, y+lados+1):
                if(matrizP2[i][x] == 1):
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
            matrizP2[y][i] = 1
    if(orientacao == 'v'):
        for i in range(y-lados, y+lados+1):
            matrizP2[i][x] = 1

def tiroValido(pos):
    s = re.sub('\d', '$', pos)
    if(s == '$,$'):
        x = int(pos[0])
        y = int(pos[2])
        if((x >= 0) and (x <= 4) and (y >= 0) and (y <= 4)):
            if(visaoP1[y][x] == 0):
                return True
            else:
                return False
        else:
            return False
    else:
        return False

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
            if(matrizP2[i,j] == 0): 
                print('--- ', end='')
            if(matrizP2[i,j] == 1): #Possui barco
                print('OOO ', end='')
            if(matrizP2[i,j] == 2): #Possui barco destruido
                print('xxx ', end='')
        print('|  |', end='')
        for j in range(5):
            if(visaoP1[i,j] == 0):
                print('--- ', end='')
            if(visaoP1[i,j] == 1): #Errou
                print('ooo ', end='')
            if(visaoP1[i,j] == 2): #Acertou
                print('XXX ', end='')
        print('|',end='')
        print('\n')
    for i in range(16):
        print('---', end='')
    print("")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.settimeout(3600)
    s.connect((HOST, PORT))
    clear()
    print("Esperando o Jogador 1 definir sua primeira posição...")
    data = s.recv(1024).decode()
    print(data)
    if(not (data=='p1a1')):
        quit()
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
    s.sendall('p2a1'.encode())

    clear()
    print("Esperando o Jogador 1 definir sua segunda posição...")
    data = s.recv(1024).decode()
    if(not (data=='p1a2')):
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
    s.sendall('p2a2'.encode())

    #THREE WAY HANDSHAKEEEEE \o/
    data = s.recv(1024).decode()
    print(data)
    if(not (data=='ok')):
        quit()

    clear()

    print('COMEÇOU')

    while(acertos < 8):
        renderizar()
        print("Esperando tiro do oponente")
        data = s.recv(1024).decode()

        x = int(data[0])
        y = int(data[2])

        clear()
        if(matrizP2[y][x] == 1):
            print("Ele acertou!!!")
            matrizP2[y][x] = 2
            s.sendall('acertou'.encode())
        if(matrizP2[y][x] == 0):
            print("Ele errou!!!")
            s.sendall('errou'.encode())

        data = s.recv(1024).decode()
        if(not(data == 'continue')):
            print("Você perdeu!")
            quit()

        renderizar()
        
        print("Digite o alvo do seu tiro...")
        entrada = input()
        while(not tiroValido(entrada)):
            print('Posição inválida, por favor tente outra')
            entrada = input()
        s.sendall(entrada.encode())
        
        data = s.recv(1024).decode()
        x = int(entrada[0])
        y = int(entrada[2])

        clear()
        
        if(not (data=='acertou' or data=='errou')):
            quit()
        if(data=='acertou'):
            print("Você acertou!!")
            print("Esperando tiro do oponente...")
            visaoP1[y][x] = 2
            acertos = acertos + 1
        if(data=='errou'):
            print("Você errou...")
            print("Esperando tiro do oponente...")
            visaoP1[y][x] = 1
        
        if(acertos < 8):
            s.sendall("continue".encode())
        else:
            break
        
    clear()
    print("Você ganhou!!!")
    s.sendall("p2ganhou".encode())