import socket
import threading

Listenning_IP = '0.0.0.0'
Listenning_Port = 9998

def main():

    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    # Bind the server to the IP an port to listen on
    server.bind((Listenning_IP,Listenning_Port))
    # Put the server in listenning mode, allowing up to 5 hosts in the queue
    server.listen(5)
    print(f'[*] Listening on {Listenning_IP}:{Listenning_Port}')

    while True:
        # Accept the incoming conection
        client,address = server.accept()
        print(f'[*] Accepted connection from {address[0]}:{address[1]}') # IP, Port
        client_handler = threading.Thread(target=handle_client,args=(client,))
        client_handler.start()

def handle_client(client_socket):

    with client_socket as sock:

        request = sock.recv(1024)
        print(f'[*] Received:{request.decode('utf-8')}')    
        sock.send(b'ACK')

if __name__ == '__main__':
    main()