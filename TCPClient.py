import socket

Target_Host = '127.0.0.1'
Taget_Port = 9998

# Create instance from the socket class
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# Connect to the server
client.connect((Target_Host,Taget_Port))

# Send data
client.send(b'Send ACK please')

# Receive response
response = client.recv(4096)

print(response.decode())
client.close()
