import socket

s = socket.socket()
host = ""
port = 60000

s.connect((host, port))

while True:
    command = raw_input("enter command $ ")
    if command == "close":
        break
    s.send(command)
    data = s.recv(1024)
    print data

s.close()
print('Successfully get the file')
print('connection closed')
