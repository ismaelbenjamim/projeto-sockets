from socket import socket, AF_INET, SOCK_DGRAM

def main():
    servidor = ('127.0.0.1', 8000)
    cliente_socket = socket(AF_INET, SOCK_DGRAM)
    print("[Info] Bem vindo ao Quiz")

    nome = input("\nDigite seu nome: ")
    mensagem_nome = nome.encode()
    cliente_socket.sendto(mensagem_nome, servidor)
    msg, endereco = cliente_socket.recvfrom(1024)
    print(msg.decode())

    while True:
        mensagem = input("\nDigite sua alternativa: ")

        if mensagem == 'sair':
            break

        mensagem_codificada = mensagem.encode()
        cliente_socket.sendto(mensagem_codificada, servidor)

        msg, endereco = cliente_socket.recvfrom(1024)
        print(msg.decode())

if __name__ == "__main__":
    main()
