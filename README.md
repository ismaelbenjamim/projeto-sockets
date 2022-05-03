﻿# Projeto de Sockets
<p>Projeto de redes utilizando os protocolos TCP e UDP para a criação de aplicações.</p>
<p><i>Autores do projeto: Ismael Benjamim e Tiago Bello</i></p>
<hr>
<h3>Aplicação de Quiz com UDP</h3>
<p>Criamos um quiz competitivo com dois temas que podem ser escolhidos pelos jogadores, por padrão o tema do quiz é  o de atualidades, porém o tema de entretenimento pode ser escolhido nas configurações iniciais do jogo, assim como o número de participantes, caso o usuário queira configurar de acordo com sua vontade, porém, por padrão o jogo define 5 usuário como o normal. 
Cada tema possui uma lista de 20 perguntas a serem respondidas com uma única palavra pelo usuário, assim que respondida corretamente, o quiz trava os outros usuários de responderem e passa para a próxima pergunta. As regras de pontuação foram as mesmas orientadas nas regras de projeto, onde cada resposta certa são 25 pontos positivos, cada errada são menos 5 e se não houver resposta na rodada é menos 1 ponto. 
O projeto se utiliza do socket UDP para fazer a comunicação cliente servidor, visto que não é orientado a web e não há necessidade da proteção de dados fornecida pelo TCP, como também por ser um jogo de velocidade de resposta, é necessário que a comunicação seja a mais eficiente possível.</p>
<hr>
<h3>Aplicação WEB com TCP</h3>
<p>O objetivo principal deste projeto é abrir um servidor web utilizando o protocolo TCP e fazer com que esta aplicação retorne pastas de diversos tipos e tamanhos ao usuário. Além disso, também tem como finalidade tratar os códigos básicos do protocolo HTTP, tal como o 200 ok, que sinaliza que a comunicação foi estabelecida de forma correta, o 400 bad request que indica que o servidor não pôde processar a requisição, o 404 not found quando uma requisição não pôde ser encontrada e o status 500 que indica um erro em alguma base que tem como função fazer o servidor rodar. Por fim, o projeto analisa o protocolo HTTP e faz um filtro para apenas responder a requisições do http/1.1</p>
<hr>
