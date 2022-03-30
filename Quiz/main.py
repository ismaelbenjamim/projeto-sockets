import threading
from socket import socket, AF_INET, SOCK_DGRAM
from _thread import *

def servidor(servidor_socket, usuarios_conectados, limite_usuarios):
    while True:
        if len(usuarios_conectados) < limite_usuarios:
            mensagem, endereco = servidor_socket.recvfrom(1024)
            usuarios_conectados.append(f'{endereco[0]}:{endereco[1]}')
            print(f'[Info] {endereco[0]}:{endereco[1]} entrou na competição')
            print(f'[Info] {len(usuarios_conectados)} usuários conectados')

            msg = str(mensagem.decode())

            if msg == 'desligar':
                print('[Info] Encerrando servidor.')
                break

            print('')
            print(f'\n[Info] {endereco[0]}:{endereco[1]}: "{msg}"')

            resp = 'Está na competição'
            servidor_socket.sendto(resp.encode(), endereco)
        else:
            resp = 'Não é possivel entrar na competição'
            mensagem, endereco = servidor_socket.recvfrom(1024)
            servidor_socket.sendto(resp.encode(), endereco)

def iniciar():
    print('')
    print('[Info] Competição sendo iniciada')

def finalizar():
    print('')
    print('[Info] Competição sendo finalizada')

def desligar():
    print('')
    print('[Info] Servidor sendo desligado')

def listar_comandos():
    print('')
    print(f"============= Lista de comandos ==============")
    print(f"/iniciar (inicia a competição)")
    print(f"/finalizar (finaliza a competição)")
    print(f"/desligar (desliga o servidor)")
    print(f"==============================================")

def executar_comandos():
    print('[Info] Caso queira saber a lista de comandos, digite: /comandos')
    while True:
        print('')
        comando = input('Digite um comando para ser executado: ')
        if comando == '/iniciar':
            iniciar()
        elif comando == '/desligar':
            desligar()
        elif comando == '/finalizar':
            finalizar()
        elif comando == '/comandos':
            listar_comandos()
        else:
            print('')
            print('[Info] Comando não reconhecido, tente novamente.')

def main():
    ip = '127.0.0.1'
    porta = 8000
    limite_usuarios = 2
    usuarios_conectados = []

    servidor_socket = socket(AF_INET, SOCK_DGRAM)
    servidor_socket.bind((ip, porta))
    #print(dir(servidor_socket))
    #print('')
    print(f"==============================================")
    print(f"Projeto com Sockets - Quiz Competitivo v1.0")
    print(f"Desenvolvido por: Ismael Benjamim e Tiago Bello")
    print(f"==============================================")

    iniciar_servidor = threading.Thread(target=servidor, args=(servidor_socket, usuarios_conectados, limite_usuarios))
    iniciar_servidor.start()

    executar_comando = threading.Thread(target=executar_comandos, args=[])
    executar_comando.start()


if __name__ == '__main__':
    main()