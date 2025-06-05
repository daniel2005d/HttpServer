from cmd2 import Cmd, with_argparser
import os
import sys
from waitress import serve
from colored import Fore, Style, Back
from datetime import date
import argparse
import subprocess
from server import Server
from settings import Settings
import json

class App(Cmd):
    def __init__(self, args, **kwargs):
        super().__init__(**kwargs)
        self._DEFAULT_PATHS = ["/usr/share/windows-binaries","/opt/SharpCollection/","/opt/nishang/","../Client/Releases/"]
        self._CONFIG_FILE = os.path.join(os.path.expanduser("~/.config"),"httpserver.conf")
        self.prompt = '$ '
        self._flask_proc = None
        self._server = None
        self.port = args.port
        self._start_http_server()
        if args.defaults:
            self._add_default_folders()
        
        if not args.ignore_config:
            self._load_config()

        self.folder = Settings.initial_folder

    def _load_config(self):
        if os.path.exists(self._CONFIG_FILE):
            print(f"[+] {Fore.chartreuse_1} Config file exists. Opening from this settings {Style.bold}{self._CONFIG_FILE}{Style.reset}")
            Settings.from_json(self._CONFIG_FILE)

    def _start_http_server(self):
        self._server = Server()
        self._server.start()
    
    def _add_default_folders(self):
        for path in self._DEFAULT_PATHS:
            if os.path.exists(path):
                print(f"[+] Adding default folder {path}")
                self._server.add_path(path)

    def _set_prompt(self):
        self.prompt = f'[{Fore.green_yellow}{os.getcwd()}{Style.reset}]> '

    def run_command(self, command):
        result = subprocess.run(["bash","-c", command],  capture_output=True, text=True)
        output = result.stdout.strip() or result.stderr.strip()
        self.poutput(output)
    
    def preloop(self):
        self.onecmd(f'cd {self.folder}')
        self._set_prompt()

    def postcmd(self, stop, line):
        self._set_prompt()
    
    def do_history(self, command):
        history = self._server.get_history()
        for h in history:
            icon = '📤' if h["upload"] else '📥'
            name = h["name"]
            print(f'{icon} {name}')

    def do_info(self, command):
        
        for index, p in enumerate(Settings.paths):
            print(f"{Fore.green}[{index}]{Fore.orange_red_1} {p}{Style.reset}")

    def do_add(self, command):
        directory = command.args.strip()
        if directory == 'defaults':
            self._add_default_folders()
        else:
            self._server.add_path(directory)
    
    def do_search(self, command):
        
        for path in Settings.paths:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.lower().startswith(command.lower()):
                        print(f"{Fore.chartreuse_1}[+] {os.path.join(root, file)}{Style.reset}") 
    
    """
    Save configuration settings
    """
    def do_save(self, command):
        with open(self._CONFIG_FILE, 'w') as config:
            config.write(Settings.to_json())
        
        print(f"[+] {Fore.chartreuse_1} Config file saved on {Style.bold}{self._CONFIG_FILE}{Style.reset}")

    complete_cd = Cmd.path_complete
    complete_add = Cmd.path_complete
    

    def do_cd(self, command):
        directory = command.args.strip()
        if directory.isdigit():
            paths = Settings.paths
            directory = paths[int(directory)]
            os.chdir(directory)
        else:
            if directory == '':
                directory = Settings.initial_folder

            if os.path.exists(directory):
                self._server.add_path(directory)
                os.chdir(directory)
            else:
                print(f"{Fore.red}Directory {directory} does not exists{Style.reset}")
    
    def default(self, line):
        try:
            if line.command:
                command = ''
                if line.command == 'ls':
                    command = f'{line.raw}  -lh --color --group-directories-first'
                else:
                    command = line.raw

                self.run_command(command)
        except Exception as e:
            self.poutput(f"❌ Error: {e}")
    
    def do_exit(self, command):
        sys.exit(0)
    


def main():
    print(f"{Fore.chartreuse_1}[*] Version {Style.bold}1.2{Style.reset}")
    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--port", default=8000)
    parser.add_argument("-f","--folder")
    parser.add_argument("-d","--defaults",help="Add default folders", action='store_true')
    parser.add_argument('-i','--ignore-config',action='store_true')
    args = parser.parse_args()
    sys.argv = [sys.argv[0]] # Clean argv to prevent default function execute first time
    Settings.port = args.port
    if args.folder:
        Settings.initial_folder = args.folder
    app = App(args=args)
    sys.exit(app.cmdloop())

if __name__ == '__main__':
    main()