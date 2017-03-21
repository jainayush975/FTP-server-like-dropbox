import socket
import os
import re
import os.path, time

def checkRegex(pattern, string):
    string = re.split(r'\s{1,}', string)
    if len(string)==9:
        m = re.search(pattern,string[8])
        if m is not None:
            return True
    return False

def handelDownload(type, filename):

    f = open(filename, 'rb')
    l = f.read(1024)
    while (l):
        conn.send(l)
        l = f.read(1024)
    f.close()

port = 60000
s = socket.socket()
host = ""

s.bind((host, port))
s.listen(5)

print 'Server listening....'
conn, addr = s.accept()
while True:
    print 'Got connection from', addr
    data = conn.recv(1024)
    print data
    print 'Server received', data

    tosend = ""

    data = data.split(" ")

    if data[0] == "close":
        break;

    elif data[0] == "index":
        if data[1] == "shortlist":
            ans = os.popen("ls -1").read()
            lsresult = ans.split("\n")
            print lsresult
            for string in lsresult:
                tosend = tosend + string + "\n"
            conn.send(tosend)
        elif data[1] == "longlist":
            ans = os.popen("ls -l").read()
            lsresult = ans.split("\n")
            lsresult.remove(lsresult[0])
            for string in lsresult:
                    tosend = tosend + string + "\n"
            conn.send(tosend)
        elif data[1] == "regex":
            ans = os.popen("ls -l").read()
            lsresult = ans.split("\n")
            lsresult.remove(lsresult[0])
            for string in lsresult:
                if checkRegex(data[2], string):
                    tosend = tosend + string + "\n"
            conn.send(tosend)


    elif data[0] == "hash":
        if data[1] == "verify":
            filename = data[2]
            hashv = os.popen("md5sum " + filename).read()
            timestamp = time.ctime(os.path.getmtime(filename))
            tosend = "Hash Value is: " + hashv + "\nTime Stamp is: " + timestamp
            conn.send(tosend)
        elif data[1] == "checkall":
            tosend = ""
            files = os.listdir("./")
            for filename in files:
                hashv = os.popen("md5sum " + filename).read()
                timestamp = time.ctime(os.path.getmtime(filename))
                fileout = "Hash Value is: " + hashv + "Time Stamp is: " + timestamp
                tosend = tosend + "For File " + filename + "\n" + fileout + "\n"
            conn.send(tosend)

    elif data[0] == "download":
        handelDownload(data[1], data[2])

    else:
        conn.send("send valid command")
        print "send valid command"
    print('Done sending')
print "server closed come back soon!"
conn.close()
s.close()
exit()
