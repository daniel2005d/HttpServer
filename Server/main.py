import os
import argparse
from glob import glob
from flask import Flask, request, render_template, send_file
from waitress import serve
from datetime import date
from colored import Fore, Style, Back

class Operations:
    def __init__(self, folder:str):
        self._folder = folder

    def file_size(self, filename:str):
        size_bytes = os.path.getsize(filename)

        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < (1024 * 1024):
            size_kb = size_bytes / 1024
            return f"{size_kb:.2f} KB"
        elif size_bytes < (1024 * 1024 * 1024):
            size_mb = size_bytes / (1024 * 1024)
            return f"{size_mb:.2f} MB"
        else:
            size_gb = size_bytes / (1024 * 1024 * 1024)
            return f"{size_gb:.2f} GB"

    def upload(self, file):
        file.save(os.path.join(self._folder, file.filename))
        return "OK", 200

    def files_list(self):
        files = []
        for file in glob(f'{self._folder}/*.*'):
            if os.path.exists(file):
                files.append({
                    'name':os.path.basename(file),
                    "size": self.file_size(file)
                })
        
        return render_template('files.html',files=files)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--port", default=8000)
    parser.add_argument("-f","--folder")
    args = parser.parse_args()

    folder = None
    if args.folder:
        folder = args.folder
    else:
        folder = os.getcwd()

    app = Flask(__name__)

    operations = Operations(folder)

    @app.route('/<file>', methods=['GET'])
    @app.route('/', methods=['GET','POST'])
    def index(file:str=None):
        client_ip = request.headers.get('X-Forwarded-For') or request.headers.get('X-Real-IP') or request.remote_addr
        current_date = date.today().strftime("%d/%b/%Y %H:%M:%S")
        status_code = 200
        message_code = "OK"
        color = Fore.black
        if request.method == 'GET':
            if file:
                file_name = os.path.join(folder, file)
                if os.path.exists(file_name):
                    response = send_file(file_name, as_attachment=True)
                    print(f'{Back.white} {color}{client_ip} - - [{current_date} ] "{request.method} /{file} HTTP/1.1 {response.status_code}" {Style.reset}')
                    return response
                    
                else:
                    color = Fore.red
                    message_code = "Not Found"
                    status_code = 404
                
            else:
                print(f'{Back.white} {color}{client_ip} - - [{current_date} ] "{request.method} /{file} HTTP/1.1 200 OK" {Style.reset}')
                return operations.files_list()
        else:
            message_code,status_code = operations.upload(request.files['file'])

        print(f'{Back.white} {color}{client_ip} - - [{current_date} ] "{request.method} /{file} HTTP/1.1" {status_code}-{message_code} {Style.reset}')
        return message_code, status_code

    

    #app.debug = True
    print(f"Serving HTTP on 0.0.0.0 port {args.port} (http://0.0.0.0:{args.port}/) ..")
    print(f"Folder {folder}")
    serve(app, host="0.0.0.0", port=args.port)

if __name__ == '__main__':
    main()