import socket
import re

def bringFile(type, filename):
    with open(filename, 'wb') as f:
        while True:
            try:
                s.settimeout(1.0)
                data = s.recv(1024)
            except:
                break
            f.write(data)
    f.close()
    s.settimeout(None)
    print "Done Recieving File!!!"


s = socket.socket()
host = ""
port = 60000

s.connect((host, port))

while True:
    command = raw_input("enter command $ ")
    s.send(command)
    command = re.split(r'\s{1,}', command)
    if command[0] == "download":
        bringFile(command[1], command[2])
    elif command[0] == "close":
        break
    else:
        data = s.recv(1024)
        print data

s.close()
print('connection closed')
