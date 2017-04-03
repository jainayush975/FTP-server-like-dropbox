import socket
import os
import re
import os.path, time
from datetime import datetime
from threading import Thread
import threading
threads=[]
requesthistory=[]

class ServerSide(Thread):
    def __init__(self,ip,port,server_socket):
    	Thread.__init__(self)
    	self.ip=ip
    	self.port= port
    	self.server_socket = server_socket
    	self.server_on=True
    	#print "Server made here"

    def AbigB(self, timestamp1, timestamp2):
        t1 = datetime.strptime(timestamp1, "%b %d %H:%M")
        t2 = datetime.strptime(timestamp2, "%b %d %H:%M")
        if t1>=t2:
            return True
        return False

    def givemd5sum(self, filename):
        string = os.popen("md5sum " + filename).read()
        string = string.split(" ")
        return string[0]

    def giveTimeStamp(self, filename):
        return time.ctime(os.path.getmtime(filename))

    def handleShortList(self, data):
        t1 = data[2] + " " + data[3] + " " + data[4]
        t2 = data[5] + " " + data[6] + " " + data[7]

        tosend = ""
        ans = os.popen("ls -l").read()
        lsresult = ans.split("\n")
        for string in lsresult:
            string = re.split(r'\s{1,}', string)
            if len(string) == 9:
                t = string[5] + " " + string[6] + " " + string[7]
                if self.AbigB(t,t1) and self.AbigB(t2,t):
                    tosend = tosend + string[8] + "\n"
        return tosend

    def checkRegex(self, pattern, string):
        string = re.split(r'\s{1,}', string)
        if len(string)==9:
            m = re.search(pattern,string[8])
            if m is not None:
                return True
        return False

    def handelDownload(self, type, filename, conn):
        f = open(filename, 'rb')
        l = f.read(1024)
        while (l):
            conn.send(l)
            l = f.read(1024)
        f.close()

    def run(self):
        conn, addr = self.server_socket.accept()
        while True:
            data = conn.recv(1024)

            tosend = ""

            data = re.split(r'\s{1,}', data)

            if data[0] == "close":
                break;

            elif data[0] == "sync":
                tosend = os.popen("ls -l").read()
                conn.send(tosend)

            elif data[0] == "index":
                if data[1] == "shortlist":
                    tosend = self.handleShortList(data)
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
                        if self.checkRegex(data[2], string):
                            tosend = tosend + string + "\n"
                    conn.send(tosend)


            elif data[0] == "hash":
                if data[1] == "verify":
                    filename = data[2]
                    hashv = self.givemd5sum(filename)
                    timestamp = self.giveTimeStamp(filename)
                    tosend = "Hash Value is: " + hashv + "\nTime Stamp is: " + timestamp
                    conn.send(tosend)
                elif data[1] == "checkall":
                    tosend = ""
                    files = os.listdir("./")
                    for filename in files:
                        hashv = self.givemd5sum(filename)
                        timestamp = self.giveTimeStamp(filename)
                        fileout = "Hash Value is: " + hashv + "\nTime Stamp is: " + timestamp
                        tosend = tosend + "For File " + filename + "\n" + fileout + "\n"
                    conn.send(tosend)

            elif data[0] == "download":
                self.handelDownload(data[1], data[2], conn)

            else:
                conn.send("send valid command")
        conn.close()
        print "server closed come back soon!"


class ClientSide(Thread):
    def __init__(self,ip,port):
    	Thread.__init__(self)
    	self.ip = ip
    	self.port = port
    	self.is_running = True
        self.sync_on = False

    def AbigB(self, timestamp1, timestamp2):
        t1 = datetime.strptime(timestamp1, "%b %d %H:%M")
        t2 = datetime.strptime(timestamp2, "%b %d %H:%M")
        if t1>=t2:
            return True
        return False

    def bringFile(self, type, filename, s):
        with open(filename, 'wb') as f:
            while True:
                try:
                    s.settimeout(1.0)
                    data = s.recv(1024)
                except:
                    break
                f.write(data)
        s.settimeout(None)
        f.close()

    def syncIt(self, s, timer):
        print "\nSyncing Data........\n"
        s.send("sync")
        data = s.recv(1024)
        other_data = data.split("\n")
        other_data.remove(other_data[0])

        mydata = os.popen("ls -l").read()
        mydata = mydata.split("\n")
        mydata.remove(mydata[0])

        for ot in other_data:
            ot = re.split(r'\s{1,}', ot)
            if len(ot) == 9:
                if ot[8] != "server.py":
                    command = "download tcp " + ot[8]
                    tot = ot[5] + " " + ot[6] + " " + ot[7]
                    flag = False
                    for my in mydata:
                        my = re.split(r'\s{1,}', my)
                        if len(my) == 9:
                            tmy = my[5] + " " + my[6] + " " + my[7]
                            if my[8] == ot[8] and self.AbigB(tot, tmy):
                                s.send(command)
                                self.bringFile("TCP", ot[8], s)
                                flag = True
                    if flag == False:
                        command = "download tcp " + ot[8]
                        s.send(command)
                        self.bringFile("TCP", ot[8], s)
        print "enter command $ "
        threading.Timer(timer, self.syncIt, [s,timer]).start()

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip,self.port))
        while True:

            command = raw_input("enter command $ ")
            if command == "":
                continue
            if command[0] == "s":
                command = re.split(r'\s{1,}', command)
                self.syncIt(s, int(command[1]))
                continue
            s.send(command)
            command = re.split(r'\s{1,}', command)
            if command[0] == "download":
                self.bringFile(command[1], command[2], s)
                print command[2], "Recieving File!!!"
            elif command[0] == "close":
                break
            else:
                data = s.recv(1024)
                print data

        s.close()

server_ip='localhost'
server_prot=10001
server_protu=11001
client_ip='localhost'
client_prot= 9001
client_protu=12001
BUFFER_SIZE=1024

#Binding socket for TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
server_socket.bind((server_ip,server_prot))
server_socket.listen(5)

#Starting Server Thread
server=ServerSide(server_ip,server_prot,server_socket)
server.start()
threads.append(server)


print "wait for 5 sec until client tries to connect to other server"
time.sleep(5)


#Starting Client Thread
client=ClientSide(client_ip,client_prot)
client.start()
threads.append(client)
for t in threads:
	t.join()
server_socket.close()
