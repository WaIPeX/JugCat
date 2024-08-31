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
    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)
        try:
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()

    def listen(self):
        print('listening')
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()

    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                    print(len(file_buffer))
                else:
                    break
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())

        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b' #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()                


logo = """

       ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░ ░▒▓██████▓▒░ ░▒▓██████▓▒░▒▓████████▓▒░ 
       ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░     
       ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░     
       ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒▒▓███▓▒░▒▓█▓▒░      ░▒▓████████▓▒░ ░▒▓█▓▒░     
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░     
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░     
 ░▒▓██████▓▒░ ░▒▓██████▓▒░ ░▒▓██████▓▒░ ░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░     
                                                                               
                                    ／l_             
                                    （ﾟ､ ｡７         
                                    l  ~ヽ       
                                    じしf_,)ノ                          
                                ,*#%%#####/    #%##(        
                                ,,,,/,,/(((/(##(   (#//    
                                /,.,/##%%#/(         /#   
                                //.*#%((####         */   
                                #,.**%/%###%((        #/   
                            //**,*//#&/%%/#%#/     #/    
                            ,(.,,/,*(#%&#######%  %(      
                            (/*  ,//(/%#%(#/#/(%#%%(       
                            */...,/((/%##%(##%#(##         
                            , *..,/#(##%###%###%(#         
                            /(*,**.#/##%(/%%#%%(%          
                            */*(//(%/%((%%%%%(           
                                /*/**(#/((#%#(%                                                       
"""



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
        description= logo + '\nJugCat - Simple NClike tool, I hope it will be netcat compatibile',
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
