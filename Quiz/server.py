import socket

localIP = "127.0.0.1"
localPort = 80
bufferSize = 1024

# Create a datagram socket
socket_servidor = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
socket_servidor.bind((localIP, localPort))

print("Servidor UDP ligado")

while True:
    dados = socket_servidor.recvfrom(1024)

    message = dados[0]
    address = dados[1]

    resposta = ''
    resposta += 'HTTP/1.1 200 OK\r\n'
    resposta += 'Content-Type: text/html\r\n'
    resposta += '\r\n'

    html = ''
    html += '<html>'
    html += '<head>'
    html += '<title>Página Teste - CIn/UFPE</title>'
    html += '<meta charset="UTF-8">'
    html += '</head>'
    html += '<body>'
    html += '<h1>Hello World</h1>'
    html += '<h2>Hello World</h2>'
    html += '<h3>Hello World</h3>'
    html += '</body>'
    html += '</html>'

    resposta += html

    socket_servidor.send(resposta.encode(), address)
    socket_servidor.close()
