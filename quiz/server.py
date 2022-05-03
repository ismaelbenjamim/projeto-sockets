import threading
import time
from random import randrange
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
            self.temas = ['atualidades', 'entreterimento']
            self.quiz_tema = None
            self.quiz_configurado = False
            self.prefixo = '[Solu Quiz]'
            self.quiz_contador = 1
            self.quiz_questoes = None
            self.quiz_questao_atual = None
            self.quiz_questao_respondida = False
            self.timeout_rodada = False
            self.quiz_jogadores_respoderam = []
            self.servidor_ligado = False
            self.partida_encerrada = False

        def response(self, codigo_msg):
            codigos = {
                "100": "CLIENTE_ATIVO",
                "200": "CLIENTE_SAIU"
            }
            return codigos[codigo_msg]

        def iniciar_servidor(self):
            self.servidor_socket = socket(AF_INET, SOCK_DGRAM)
            self.servidor_socket.bind((self.ip, self.porta))
            self.servidor_socket.setblocking(False)
            self.servidor_ligado = True
            print(f"\n======================= {self.prefixo} =======================")
            print(f"Projeto com Sockets - Solu Quiz Competitivo v1.0")
            print(f"Desenvolvido por: Ismael Benjamim e Tiago Bello")
            print(f'Configure inicialmente o quiz para poder começar, digite: /configurar')
            print(f'Em seguida use o comando /iniciar para dar início a competição')
            print(f'Caso queira saber a lista de comandos, digite: /comandos')
            print(f"===========================================================" + '\n')

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
            while self.servidor_ligado:
                if not self.servidor_ligado:
                    break
                comando = input(self.prefixo + ' Digite um comando para ser executado: ' + '\n')
                comando_params = comando.split(' ')
                if comando_params[0] == '/configurar':
                    if len(comando_params) == 1:
                        comando_params.append(5)
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
                            print(self.prefixo,
                                  'O limite de jogadores precisa ser um valor numérico e o tema do quiz uma string')
                            print(self.prefixo, 'Use o comando como no exemplo: /configurar 5 atualidades' + '\n')
                if not self.quiz_configurado:
                    print(self.prefixo, 'É necessário configurar o quiz inicialmente.')
                    print(self.prefixo, 'Use o comando: /configurar [limite de jogadores] [tema do quiz].' + '\n')
                else:
                    if comando == '/iniciar':
                        if not self.jogadores_conectados or len(self.jogadores_conectados) <= 1:
                            print(self.prefixo, 'Não é possível iniciar a competição, pois não existem jogadores suficientes')
                        else:
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
                chat_server = threading.Thread(target=self.chat_server, args=[])
                chat_server.start()

        def iniciar(self):
            print(self.prefixo, 'Competição sendo iniciada' + '\n')
            quiz = threading.Thread(target=self.quiz, args=[])
            quiz.start()

        def finalizar(self):
            self.partida_encerrada = True
            print(self.prefixo, 'Competição sendo finalizada' + '\n')

        def desligar(self):
            print(self.prefixo, 'Servidor sendo desligado.. aguarde!' + '\n')
            self.servidor_ligado = False
            print(self.prefixo, "Bye bye!!")
            self.servidor_socket.close()
            quit()

        def status(self):
            print(self.prefixo,
                  f'{len(self.jogadores_conectados)}/{self.jogadores_limite} de jogadores conectados' + '\n')

        def enviar_mensagem(self, mensagem, endereco=None):
            if not endereco:
                try:
                    for ip, jogador in self.jogadores_conectados.items():
                        self.servidor_socket.sendto(mensagem.encode(), jogador['ip'])
                except:
                    pass
            else:
                try:
                    self.servidor_socket.sendto(mensagem.encode(), endereco)
                except:
                    pass

        def aguardar_resposta(self):
            mensagem, endereco = self.servidor_socket.recvfrom(1024)

        def get_questao_respondida(self, endereco_str, acertou):
            jogador = self.jogadores_conectados[endereco_str]
            self.quiz_jogadores_respoderam.append(endereco_str)

            if acertou:
                self.quiz_questao_respondida = True
                self.jogadores_conectados[endereco_str]['pontos'] += 25
            else:
                self.jogadores_conectados[endereco_str]['pontos'] += -5
                mensagem = f"Você respondeu incorretamente, então perdeu -5 pontos!"
                self.servidor_socket.sendto(mensagem.encode(), jogador['ip'])

        def rodada_encerrada_sem_vencedor(self):
            mensagem = "Nenhum jogador conseguiu responder em 10seg!"
            for ip, jogador in self.jogadores_conectados.items():
                if ip not in self.quiz_jogadores_respoderam:
                    self.jogadores_conectados[ip]['pontos'] += -1
                    mensagem_nao_respondeu = 'Você não respondeu, então perdeu -1 pontos!'
                    self.servidor_socket.sendto(mensagem_nao_respondeu.encode(), jogador['ip'])
                self.servidor_socket.sendto(mensagem.encode(), jogador['ip'])

        def timeout_questao(self):
            verificar_questao = self.quiz_questao_atual
            time.sleep(10)
            if verificar_questao == self.quiz_questao_atual:
                self.timeout_rodada = True

        def get_response_questao(self):
            while not self.quiz_questao_respondida and not self.timeout_rodada:
                pass
            self.finish_rodada()

        def finish_rodada(self):
            if self.timeout_rodada:
                self.rodada_encerrada_sem_vencedor()
                self.timeout_rodada = False
            else:
                self.quiz_questao_respondida = False
            self.quiz_jogadores_respoderam = []

        def finish_quiz(self):
            #jogadores_ranking = dict(sorted(self.jogadores_conectados.items(), key=lambda item: item['pontos']))
            limite_ranking = 3
            posicao_ranking = 1
            jogadores_ranking = [{'nome': jogador['nome'], 'pontos': jogador['pontos']} for ip, jogador in
                                 self.jogadores_conectados.items()]
            def ordernar_pontos(e):
                return e['pontos']
            jogadores_ranking.sort(key=ordernar_pontos, reverse=True)
            ranking = f"===========================================\n{self.prefixo} Ranking do Solu Quiz\n"
            for jogador in jogadores_ranking:
                if posicao_ranking <= limite_ranking:
                    ranking += f"{self.prefixo} {posicao_ranking}. {jogador['nome']} ({jogador['pontos']} pontos)\n"
                else:
                    break
                posicao_ranking += 1
            for jogador in self.jogadores_conectados:
                self.jogadores_conectados[jogador]['pontos'] = 0
            ranking += '===========================================\n'
            print(ranking)
            self.partida_encerrada = False
            self.enviar_mensagem(ranking)
            self.enviar_mensagem(f"{self.prefixo} O jogo acabou, parabéns pela pontuação!!")


        def get_quiz_questoes(self):
            self.quiz_iniciado = True
            questoes = []
            if self.quiz_tema:
                questoes_arquivo = open(f'questoes/{self.quiz_tema}', 'rb')
                for linha in questoes_arquivo.read().splitlines():
                    questao = str(linha.decode()).split('=')
                    questoes.append((questao[0], questao[1]))
                self.quiz_questoes = questoes

        def get_questoes_rodada(self):
            num_questoes = 5
            questoes = []
            for num in range(0, num_questoes):
                valor = randrange(1, 20)
                questao = self.quiz_questoes[valor]
                while questao in questoes:
                    valor = randrange(1, 20)
                    questao = self.quiz_questoes[valor]
                questoes.append(questao)
            return questoes

        def get_questao(self):
            questoes = self.get_questoes_rodada()
            for questao in questoes:
                if not self.servidor_ligado:
                    break
                if self.partida_encerrada:
                    break
                self.quiz_questao_atual = questao
                index_questao_atual = questoes.index(questao)
                try:
                    self.proxima_questao = questoes[index_questao_atual + 1]
                except:
                    self.proxima_questao = []

                self.enviar_mensagem(f"{self.prefixo} ai vai a questão, preparado?!")
                time.sleep(5)
                self.enviar_mensagem(f"{self.prefixo} {questao[0]}")

                timeout = threading.Thread(target=self.timeout_questao, args=[])
                timeout.start()

                self.get_response_questao()

            self.partida_encerrada = False
            self.finish_quiz()

        def quiz(self):
            self.get_quiz_questoes()
            self.get_questao()
            print(self.prefixo, 'Partida finalizada')

        def get_client_response(self, endereco, endereco_str, mensagem_cliente):
            response_status_ativo = f'{self.prefixo} Ativo'
            if mensagem_cliente == f'{self.prefixo} Sair':
                self.jogadores_conectados.pop(endereco_str)

            if mensagem_cliente == response_status_ativo:
                self.jogadores_conectados[endereco_str]['status'] = True
                print(self.prefixo, f'{endereco_str} atualizado com o status: {self.jogadores_conectados[endereco_str]["status"]}' + '\n')

            if self.quiz_iniciado and mensagem_cliente == self.quiz_questao_atual[1]:
                self.get_questao_respondida(endereco_str, True)

            if self.quiz_iniciado and mensagem_cliente != self.quiz_questao_atual[1]:
                self.get_questao_respondida(endereco_str, False)

            print(self.prefixo, f'[{endereco[0]}:{endereco[1]}] - "{mensagem_cliente}"' + '\n')

        def send_client_response(self, endereco, endereco_str, mensagem_cliente):
            if not self.servidor_lotado:
                self.jogadores_conectados[endereco_str] = {"ip": endereco, "status": False, "nome": mensagem_cliente,
                                                           "pontos": 0}
                print(self.prefixo, f'{endereco[0]}:{endereco[1]} entrou na competição')
                print(self.prefixo, f'{len(self.jogadores_conectados)}/{self.jogadores_limite} usuários conectados')
                print(self.prefixo, f'[{endereco[0]}:{endereco[1]}] - Nome do jogador: "{mensagem_cliente}"' + '\n')

                resposta_servidor = f'{self.prefixo} Bem vindo á competição'
                self.servidor_socket.sendto(resposta_servidor.encode(), endereco)
            else:
                verificar_jogadores_conectados = threading.Thread(target=self.checkar_jogadores,
                                                                  args=[endereco_str, endereco, mensagem_cliente])
                verificar_jogadores_conectados.start()

        def chat_server(self):
            while self.servidor_ligado:
                if len(self.jogadores_conectados) >= self.jogadores_limite:
                    self.servidor_lotado = True

                try:
                    if not self.servidor_ligado:
                        break
                    else:
                        mensagem, endereco = self.servidor_socket.recvfrom(1024)
                except:
                    print(self.prefixo, "Um usuário se desconectou" + '\n')
                    continue

                endereco_str = f'{endereco[0]}:{endereco[1]}'
                mensagem_cliente = str(mensagem.decode())

                if self.jogadores_conectados.get(endereco_str):
                    self.get_client_response(endereco, endereco_str, mensagem_cliente)

                else:
                    if self.quiz_iniciado:
                        resposta_servidor = f'{self.prefixo} Competição já iniciada'
                        self.servidor_socket.sendto(resposta_servidor.encode(), endereco)
                        continue

                    self.send_client_response(endereco, endereco_str, mensagem_cliente)

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
                self.jogadores_conectados[endereco_str] = {"ip": endereco, "status": False, "nome": mensagem_cliente,
                                                           "pontos": 0}
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
