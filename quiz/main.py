import threading
import time
import json
from random import randrange
from socket import socket, AF_INET, SOCK_DGRAM

"""
- Deverá ser desenvolvido um jogo com competições online de perguntas e respostas;
- Um protocolo da camada de aplicação deverá ser desenvolvido e especificado no relatório;
o Deverá ter pelo menos uma mensagem de requisição e pelo menos uma mensagem de
resposta;
- O protocolo de transporte UDP deverá ser utilizado;
- Um servidor UDP deverá gerenciar as competições;
- Até 5 clientes UDP poderão participar de uma competição;
- Após a competição ser iniciada, não deverá ser permitido o ingresso de novos participantes;
- Cada competição terá 5 rodadas de perguntas e respostas;
- O servidor deverá ter um arquivo de texto contendo pelo menos 20 tuplas de perguntas e
respostas;
    - As respostas deverão ser compostas por uma única palavra, com caracteres minúsculos
    - O tema do Quiz ficará a critério da equipe
- O servidor irá escolher aleatoriamente uma tupla de pergunta/resposta que será utilizada na
rodada;
- Uma mesma competição não poderá ter duas tuplas repetidas;
- Cada rodada será encerrada quando algum participante acertar a resposta ou atingir uma
duração máxima de 10 segundos;
- Pontuação de cada rodada:
    - Cada resposta errada: -5 pontos
    - Sem resposta: -1 ponto
    - Resposta correta: 25 pontos
- Após uma competição ser encerrada, um ranking com a pontuação é divulgado e uma nova
competição poderá ser iniciada.
"""


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
            self.temas = ['atualidades', 'entreterimento', 'historia']
            self.quiz_tema = None
            self.quiz_configurado = False
            self.prefixo = '[Solu Quiz]'
            self.quiz_contador = 1
            self.quiz_perguntas = None
            self.quiz_pergunta_atual = None
            self.quiz_pergunta_respondida = False

        def response(self, codigo_msg):
            codigos = {
                "USUARIO_ATIVO": ""
            }

        def iniciar_servidor(self):
            self.servidor_socket = socket(AF_INET, SOCK_DGRAM)
            self.servidor_socket.bind((self.ip, self.porta))
            self.servidor_socket.setblocking(False)
            print(f"\n======================= {self.prefixo} =======================")
            print(f"Projeto com Sockets - Solu Quiz Competitivo v1.0")
            print(f"Desenvolvido por: Ismael Benjamim e Tiago Bello")
            print(f'Configure inicialmente o quiz para poder começar, digite: /configurar')
            print(f'Em seguida use o comando /iniciar para dar início a competição')
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
                comando = input(self.prefixo + ' Digite um comando para ser executado: ' + '\n')
                comando_params = comando.split(' ')
                if comando_params[0] == '/configurar':
                    if len(comando_params) == 1:
                        comando_params.append(2)
                        comando_params.append('atualidades')
                        self.configurar(comando_params[1], comando_params[2])
                        continue
                    else:
                        try:
                            comando_params[1] = int(comando_params[1])
                            comando_params[2] = str(comando_params[2])
                            self.configurar(comando_params[1], comando_params[2])
                            continue
                        except:
                            print(self.prefixo, 'O limite de jogadores precisa ser um valor numérico e o tema do quiz uma string')
                            print(self.prefixo, 'Use o comando como no exemplo: /configurar 5 atualidades' + '\n')
                if not self.quiz_configurado:
                    print(self.prefixo, 'É necessário configurar o quiz inicialmente.')
                    print(self.prefixo, 'Use o comando: /configurar [limite de jogadores] [tema do quiz].' + '\n')
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


        def configurar(self, jogadores_limite, tema):
            if not jogadores_limite or not tema:
                print(self.prefixo, 'É necessário informar o limite de jogadores e o tema do quiz.')
                print(self.prefixo, 'Use o comando como no exemplo: /configurar 5 atualidades')
            elif jogadores_limite < 2:
                print(self.prefixo, 'O limite de jogadores precisa ser maior que 1')
            elif tema not in self.temas:
                print(self.prefixo, 'O tema do quiz precisa ser atualidades, entreterimento ou historia')
            else:
                self.jogadores_limite = jogadores_limite
                self.quiz_tema = tema
                self.quiz_configurado = True
                self.servidor_socket.setblocking(True)
                print(self.prefixo, 'Quiz configurado com sucesso!')
                print(self.prefixo, f'Limite de jogadores: {self.jogadores_limite} - Tema do quiz: {self.quiz_tema}')
                print(self.prefixo, 'A lista de espera foi aberta e os jogadores poderão se conectar.' + '\n')
                configurar_quiz = threading.Thread(target=self.configurar_quiz, args=[])
                configurar_quiz.start()

        def iniciar(self):
            print(self.prefixo, 'Competição sendo iniciada' + '\n')
            self.quiz()

        def finalizar(self):
            print(self.prefixo, 'Competição sendo finalizada' + '\n')

        def desligar(self):
            print(self.prefixo, 'Servidor sendo desligado' + '\n')

        def status(self):
            print(self.prefixo, f'{len(self.jogadores_conectados)}/{self.jogadores_limite} de jogadores conectados' + '\n')

        def enviar_mensagem(self, mensagem, endereco=None):
            if not endereco:
                for ip, jogador in self.jogadores_conectados.items():
                    self.servidor_socket.sendto(mensagem.encode(), jogador['ip'])
            else:
                self.servidor_socket.sendto(mensagem.encode(), endereco)

        def aguardar_resposta(self):
            mensagem, endereco = self.servidor_socket.recvfrom(1024)

        def get_questao_respondida(self, jogador):
            if not self.quiz_pergunta_respondida:
                self.quiz_pergunta_respondida = True

        def get_questao(self):
            while self.quiz_contador <= 5:
                def valor_aleatorio():
                    return randrange(1, 5)
                valor = valor_aleatorio()
                self.quiz_pergunta_atual = self.quiz_perguntas[valor]
                self.enviar_mensagem(self.quiz_pergunta_atual['pergunta'])
                self.aguardar_resposta()
                self.quiz_contador += 1

            self.quiz_contador = 1
            pass

        def quiz(self):
            self.quiz_iniciado = True
            perguntas = []
            if self.quiz_tema:
                perguntas_arquivo = open(f'quiz/perguntas/{self.quiz_tema}.json', 'r')
                self.quiz_perguntas = json.load(perguntas_arquivo)

            get_questao = threading.Thread(target=self.get_questao, args=[])
            get_questao.start()
            print('Perguntas iniciadas')

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
                    if mensagem_cliente == f'{self.prefixo} Ativo':
                        self.jogadores_conectados[endereco_str]['status'] = True
                        print(self.prefixo, f'{endereco_str} atualizado com o status: {self.jogadores_conectados[endereco_str]["status"]}' + '\n')
                    if self.quiz_iniciado and mensagem_cliente == self.quiz_pergunta_atual['resposta']:
                        self.get_questao_respondida(endereco_str)



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
