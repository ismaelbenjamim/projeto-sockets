import threading
import time
from socket import socket, AF_INET, SOCK_DGRAM
from _thread import *

def main():

    class Servidor:
        def __init__(self, ip, porta, jogadores_limite):
            self.ip = ip
            self.porta = porta
            self.jogadores_limite = jogadores_limite
            self.jogadores_conectados = {}
            self.servidor_socket = None
            self.servidor_lotado = False
            self.quiz_iniciado = False
            self.prefixo = '[Solu Quiz]'

        def iniciar_servidor(self):
            self.servidor_socket = socket(AF_INET, SOCK_DGRAM)
            self.servidor_socket.bind((self.ip, self.porta))
            self.servidor_socket.setblocking(False)
            print(f"\n======================= {self.prefixo} =======================")
            print(f"Projeto com Sockets - Solu Quiz Competitivo v1.0")
            print(f"Desenvolvido por: Ismael Benjamim e Tiago Bello")
            print(f'Caso queira saber a lista de comandos, digite: /comandos')
            print(f"==========================================================="+ '\n')

            executar_comando = threading.Thread(target=self.executar_comandos, args=[])
            executar_comando.start()

        def listar_comandos(self):
            print(f"\n======== {self.prefixo} Lista de comandos ========")
            print("-> /iniciar (inicia a competição)")
            print("-> /finalizar (finaliza a competição)")
            print("-> /desligar (desliga o servidor)")
            print("-> /status (confere o status do servidor)")
            print("===============================================")

        def executar_comandos(self):
            print(self.prefixo, 'Caso queira saber a lista de comandos, digite: /comandos')
            while True:
                comando = input('Digite um comando para ser executado: ')
                if comando == '/iniciar':
                    self.iniciar()
                elif comando == '/desligar':
                    self.desligar()
                elif comando == '/finalizar':
                    self.finalizar()
                elif comando == '/status':
                    self.status()
                elif comando == '/comandos':
                    self.listar_comandos()
                else:
                    print(self.prefixo, 'Comando não reconhecido, tente novamente.' + '\n')


        def iniciar(self):
            print(self.prefixo, 'Competição sendo iniciada' + '\n')
            self.servidor_socket.setblocking(True)
            iniciar_quiz = threading.Thread(target=self.iniciar_quiz(), args=[])
            iniciar_quiz.start()

        def finalizar(self):
            print(self.prefixo, 'Competição sendo finalizada' + '\n')

        def desligar(self):
            print(self.prefixo, 'Servidor sendo desligado' + '\n')

        def status(self):
            print(self.prefixo, f'{len(self.jogadores_conectados)}/{self.jogadores_limite} de jogadores conectados' + '\n')


        def iniciar_quiz(self):
            while True:
                if len(self.jogadores_conectados) >= self.jogadores_limite:
                    self.servidor_lotado = True

                try:
                    mensagem, endereco = self.servidor_socket.recvfrom(1024)
                except:
                    print(self.prefixo, "Um usuário se desconectou" + '\n')
                    continue
                endereco_str = f'{endereco[0]}:{endereco[1]}'
                mensagem_cliente = str(mensagem.decode())

                if self.jogadores_conectados.get(endereco_str):
                    if mensagem_cliente == 'desligar':
                        print(self.prefixo, 'Encerrando servidor.' + '\n')
                        break
                    elif mensagem_cliente == f'{self.prefixo} Ativo':
                        self.jogadores_conectados[endereco_str]['status'] = True
                        print(self.prefixo, f'{endereco_str} atualizado com o status: {self.jogadores_conectados[endereco_str]["status"]}' + '\n')

                    print(self.prefixo, f'[{endereco[0]}:{endereco[1]}] - "{mensagem_cliente}"' + '\n')

                else:
                    if not self.servidor_lotado:
                        if mensagem_cliente == 'desligar':
                            print(self.prefixo, 'Encerrando servidor.' + '\n')
                            break

                        self.jogadores_conectados[endereco_str] = {"ip": endereco, "status": False, "nome": mensagem_cliente}
                        print(self.prefixo, f'{endereco[0]}:{endereco[1]} entrou na competição')
                        print(self.prefixo, f'{len(self.jogadores_conectados)} usuários conectados')
                        print(self.prefixo, f'[{endereco[0]}:{endereco[1]}] - Nome do jogador: "{mensagem_cliente}"' + '\n')

                        resposta_servidor = f'{self.prefixo} Bem vindo á competição'
                        self.servidor_socket.sendto(resposta_servidor.encode(), endereco)
                    else:
                        verificar_jogadores_conectados = threading.Thread(target=self.checkar_jogadores, args=[endereco_str, endereco, mensagem_cliente])
                        verificar_jogadores_conectados.start()


        def checkar_jogadores(self, endereco_str, endereco, mensagem_cliente):
            mensagem_jogador = f'{self.prefixo} Jogador conectado?'
            for ip, jogador in self.jogadores_conectados.items():
                self.servidor_socket.sendto(mensagem_jogador.encode(), jogador['ip'])

            time.sleep(5)

            jogadores_desconectados = []
            for ip, jogador in self.jogadores_conectados.items():
                if not jogador["status"]:
                    jogadores_desconectados.append(ip)

            if jogadores_desconectados:
                for ip in jogadores_desconectados:
                    self.jogadores_conectados.pop(ip)
                self.servidor_lotado = False

            if not self.servidor_lotado:
                self.jogadores_conectados[endereco_str] = {"ip": endereco, "status": False, "nome": mensagem_cliente}
                print(self.prefixo, f'{endereco[0]}:{endereco[1]} entrou na competição')
                print(self.prefixo, f'[Info] {len(self.jogadores_conectados)} usuários conectados')
                print(self.prefixo, f'[{endereco[0]}:{endereco[1]}] - Nome do jogador: "{mensagem_cliente}"' + '\n')
            else:
                resposta_servidor = f'{self.prefixo} Limite de jogadores alcançado!'
                self.servidor_socket.sendto(resposta_servidor.encode(), endereco)

            for ip, jogador in self.jogadores_conectados.items():
                jogador["status"] = False


    servidor = Servidor('127.0.0.1', 8000, 2)
    servidor.iniciar_servidor()


if __name__ == '__main__':
    main()
