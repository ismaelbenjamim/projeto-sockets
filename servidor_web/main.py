from _thread import *
import logging
from socket import socket, AF_INET, SOCK_STREAM

ip = "localhost"
index = 'index.html'
style = 'assets/style.css'
porta = 80

def server(socket_cliente, numero_thread, socket_servidor):
    while True:
        dados = socket_cliente.recv(2048)

        if not dados:
            break

        mensagem = dados.decode()
        string_list = mensagem.split(' ')
        method = string_list[0]
        requesting_file = string_list[1]
        parametros = {}
        print('Requisição do cliente:', requesting_file, method)
        myfile = requesting_file.split('?')[0]

        if '?' in requesting_file:
            parametros_url = (requesting_file.split('?')[1]).split('&')
            for param in parametros_url:
                parametro = param.split('=')
                parametros[parametro[0]] = parametro[1]

        if parametros.get('acao') == 'cancelar':
            break

        myfile = myfile.lstrip('/')
        if (myfile == ''):
            myfile = 'index.html'  # Load index file as default

        try:
            file = open(myfile, 'rb')  # open file , r => read , b => byte format
            response = file.read()
            file.close()

            header = 'HTTP/1.1 200 OK\n'

            if (myfile.endswith(".jpg")):
                mimetype = 'image/jpg'
            elif (myfile.endswith(".css")):
                mimetype = 'text/css'
            else:
                mimetype = 'text/html'

            header += 'Content-Type: ' + str(mimetype) + '\n\n'

        except Exception as e:
            header = 'HTTP/1.1 404 Not Found\n\n'
            response = '<html><body><center><h3>Error 404: File not found</h3><p>Python HTTP Server</p></center></body></html>'.encode(
                'utf-8')

        final_response = header.encode('utf-8')
        final_response += response
        socket_cliente.send(final_response)
        break

    socket_cliente.close()
    logging.info("Thread %s: finalizada", numero_thread)


def main():
    socket_servidor = socket(AF_INET, SOCK_STREAM)
    socket_servidor.bind((ip, porta))
    socket_servidor.listen(2)

    numero_thread = 0

    while True:
        socket_cliente, endereco_cliente = socket_servidor.accept()
        print(f'Conectado com: {endereco_cliente[0]}:{endereco_cliente[1]}')
        numero_thread += 1
        logging.info("Thread %s: iniciada", numero_thread)
        start_new_thread(server, (socket_cliente, numero_thread, socket_servidor))

if __name__ == "__main__":
    print(f"----------------------------------------------")
    print(f"Projeto com Sockets - Servidor WEB v1.0")
    print(f"Server iniciado com sucesso: http://{ip}:{porta}")
    print(f"Desenvolvido por: Ismael Benjamim e Tiago Bello")
    print(f"----------------------------------------------")
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    main()
