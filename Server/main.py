from cmd2 import Cmd
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
        self.port = args.port
        self.folder = args.folder
        self._start_http_server()

    def _start_http_server(self):
        server = Server(self.port, self.folder)
        server.start()
    
    def default(self, line):
        try:
            if line.command:
                self.poutput(f"{Fore.yellow}Result from {Style.bold}{Style.reset}{line.raw} {Fore.yellow}command {Style.reset}\n")
                result = subprocess.run(["bash","-c",line.raw],  capture_output=True, text=True)
                output = result.stdout.strip() or result.stderr.strip()
                self.poutput(output)
        except Exception as e:
            self.poutput(f"❌ Error: {e}")
    
    def do_exit(self, command):
        return True
    


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--port", default=8000)
    parser.add_argument("-f","--folder")
    args = parser.parse_args()

    app = App(args)
    sys.exit(app.cmdloop())

if __name__ == '__main__':
    main()