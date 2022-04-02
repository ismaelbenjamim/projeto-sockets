import threading
import time
from socket import socket, AF_INET, SOCK_DGRAM
from _thread import *

def servidor(servidor_socket, jogadores_conectados, limite_usuarios):
    servidor_lotado = False
    while True:
        if len(jogadores_conectados) >= limite_usuarios:
            servidor_lotado = True

        try:
            mensagem, endereco = servidor_socket.recvfrom(1024)
        except:
            print("[Info] Um usuário se desconectou")
            continue
        endereco_str = f'{endereco[0]}:{endereco[1]}'
        mensagem_cliente = str(mensagem.decode())

        if jogadores_conectados.get(endereco_str):
            if mensagem_cliente == 'desligar':
                print('[Info] Encerrando servidor.')
                break
            elif mensagem_cliente == '[Info] Ativo':
                jogadores_conectados[endereco_str]['status'] = True
                print(f'[Info] {endereco_str} atualizado com o status: {jogadores_conectados[endereco_str]["status"]}')

            print(f'\n[{endereco[0]}:{endereco[1]}]: "{mensagem_cliente}"')

        else:
            if not servidor_lotado:
                if mensagem_cliente == 'desligar':
                    print('[Info] Encerrando servidor.')
                    break

                jogadores_conectados[endereco_str] = {"ip": endereco, "status": False}
                print(f'[Info] {endereco[0]}:{endereco[1]} entrou na competição')
                print(f'[Info] {len(jogadores_conectados)} usuários conectados')
                print('')
                print(f'\n[{endereco[0]}:{endereco[1]}] - Nome do jogador: "{mensagem_cliente}"')

                resposta_servidor = '[Info] Bem vindo á competição'
                servidor_socket.sendto(resposta_servidor.encode(), endereco)
            else:
                info_jogador = {
                    "endereco_str": endereco_str,
                    "endereco": endereco,
                    "mensagem_cliente": mensagem_cliente
                }
                verificar_jogadores_conectados = threading.Thread(target=checkar_jogadores, args=[jogadores_conectados, servidor_socket, servidor_lotado, info_jogador])
                verificar_jogadores_conectados.start()


def iniciar():
    print('')
    print('[Info] Competição sendo iniciada')

def finalizar():
    print('')
    print('[Info] Competição sendo finalizada')

def desligar():
    print('')
    print('[Info] Servidor sendo desligado')

def status(jogadores_conectados, limite_usuarios):
    print('')
    print(f'[Info] {len(jogadores_conectados)}/{limite_usuarios} de jogadores conectados')

def checkar_jogadores(jogadores_conectados, servidor_socket, servidor_lotado, info_jogador):
    endereco_str = info_jogador['endereco_str']
    endereco = info_jogador['endereco']
    mensagem_cliente = info_jogador['mensagem_cliente']

    mensagem_jogador = '[Info] Jogador conectado?'
    print(jogadores_conectados)

    for ip, jogador in jogadores_conectados.items():
        servidor_socket.sendto(mensagem_jogador.encode(), jogador['ip'])

    time.sleep(5)

    jogadores_desconectados = []
    for ip, jogador in jogadores_conectados.items():
        if not jogador["status"]:
            jogadores_desconectados.append(ip)

    if jogadores_desconectados:
        for ip in jogadores_desconectados:
            jogadores_conectados.pop(ip)
        servidor_lotado = False

    print(jogadores_conectados)

    if not servidor_lotado:
        jogadores_conectados[endereco_str] = {"ip": endereco, "status": False}

        print(f'[Info] {endereco[0]}:{endereco[1]} entrou na competição')
        print(f'[Info] {len(jogadores_conectados)} usuários conectados')
        print('')
        print(f'\n[{endereco[0]}:{endereco[1]}] - Nome do jogador: "{mensagem_cliente}"')
    else:
        resposta_servidor = '[Info] Limite de jogadores alcançado!'
        servidor_socket.sendto(resposta_servidor.encode(), endereco)

    for ip, jogador in jogadores_conectados.items():
        jogador["status"] = False

    return servidor_lotado



def listar_comandos():
    print('')
    print(f"============= Lista de comandos ==============")
    print(f"/iniciar (inicia a competição)")
    print(f"/finalizar (finaliza a competição)")
    print(f"/desligar (desliga o servidor)")
    print(f"==============================================")

def executar_comandos(jogadores_conectados, limite_usuarios):
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
        elif comando == '/status':
            status(jogadores_conectados, limite_usuarios)
        elif comando == '/comandos':
            listar_comandos()
        else:
            print('')
            print('[Info] Comando não reconhecido, tente novamente.')

def main():
    ip = '127.0.0.1'
    porta = 8000
    limite_usuarios = 2
    jogadores_conectados = {}

    servidor_socket = socket(AF_INET, SOCK_DGRAM)
    servidor_socket.bind((ip, porta))
    #print(dir(servidor_socket))
    #print('')
    print(f"==============================================")
    print(f"Projeto com Sockets - Quiz Competitivo v1.0")
    print(f"Desenvolvido por: Ismael Benjamim e Tiago Bello")
    print(f"==============================================")

    iniciar_servidor = threading.Thread(target=servidor, args=(servidor_socket, jogadores_conectados, limite_usuarios))
    iniciar_servidor.start()

    executar_comando = threading.Thread(target=executar_comandos, args=[jogadores_conectados, limite_usuarios])
    executar_comando.start()


if __name__ == '__main__':
    main()