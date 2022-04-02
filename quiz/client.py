import threading
from socket import socket, AF_INET, SOCK_DGRAM

def response_servidor(cliente_socket, servidor):
    while True:
        msg, endereco = cliente_socket.recvfrom(1024)
        mensagem_servidor = msg.decode()

        if mensagem_servidor == '[Info] Jogador conectado?':
            request_servidor(cliente_socket, servidor, '[Info] Ativo')

        print(mensagem_servidor)

def request_servidor(cliente_socket, servidor, mensagem_envio=None):
    if mensagem_envio:
        if mensagem_envio == 'sair':
            print('[Info] Cliente encerrando!')
            cliente_socket.close()

        mensagem_codificada = mensagem_envio.encode()
        cliente_socket.sendto(mensagem_codificada, servidor)

def enviar_mensagem(cliente_socket, servidor):
    while True:
        mensagem_envio = input("\nDigite sua mensagem: ")
        request_servidor(cliente_socket, servidor, mensagem_envio)


def main():
    servidor = ('127.0.0.1', 8000)
    cliente_socket = socket(AF_INET, SOCK_DGRAM)
    print("[Info] Tentando conectar...")

    nome = input("\nDigite seu nome: ")
    mensagem_nome = nome.encode()
    cliente_socket.sendto(mensagem_nome, servidor)

    aguardar_servidor = threading.Thread(target=response_servidor, args=[cliente_socket, servidor])
    aguardar_servidor.start()

    aguardar_mensagem = threading.Thread(target=enviar_mensagem, args=[cliente_socket, servidor])
    aguardar_mensagem.start()



if __name__ == "__main__":
    main()
