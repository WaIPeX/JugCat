import threading
import subprocess

import sys
import socket

import textwrap
import argparse
import shlex

class JugCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd), stderr = subprocess.STDOUT)
    return output.decode()
# Run and check output of command on local machine


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='JugCat',
        description='JugCat - Simple NClike tool, I hope it will be netcat compatibile',
        formatter_class= argparse.RawDescriptionHelpFormatter,
        epilog = textwrap.dedent('''Usage examples:
                    jugcat.py -t 192.168.1.101 -p 4444 -l -c                     # Listen for command shell output
                    jugcat.py -t 192.168.1.101 -p 4444 -l -e=\"cat /etc/passwd\" # Execute command and listen for output
                    jugcat.py -t 192.168.1.101 -p 4444 -l -u= testfile.txt       # Upload 
                    jugcat.py -t 192.168.209.1 -p 4444                           # Connect to server
                    echo 'Example' | ./jugcat.py -t 192.168.209.1 -p 135         # Echo message to server on port 135                                 
'''))
# Basic argparse, name description etc.    

parser.add_argument('-c','--command', action='store_true', help='Use Command Shell arg')
parser.add_argument('-l','--listen', action='store_true', help = 'Listen')
parser.add_argument('-u','--upload', help = 'Upload file')
parser.add_argument('-p','--port',type = int, default = 4444, help = 'Port')
parser.add_argument('-t','--target', help = 'IP Address of target')
parser.add_argument('-e','--execute', help = 'Execute this command')
args = parser.parse_args()
# Parser arguments to use when using commands
if args.listen:
    buffer = ''
# Buffer empty
else:
    buffer = sys.stdin.read()
    jc = JugCat(args, buffer.encode)
    jc.run()