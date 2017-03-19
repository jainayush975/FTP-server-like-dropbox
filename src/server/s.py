import socket
import os

port = 60000
s = socket.socket()
host = ""

s.bind((host, port))
s.listen(5)

#sfilename = raw_input("Enter file to share:")
print 'Server listening....'
conn, addr = s.accept()
while True:
    print 'Got connection from', addr
    data = conn.recv(1024)
    print data
    print 'Server received', data

    tosend = ""

    data = data.split(" ")

    if data[0] == "index":
        ans = os.listdir("./")
        print "inside", ans
        for string in ans:
            tosend = tosend + string + "\n"
        conn.send(tosend)

    elif data[0] == 'hash':
        if data[1] == "verify":
            tosend = os.popen("cksum " + data[2]).read()
            conn.send(tosend)
    else:
        print "send valid command"
    print('Done sending')
conn.close()

s.close()
exit()
