import threading
import time
from socket import socket, AF_INET, SOCK_DGRAM

def main():

    class Servidor:
        def __init__(self, ip, porta):
            self.ip = ip
            self.porta = porta
            self.jogadores_limite = None
            self.jogadores_conectados = {}
            self.servidor_socket = None
            self.servidor_lotado = False
            self.quiz_iniciado = False
            self.quiz_configurado = False
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
            print("-> /configurar (configura as informações iniciais do quiz)")
            print("-> /iniciar (inicia a competição)")
            print("-> /finalizar (finaliza a competição)")
            print("-> /desligar (desliga o servidor)")
            print("-> /status (confere o status do servidor)")
            print("===============================================")

        def executar_comandos(self):
            print(self.prefixo, 'Caso queira saber a lista de comandos, digite: /comandos')
            while True:
                comando = input('Digite um comando para ser executado: ')
                comando_params = comando.split(' ')
                if comando_params[0] == '/configurar':
                    try:
                        comando_params[1] = int(comando_params[1])
                        comando_params[2] = int(comando_params[2])
                        self.configurar(comando_params.__getitem__(1), comando_params.__getitem__(2))
                        continue
                    except:
                        print(self.prefixo, 'O limite de jogadores e o nível do quiz precisam ser um valor numérico.')
                        print(self.prefixo, 'Use o comando como no exemplo: /configurar 5 1'+ '\n')
                if not self.quiz_configurado:
                    print(self.prefixo, 'É necessário configurar o quiz inicialmente.')
                    print(self.prefixo, 'Use o comando: /configurar [limite de jogadores] [nível do quiz].' + '\n')
                else:
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


        def configurar(self, jogadores_limite, nivel_quiz):
            if not jogadores_limite or not nivel_quiz:
                print(self.prefixo, 'É necessário informar o limite de jogadores e o nível do quiz.')
                print(self.prefixo, 'Use o comando como no exemplo: /configurar 5 1')
            if jogadores_limite < 2:
                print(self.prefixo, 'O limite de jogadores precisa ser maior que 1')
            if nivel_quiz < 1 or nivel_quiz > 3:
                print(self.prefixo, 'O nível do quiz precisa ser entre 1 e 3')
            self.jogadores_limite = jogadores_limite
            self.quiz_configurado = True
            self.servidor_socket.setblocking(True)
            print(self.prefixo, 'Quiz configurado com sucesso e está pronto para iniciar.' + '\n')
            configurar_quiz = threading.Thread(target=self.configurar_quiz, args=[])
            configurar_quiz.start()

        def iniciar(self):
            print(self.prefixo, 'Competição sendo iniciada' + '\n')

        def finalizar(self):
            print(self.prefixo, 'Competição sendo finalizada' + '\n')

        def desligar(self):
            print(self.prefixo, 'Servidor sendo desligado' + '\n')

        def status(self):
            print(self.prefixo, f'{len(self.jogadores_conectados)}/{self.jogadores_limite} de jogadores conectados' + '\n')


        def configurar_quiz(self):
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
                print(self.prefixo, f'{len(self.jogadores_conectados)} usuários conectados')
                print(self.prefixo, f'[{endereco[0]}:{endereco[1]}] - Nome do jogador: "{mensagem_cliente}"' + '\n')
            else:
                resposta_servidor = f'{self.prefixo} Limite de jogadores alcançado!'
                self.servidor_socket.sendto(resposta_servidor.encode(), endereco)

            for ip, jogador in self.jogadores_conectados.items():
                jogador["status"] = False


    servidor = Servidor('127.0.0.1', 8000)
    servidor.iniciar_servidor()


if __name__ == '__main__':
    main()
