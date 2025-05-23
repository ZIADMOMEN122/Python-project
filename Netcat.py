import argparse
import socket
import sys
import subprocess
import shlex
import textwrap
import threading
import os

class NetCat:

    def __init__(self,args,buffer=None):

        self.args = args
        self.buffer = buffer
        
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    def run(self):

        if self.args.listen:
            self.listen()
        else:
            self.send()
    
    def send(self):

        self.socket.connect((self.args.target,self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)
        
        try:

            while True:
                recv_len = 1
                response = ''

                while recv_len < 4096:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break

                if response:
                    print(response)
                    buffer = input('>')
                    buffer += '\n'

                    self.socket.send(buffer.encode())


        except KeyboardInterrupt:

            print('User terminated.')
            self.socket.close()
            sys.exit()
    
    def listen(self):
        self.socket.bind((self.args.target,self.args.port))
        self.socket.listen(5)

        while True:

            Client,_ = self.socket.accept()
            client_handel = threading.Thread(target=self.client_handler,args=(Client,))
            client_handel.start()
    
    
    def client_handler(self,client_socket):
        
        if self.args.execute:

            output = execute(self.args.execute)
            client_socket.send(output)

        elif self.args.upload:

            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            
            with open(self.args.upload,'wb') as f:
                f.write(file_buffer)
            
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())
        
        elif self.args.command:

            cmd_buffer = b''

            while True:

                try:
                    client_socket.send(b'Command:#>')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    
                    command = cmd_buffer.decode().strip()
                    if command.startswith('cd '):
                        path = command[3:].strip()
                        
                        try:

                            os.chdir(path)
                            current_dir = os.getcwd()
                            client_socket.send(f"Changed directory to {current_dir}\n".encode())
                            cmd_buffer = b''


                        except FileNotFoundError as e:
                            client_socket.send(f'Directory not found:{path}\n'.encode())
                    else:
                        response = execute(cmd_buffer.decode())
                        if response:
                            client_socket.send(response)
                            cmd_buffer = b''

                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()

                    

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return b''

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=False 
        )
        return result.stdout + result.stderr

    except Exception as e:
        return f"Error executing command: {str(e)}\n".encode()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description = 'Netcat tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog = textwrap.dedent('''Example:
                    
                netcat.py -t <target> -p <port> -l -c    # command shell
                netcat.py -t <target> -p <port> -l -u=mytest.txt   # Upload to a file
                netcat.py -t <target> -p <port> -l -e = \"cat /etc/passwd\"   # Execute a command
                echo "Test" | ./netcat.py -t <target> -p <port>     # Echo text to a server
                netcat.py -t <target> -p <port>    # connect to the server
                                 
        '''))
    parser.add_argument('-c','--command',action='store_true',help='command_shell')
    parser.add_argument('-e','--execute',help='Execute specified command')
    parser.add_argument('-l','--listen',action='store_true',help='listen')
    parser.add_argument('-p','--port',type=int,default=4444,help='Specified port')
    parser.add_argument('-t','--target',help='Specified IP')
    parser.add_argument('-u','--upload',help='Upload a file')

    args = parser.parse_args()

    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()
    
    nc = NetCat(args,buffer.encode())
    nc.run() 
