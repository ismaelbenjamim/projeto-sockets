import os
import threading
import urllib.parse
from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM


class Server:
    def __init__(self, ip, port, default_dir_path="files"):
        self.ip = ip
        self.port = port
        self.socket_server = None
        self.client = None
        self.prefix = '[Solu WebApp]'
        self.default_dir_path = default_dir_path
        self.root_path = self.get_root_path()
        self.server_on = True

    def start_server(self):
        print(f"----------------------------------------------")
        print(f"Projeto com Sockets - Servidor WEB v1.0")
        print(f"Server iniciado com sucesso: http://{self.ip}:{self.port}")
        print(f"Desenvolvido por: Ismael Benjamim e Tiago Bello")
        print(f"----------------------------------------------")
        self.socket_server = socket(AF_INET, SOCK_STREAM)
        self.socket_server.bind((self.ip, self.port))
        self.socket_server.listen(2)

        self.create_dir_default()

        while self.server_on:
            client, endereco_cliente = self.socket_server.accept()
            server = threading.Thread(target=self.server, args=[client])
            server.start()

    def get_root_path(self):
        project_file_path = __file__
        project_file_name = os.path.basename(__file__)
        root_path = str(project_file_path).replace(str(project_file_name), "")
        return root_path

    def create_dir_default(self):
        path_exists = os.path.exists(self.default_dir_path)
        if path_exists:
            print(self.prefix, f'O diretório "{self.default_dir_path}" foi encontrado!')
        else:
            os.mkdir(self.default_dir_path)
            print(self.prefix, f'O diretório "{self.default_dir_path}" não foi encontrado, portanto foi criado!')

    def request(self, client):
        if not client:
            return None

        data = str(client.decode()).split(' ')
        http_type = str(data[2]).split("\n")[0]
        response = {
            "path": data[1],
            "method": data[0],
            "http_type": http_type
        }
        return response

    def get_mime_type(self, file_path):
        import mimetypes
        mimetype = mimetypes.guess_type(file_path)
        return mimetype[0]

    def get_status_code(self, status):
        if status == 200:
            response = "200 OK"
        elif status == 400:
            response = "400 Bad Request"
        elif status == 404:
            response = "404 Not Found"
        else:
            response = "505 HTTP Version Not Supported"
        return response

    def get_file(self, file_name, file_path):
        try:
            file_name = urllib.parse.unquote(file_name)
            file = open(file_name, 'rb')
            body = file.read()
            file.close()
            status = self.get_status_code(200)
            header = f'HTTP/1.1 {status}\n'
            mimetype = self.get_mime_type(file_path)
            header += 'Content-Type: ' + str(mimetype) + '\n\n'
            return {"header": header, "body": body}
        except:
            url_decode = urllib.parse.unquote(file_name)
            return 400 if "%" or "{" in url_decode else 404

    def convert_bytes_to_kb(self, size_in_bytes):
        return size_in_bytes / 1024

    def get_response(self, file_path, error=None):
        if error == 505:
            file = open(f'505.html', 'rb')
            body = file.read()
            file.close()
            status = self.get_status_code(505)
        else:
            path_exists = os.path.exists(file_path[1:])
            if path_exists:
                isdir = os.path.isdir(file_path[1:])
                if not "/" == file_path[-1]:
                    file_path = file_path + "/"
                if isdir:
                    files_dir = os.listdir(str(file_path.removeprefix("/")))
                else:
                    files_dir = []

                path_in_list = str(file_path).split("/")
                last_dir_path = path_in_list[-2] + "/"

                file = open(f'navigation.html', 'rb')
                body = file.read()
                body = body.decode()

                files_navigation = ""
                for file_dir in files_dir:
                    path = f'{file_path[1:]}{file_dir}'
                    last_modified = datetime.fromtimestamp(os.path.getmtime(path))
                    size = round(self.convert_bytes_to_kb(os.path.getsize(path)), 2)
                    files_navigation += f'<tr><td><a href="/{path}" style="color: white;">{file_dir}</a></td>' \
                                        f'<td>{last_modified.strftime("%d/%m/%Y - %H:%M")}</td>' \
                                        f'<td>{size} KB</td>' \
                                        f'<td></td></tr>'

                body = body.replace("{{ files }}", files_navigation)
                body = body.replace("{{ file_path }}", file_path)
                body = body.replace("{{ file_path_back }}", file_path.replace(last_dir_path, ""))
                body = body.encode('utf-8')
                file.close()
                status = self.get_status_code(200)
            else:
                if error == 400:
                    file = open(f'400.html', 'rb')
                    body = file.read()
                    file.close()
                    status = self.get_status_code(400)
                else:
                    file = open(f'404.html', 'rb')
                    body = file.read()
                    file.close()
                    status = self.get_status_code(404)
        response = {}
        response['header'] = f'HTTP/1.1 {status}\n\n'
        response['body'] = body
        return response


    def server(self, client):
        while True:
            request = self.request(client.recv(2048))
            if not request:
                break

            params = {}

            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print(self.prefix, f'[{current_time}]', request['path'], request['method'])
            file_path = request['path'].split('?')[0]

            if '?' in request['path']:
                params_url = (request['path'].split('?')[1]).split('&')
                for param_url in params_url:
                    param = param_url.split('=')
                    params[param[0]] = param[1]

            if params.get('stop'):
                self.server_on = False
                break

            file_name = file_path.lstrip('/')
            file_name = f'index.html' if file_name == '' else file_name

            if not request['http_type'] != "HTTP/1.1":
                response = self.get_response(f"{file_path}", 505)
            else:
                response = self.get_file(f"{file_name}", file_path)

                if response == 400 or response == 404:
                    response = self.get_response(f"{file_path}", response)

            client.send(response['header'].encode('utf-8') + response['body'])
            break

        client.close()


def main():
    server = Server("localhost", 80, "files")
    server.start_server()


if __name__ == "__main__":
    main()
