from cmd2 import Cmd
import os
import sys
from waitress import serve
from colored import Fore, Style, Back
from datetime import date
import argparse
import subprocess
from server import Server

class App(Cmd):
    def __init__(self, args, **kwargs):
        super().__init__(**kwargs)
        self._DEFAULT_PATHS = ["/usr/share/windows-binaries","/opt/SharpCollection/","/opt/nishang/"]
        self.prompt = '$ '
        self._flask_proc = None
        self._server = None
        self.port = args.port
        self.folder = args.folder or os.getcwd()
        #self.do_cd(self.folder)
        self._start_folder = self.folder
        self._start_http_server()
        if args.defaults:
            self._add_default_folders()
        

    def _start_http_server(self):
        self._server = Server(self.port)
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
    
    def complete_cd(self, text, line, begidx, endidx):
        """Autocompleta directorios como Bash sin espacio final."""
        text = os.path.expanduser(text or '')
        dirname = os.path.dirname(text) or '.'
        prefix = os.path.basename(text)

        try:
            entries = os.listdir(dirname)
        except FileNotFoundError:
            return []

        completions = []
        for entry in entries:
            full_path = os.path.join(dirname, entry)
            if os.path.isdir(full_path) and entry.startswith(prefix):
                suggestion = os.path.join(dirname, entry)
                # Asegura que sea relativo si es necesario
                suggestion = os.path.normpath(suggestion)
                # Agrega '/' solo si no está al final
                if not suggestion.endswith(os.sep):
                    suggestion += os.sep
                completions.append(suggestion)

        return completions

    def complete_add(self, text, line, begidx, endidx):
        if text.startswith('def'):
            return ['defaults']
        else:
            return self.complete_cd(text, line, begidx, endidx)
    
    def postcmd(self, stop, line):
        self._set_prompt()
    
    def do_history(self, command):
        history = self._server.get_history()
        for h in history:
            icon = '📤' if h["upload"] else '📥'
            name = h["name"]
            print(f'{icon} {name}')

    def do_info(self, command):
        paths = self._server.get_paths()
        for index, p in enumerate(paths):
            print(f"{Fore.green}[{index}]{Fore.orange_red_1} {p}{Style.reset}")

    def do_add(self, command):
        directory = command.args.strip()
        if directory == 'defaults':
            self._add_default_folders()
        else:
            self._server.add_path(directory)
    
    def do_search(self, command):
        paths = self._server.get_paths()
        for path in paths:
            for root, dirs, files in os.walk(path):
                if command in files:
                    print(f"{Fore.chartreuse_1}[+] {os.path.join(root, command)}{Style.reset}") 

    
    def do_cd(self, command):
        directory = command.args.strip()
        if directory.isdigit():
            paths = self._server.get_paths()
            directory = paths[int(directory)]
            os.chdir(directory)
        else:
            if directory == '':
                directory = self._start_folder

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
    print(f"{Fore.chartreuse_1}[*] Version {Style.bold}1.11{Style.reset}")
    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--port", default=8000)
    parser.add_argument("-f","--folder")
    parser.add_argument("-d","--defaults",help="Add default folders", action='store_true')
    args = parser.parse_args()
    sys.argv = [sys.argv[0]] # Clean argv to prevent default function execute first time

    app = App(args=args)
    sys.exit(app.cmdloop())

if __name__ == '__main__':
    main()