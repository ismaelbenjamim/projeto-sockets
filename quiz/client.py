import threading
from socket import socket, AF_INET, SOCK_DGRAM


class Client:
    def __init__(self, servidor):
        self.cliente_socket = None
        self.servidor = servidor
        self.status = True

    def iniciar_cliente(self):
        self.cliente_socket = socket(AF_INET, SOCK_DGRAM)

    def response_servidor(self):
        while self.status:
            try:
                msg, endereco = self.cliente_socket.recvfrom(1024)
                mensagem_servidor = msg.decode()

                if mensagem_servidor == '[Solu Quiz] Jogador conectado?':
                    self.request_servidor('[Solu Quiz] Ativo')

                print(f"\n{mensagem_servidor}")
            except:
                pass

    def request_servidor(self, mensagem_envio=None):
        if mensagem_envio:
            mensagem_codificada = mensagem_envio.encode()
            self.cliente_socket.sendto(mensagem_codificada, self.servidor)

    def enviar_mensagem(self):
        while self.status:
            mensagem_envio = input("\nDigite sua mensagem: ")
            if mensagem_envio == '/sair':
                self.status = False
                self.request_servidor('[Solu Quiz] Sair')
                print('[Solu Quiz] Cliente encerrando! \n')
                self.cliente_socket.close()
            else:
                self.request_servidor(mensagem_envio)


def main():
    servidor = ('127.0.0.1', 8000)
    cliente = Client(servidor)
    cliente.iniciar_cliente()
    print("[Solu Quiz] Tentando conectar...")

    nome = input("\nDigite seu nome: ")
    mensagem_nome = nome.encode()
    cliente.cliente_socket.sendto(mensagem_nome, servidor)

    aguardar_servidor = threading.Thread(target=cliente.response_servidor)
    aguardar_servidor.start()

    aguardar_mensagem = threading.Thread(target=cliente.enviar_mensagem)
    aguardar_mensagem.start()



if __name__ == "__main__":
    main()
