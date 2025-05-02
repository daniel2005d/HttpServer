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
        self.prompt = '$ '
        self._flask_proc = None
        self._server = None
        self.port = args.port
        self.folder = args.folder or os.getcwd()
        self._start_folder = self.folder
        self._start_http_server()
        
        #self.register_cmdfinalization_hook(self._postcmd)

    def _start_http_server(self):
        self._server = Server(self.port, self.folder)
        self._server.start()
    
    def run_command(self, command):
        #self.poutput(f"{Fore.yellow}Result from {Style.bold}{Style.reset}{command} {Fore.yellow}command {Style.reset}\n")
        result = subprocess.run(["bash","-c", command],  capture_output=True, text=True)
        output = result.stdout.strip() or result.stderr.strip()
        self.poutput(output)
    
    def complete_cd(self, text, line, begidx, endidx):
        """Autocompleta directorios como Bash."""
        if not text:
            text = ''
        else:
            text = os.path.expanduser(text)

        # Obtén la parte base y el directorio a listar
        dirname = os.path.dirname(text)
        prefix = os.path.basename(text)

        if not dirname:
            dirname = '.'

        try:
            entries = os.listdir(dirname)
        except FileNotFoundError:
            return []

        completions = []
        for entry in entries:
            full_path = os.path.join(dirname, entry)
            if os.path.isdir(full_path) and entry.startswith(prefix):
                suggestion = os.path.join(dirname, entry)
                if not suggestion.startswith('/'):
                    suggestion = os.path.relpath(suggestion)
                completions.append(suggestion + os.sep)

        return completions
    
    def postcmd(self, stop, line):
        self.prompt = f'[{Fore.green_yellow}{self._server.get_folder()}{Style.reset}]> '
    
    def do_cd(self, command):
        directory = command.args.strip()
        if directory == '':
            directory = self._start_folder

        if os.path.exists(directory):
            self._server.set_folder(directory)
            self.run_command(f"cd {self._server.get_folder()}")
            os.chdir(directory)
        else:
            print(f"{Style.red}Directory {directory} does not exists{Style.reset}")
    
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
    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--port", default=8000)
    parser.add_argument("-f","--folder")
    args = parser.parse_args()

    app = App(args)
    sys.exit(app.cmdloop())

if __name__ == '__main__':
    main()