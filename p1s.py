import socket
from os import system
import numpy as np
import re
import math

HOST = 'localhost'
PORT = 32000

matrizP1 = np.zeros((5,5))
visaoP2 = np.zeros((5,5))
mapa = [['00','10','20','30','40'],
        ['01','11','21','31','41'],
        ['02','12','22','32','42'],
        ['03','13','23','33','43'],
        ['04','14','24','34','44']]
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
            print('O barco está saindo para fora do mapa')
            return False
        if(orientacao=='v' and (y-lados < 0 or y+lados > 4)):
            print('O barco está saindo para fora do mapa')
            return False
        if(orientacao=='h'):
            for i in range(x-lados, x+lados+1):
                if(matrizP1[y][i] == 1):
                    print('Os barcos não podem se sobrepor')
                    valido = False
        if(orientacao=='v'):
            for i in range(y-lados, y+lados+1):
                if(matrizP1[i][x] == 1):
                    print('Os barcos não podem se sobrepor')
                    valido = False
    else:
        print('Posição inválida')
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

def tiroValido(pos):
    s = re.sub('\d', '$', pos)
    if(s == '$,$'):
        x = int(pos[0])
        y = int(pos[2])
        if((x >= 0) and (x <= 4) and (y >= 0) and (y <= 4)):
            if(visaoP2[y][x] == 0):
                return True
            else:
                print('Um tiro já foi dado nessa posição')
                return False
        else:
            print('Tiro fora do mapa.')
            return False
    else:
        print('Formato inválido.')
        return False

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
            if(matrizP1[i,j] == 1): #Possui barco
                print('OOO ', end='')
            if(matrizP1[i,j] == 2): #Possui barco destruido
                print('xxx ', end='')
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
    print('')
    mostrarMapa()
    mostrarAjuda()

def mostrarMapa():
    print('-------------------')
    for i in range(5):
        for j in range(5):
            print(mapa[i][j],end='')
            print('  ', end='')
        print('')
    print('-------------------')

def mostrarAjuda():
    print('Legenda do seu campo:')
    print('OOO: Seu barco')
    print('xxx: Seu barco destruido')
    print('---------------------')
    print("Leganda do campo do oponente")
    print("ooo: Tiro errado")
    print("XXX: Tiro certo")
    print('---------------------')


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.settimeout(3600)
    s.bind((HOST, PORT))
    s.listen()
    print("Esperando conexão do segundo jogador")
    conn, addr = s.accept()
    with conn:
        clear()
        print("Digite a posição central do seu primeiro barco 3x1 seguida da orientação.")
        print("Exemplo: 1,0h para posicionar o centro do barco na posição (1,0) na horizontal.")
        print("Obs: O índice de posições começa no 0")
        mostrarMapa()
        entrada = input()
        #entrada = '1,1v'
        while(not posicaoValida(entrada, 3)):
            #print('Posição inválida, por favor tente outra')
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
        mostrarMapa()
        entrada = input()
        #entrada = '4,2v'
        while(not posicaoValida(entrada, 5)):
            #print('Posição inválida, por favor tente outra')
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
        
        while(acertos < 8):
            renderizar()
            print("Digite o alvo do seu tiro...")
            entrada = input()
            while(not tiroValido(entrada)):
                #print('Posição inválida, por favor tente outra')
                entrada = input()
            conn.sendall(entrada.encode())
            x = int(entrada[0])
            y = int(entrada[2])
            
            data = conn.recv(1024).decode()
            clear()
            if(not (data=='acertou' or data=='errou')):
                quit()
            if(data=='acertou'):
                print("Você acertou!!")
                print("Esperando tiro do oponente...")
                visaoP2[y][x] = 2
                acertos = acertos + 1
            if(data=='errou'):
                print("Você errou...")
                print("Esperando tiro do oponente...")
                visaoP2[y][x] = 1
        
            if(acertos < 8):
                conn.sendall("continue".encode())
            else:
                break

            renderizar()
            
            data = conn.recv(1024).decode()
            x = int(data[0])
            y = int(data[2])

            clear()
            if(matrizP1[y][x] == 1):
                print("Ele acertou!!!")
                matrizP1[y][x] = 2
                conn.sendall('acertou'.encode())
            if(matrizP1[y][x] == 0):
                print("Ele errou!!!")
                conn.sendall('errou'.encode())
            
            data = conn.recv(1024).decode()
            if(not(data == 'continue')):
                print("Você perdeu!")
                quit()
        
        clear()
        print("Você ganhou!!!")
        conn.sendall("p1ganhou".encode())
