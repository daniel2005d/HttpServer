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
        file.save(os.path.join(os.getcwd(), file.filename))
        return os.path.join(os.getcwd(), file.filename)

    def files_list(self):
        files = []
        for file in glob(f'{os.getcwd()}/*.*'):
            if os.path.exists(file):
                files.append({
                    'name':os.path.basename(file),
                    "size": self.file_size(file)
                })
        
        return render_template('files.html',files=files)
    
class Server:
    def __init__(self, port:int):
        self.app = Flask(__name__)
        self.operations = Operations(os.getcwd())
        self.port = port
        self._paths = []
        self.add_path(os.getcwd())
        self._history = []
    

        @self.app.route('/', methods=['GET','POST'])
        @self.app.route('/<path:file>', methods=['GET','POST'])
        def index(file:str=None):
            try:
                file_name = file
                status_code = 200
                message_code = "OK"
                
                if request.method == 'GET':
                    if file:
                        #file_name = os.path.join(os.getcwd(), file)
                        
                        for path in self._paths:
                            if os.path.exists(os.path.join(path, file)):
                                file_name = os.path.join(path, file)
                                self.add_path(file_name)
                                self._add_to_history(file_name)
                                response = send_file(file_name, as_attachment=True)
                                self._print(os.path.join(path, file), response.status_code, "OK", request)
                                return response
                            
                        else:
                            message_code = f"{file} Not Found"
                            status_code = 404
                        
                    else:
                        self._print(None, 200, "OK", request)
                        
                        return self.operations.files_list()
                else:
                    saved_file = self.operations.upload(request.files['file'])
                    self._add_to_history(saved_file, True)
                    print(f'\n[*] {Fore.light_cyan_1} File saved on {saved_file} {Style.reset}\n')

                    message_code = "OK"
                    status_code = 200

            except Exception as e:
                message_code = str(e)
                status_code = 500
            
            self._print(file_name, status_code, message_code, request)
            return message_code, status_code
    
    def _add_to_history(self, path, upload=False):
        if path not in self._history:
            self._history.append({
                'name':path,
                'upload':upload
            })
        
    def _print(self, filename,status_code=None,status_message='', request=None):

        client_ip = request.headers.get('X-Forwarded-For') or request.headers.get('X-Real-IP') or request.remote_addr
        current_date = date.today().strftime("%d/%b/%Y %H:%M:%S")
        color = None
        if status_code is not None:
            if status_code == 200:
                color = Fore.green
            elif status_code == 400 or status_code == 404:
                color = Fore.yellow
            elif status_code == 500:
                color = Fore.red

        print(f'{color}{client_ip} - - [{current_date} ] "{request.method} {Style.bold}/{filename}{Style.reset}{color} HTTP/1.1" {Fore.red_3b}{status_code}{Style.reset}-{status_message} {Style.reset}')


    def get_history(self):
        return self._history
    
    def add_path(self, path:str):
        
        if os.path.isdir(path):
            directory_name = path
        else:
            directory_name = os.path.dirname(path)
        
        if os.path.exists(directory_name):
            directory_name = os.path.abspath(directory_name)
            if directory_name not in self._paths:
                if path not in self._paths:
                    self._paths.append(directory_name)
        else:
            print(f"{Fore.red}[-] Directory {path} not exists{Style.reset}")
    
    def get_paths(self):
        return self._paths
    
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
        print(f"{Fore.cyan}Exposed Folder: {Style.bold}{os.getcwd()}{Style.reset}")
        print(f"{Fore.yellow}Running on: {Style.bold}http://0.0.0.0:{self.port}{Style.reset}")

    def start(self):
        self._print_banner()
        def run_flask():
            #serve(self.app.run(port=self.port))
            serve(self.app, host="0.0.0.0", port=self.port)
            

        thread = threading.Thread(target=run_flask)
        thread.daemon = True
        thread.start()
