import os
import argparse
from glob import glob
from flask import Flask, request, render_template, send_file
from waitress import serve
import threading
from datetime import date
from colored import Fore, Style, Back
import os

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
    
class Server:
    def __init__(self, port:int, folder:str):
        self.app = Flask(__name__)
        self.operations = Operations(folder)
        self.port = port
        self.folder = folder

        @self.app.route('/<file>', methods=['GET'])
        @self.app.route('/', methods=['GET','POST'])
        def index(file:str=None):
            try:
                client_ip = request.headers.get('X-Forwarded-For') or request.headers.get('X-Real-IP') or request.remote_addr
                current_date = date.today().strftime("%d/%b/%Y %H:%M:%S")
                status_code = 200
                message_code = "OK"
                color = Fore.black
                if request.method == 'GET':
                    if file:
                        file_name = os.path.join(self.folder, file)
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
                        return self.operations.files_list()
                else:
                    message_code,status_code = self.operations.upload(request.files['file'])

                print(f'{Back.white} {color}{client_ip} - - [{current_date} ] "{request.method} /{file} HTTP/1.1" {status_code}-{message_code} {Style.reset}')
            except Exception as e:
                message_code = str(e)
                status_code = 500

            return message_code, status_code
    
    def set_folder(self, folder:str):
        self.folder = folder
        print(f"New folder {self.folder} set.")
    
    def get_folder(self):
        return self.folder
    
    def _print_banner(self):
        banner = """
         _   _ _____ ___________  _____                          
        | | | |_   _|_   _| ___ \/  ___|                         
        | |_| | | |   | | | |_/ /\ `--.  ___ _ ____   _____ _ __ 
        |  _  | | |   | | |  __/  `--. \/ _ \ '__\ \ / / _ \ '__|
        | | | | | |   | | | |    /\__/ /  __/ |   \ V /  __/ |   
        \_| |_/ \_/   \_/ \_|    \____/ \___|_|    \_/ \___|_|   
        """
        print(banner)
        print(f"{Fore.cyan}Exposed Folder: {Style.bold}{self.folder}{Style.reset}")
        print(f"{Fore.yellow}Running on: {Style.bold}http://0.0.0.0:{self.port}{Style.reset}")
        print(f"{Fore.green}Current directory: {Style.bold}{os.getcwd()}{Style.reset}")

    def start(self):
        self._print_banner()
        def run_flask():
            #serve(self.app.run(port=self.port))
            serve(self.app, host="0.0.0.0", port=self.port)
            

        thread = threading.Thread(target=run_flask)
        thread.daemon = True
        thread.start()
