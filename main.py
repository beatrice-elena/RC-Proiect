import socket
import threading
import socket
import struct
import time
import json
import ast
import sys
from tkinter import *
import tkinter as tk
import time
import multiprocessing
from tkinter.messagebox import showinfo

# clasa header reprezinta header-ul tabelei de rutare, conform RIPv2
class header:
    def __init__(self, command, virtualBoxId, tag, address, subnetMask):
        self.command = command
        self.version = 2
        self.setUnused = 0
        self.virtualBoxId = virtualBoxId
        self.afi = 2
        self.tag = tag
        self.address = address
        self.subnetMask = subnetMask

    def showH(self):
        print("Command:", self.command, " Version:", self.version, " setUnused:", self.setUnused, " VirtualBoxID:",
              self.virtualBoxId, " afi: ", afi, " tag: ", tag, " address: ", address, " subnetMask")

    def pack(self):
        return struct.pack("iii11sh11s13s", self.command, self.version, self.setUnused, self.virtualBoxId, self.tag,
                           self.address, self.subnetMask)
    def isValid(self):
        if (self.command not in [1, 2]):
            print("Invalid command in header")
            return False


# clasa entry reprezinta adaugarile care se fac tabelei de rutare pentru a pastra destinatia si metrica
class entry:
    def __init__(self, nextHop, metric):
        self.nextHop = nextHop
        self.metric = metric

    def returnareEntry(self):
        return struct.pack('ii', self.nextHop, self.metric)

    def isValidEntry(self):
        if (self.metric > 15):
            print("Metrica nu trebuie sa fie mai mare decat 16!")
            return False
        else:
            return True

    def setMetric(self, x):
        self.metric = x


# tabelaRutare este clasa care combina header-ul cu entry-urile pentru a compune tabela de rutare finala a masinii virtuale folosite
class tabelaRutare:
    entries = []

    def __init__(self, header):
        self.header = header.pack()
        self.entries = []

    def adaugareEntry(self, entry):
        self.entries.append(entry.returnareEntry())

    def clear(self):
        self.entries = []

    def deleteEntry(self, entry):
        self.entries.remove(entry.returnareEntry())

    def unpack(self):
        data = []
        string = ""
        k = 1
        header = struct.unpack('iii11sh11s13s', self.header)
        print("HEADERUL!")
        print(header)
        data.append(header)
        line = "+-----------+----------+-----------+---------------+----------+-------------+"
        # string = string + line
        print(line)
        # string = string + line
        print(
            "|                              Routing Table                                |")
        print(line)
        # string = string + line
        print("Command: " + str(header[0]) + "\nVERSION: " + str(header[1]) + "\nsetUnused: " + str(
            header[2]) + "VirtualBoxID:" + str(
            header[3]) + "tag:" + str(header[4]) + "address:" + str(header[5]) + "subnetMask:" + str(header[6]))
        string = string + "Command: " + str(header[0]) + "\nVERSION: " + str(header[1]) + "\nSetUnused: " + str(
            header[2])  + "\nTag: " + str(header[4]) + "\nAddress: " + (str(header[5])).replace('b\'','').replace('\'','') + "\nSubnetMask: " + (str(header[6])).replace('b\'','').replace('\'','')
        print(line)
        # string = string + line
        for x in range(len(self.entries)):
            w = struct.unpack('ii', self.entries[x])
            print("NextHop:", str(w[0]), "Metric:", w[1])
            string = string + "\nNextHop: "  + str(w[0]) + " Metric: " + str(w[1])
            print(line)
            # string = string + line
            # k=k+1
        return string

    def set_nexthop(self, nextHop):
        self.nextHop = nextHop

    def updateTable(self, entry, flag):
        if (flag == 1):
            self.adaugareEntry(entry)
        if (flag == 0):
            self.deleteEntry(entry)

    # cand adaugam noi entry-uri in tabela de rutare, trebuie sa le stergem pe cele vechi pentru a nu ne afisa de mai multe ori aceeasi destinatie-metrica
    def stergereEntries(self):
        # for entry in self.entries:
        self.entries[:] = []


class Connection:
    def __init__(self, port, sockt):
        self.port = port
        self.sockt = sockt

    def __repr__(self):
        return "Conexiune".format(self.port)


def show_packet(packet):
    data = packet.unpack()


# aceasta clasa este folosita pentru a forma graful folosit la calculul BellmanFord

class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = []

    def addEdge(self, u, v, w):
        self.graph.append([u, v, w])

    def delEdge(self, u, v, w):
        if [u, v, w] in self.graph:
            self.graph.remove([u, v, w])

    def printare(self):
        print("PRINTARE:")
        for x in self.graph:
            print(x)

    def printArr(self, dist):
        print("Distanta de la sursa")
        for i in range(self.V):
            print("{0}\t\t{1}".format(i, dist[i]))

    def BellmanFord(self, src):
        dist = [float("Inf")] * self.V
        dist[src] = 0
        for _ in range(self.V - 1):
            for u, v, w in self.graph:
                if dist[u] != float("Inf") and dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
        for u, v, w in self.graph:
            if dist[u] != float("Inf") and dist[u] + w < dist[v]:
                print("Graful contine cicluri negative")
                return
        print(dist)

        self.printArr(dist)
        return dist


# Creaza un socket UDP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# adresa multicast
p = '224.0.0.251'

# reuseaddr permite refolosirea adreselor locale
# am folosit SOL_SOCKET deoarece este folosit pentru optiuni care sunt independente de protocolul folosit
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# am folosit IP_MULTICAST_LOOP pentru a putea avea o aplicatie cu mai mult receptori si emitatori
s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
IS_ALL_GROUPS = True

s.bind((p, 5000))

# mreq=struct.pack("4sl", socket.inet_aton('224.0.0.9'), socket.INADDR_ANY)
host = socket.gethostbyname(socket.gethostname())
s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
s.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP,
             socket.inet_aton(p) + socket.inet_aton(host))
tabelaR = ""
users = {'Elena': 'abcd', 'Beti': 'cdef'}
nghbs = {}
addrs = []
dict = {}
print('Asteapta conexiuni (oprire server cu Ctrl-C)')
header1 = header(1, '192.168.0.107'.encode(), 2,
                 '192.168.0.107'.encode(), '255.255.255.0'.encode())
neighbours = {2: 1, 5: 1}
s.sendto(str(neighbours).encode(), (p, 5000))
acestRuter = 1
g = Graph(6)
for key in neighbours:
    g.addEdge(acestRuter, key, neighbours[key])
# calculam entry-urile din tabela de rutare initiala a acestei masini virtuale
print(g.BellmanFord(acestRuter))
a = g.BellmanFord(acestRuter)
print("ssssssssssssssssssssssssss")
print(a[1], a[2], a[3], a[4], a[5])
# intrucat RIPv2 nu poate avea o topologie de maxim 15, vom pune 16 care reprezinta infinitul
if a[1] == float("Inf"):
    a[1] = 16
if a[2] == float("Inf"):
    a[2] = 16
if a[3] == float("Inf"):
    a[3] = 16
if a[4] == float("Inf"):
    a[4] = 16
if a[5] == float("Inf"):
    a[5] = 16
entry1 = entry(1, a[1])
entry2 = entry(2, a[2])
entry3 = entry(3, a[3])
entry4 = entry(4, a[4])
entry5 = entry(5, a[5])
pack = tabelaRutare(header1)
pack.adaugareEntry(entry1)
pack.adaugareEntry(entry2)
pack.adaugareEntry(entry3)
pack.adaugareEntry(entry4)
pack.adaugareEntry(entry5)
m = 1
v = 0
flag = 0
update = 0
old_m = 0
timerr = 30
threadRunning = 1


# acesta este thread-ul care va apasa butonul de update de cate ori este specificat in timerr
def comm_thread(button1, button2, button3):
    print("s-a pornit")
    global threadRunning
    while threadRunning:
        global timerr
        print("s-a apasat")
        button1.invoke()
        button2.invoke()
        button3.invoke()
        time.sleep(int(timerr))


class GUI:
    def __init__(self):
        self.Window = Tk()
        self.Window.withdraw()
        self.login = Toplevel()
        self.login.title("Login")
        self.login.resizable(width=False, height=False)
        self.login.configure(width=400, height=300)
        self.pls = Label(self.login, text="Please login to continue", justify=CENTER, font="Helvetica 14 bold")
        self.pls.place(relheight=0.15, relx=0.2, rely=0.07)
        self.labelName1 = Label(self.login, text="Username: ", font="Helvetica 12")
        self.labelName1.place(relheight=0.2, relx=0.1, rely=0.2)
        self.labelName2 = Label(self.login, text="Password: ", font="Helvetica 12")
        self.labelName2.place(relheight=0.2, relx=0.1, rely=0.4)
        password=tk.StringVar()
        username=tk.StringVar()
        self.entryName1 = Entry(self.login, textvariable=password, show='*')

        self.entryName1.place(relwidth=0.4,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.4)
        self.entryName = Entry(self.login,
                               
                               textvariable=username)

        self.entryName.place(relwidth=0.4,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.2)
        self.entryName.focus()
       
        self.go = Button(self.login, text="CONTINUE", font="Helvetica 14 bold",
                         command=lambda: self.goAhead(username.get(), password.get()))
        self.go.place(relx=0.4, rely=0.55)
        self.Window.mainloop()
    def goAhead(self, username, password):
        if(username=='beti' and password=='beti' or username=='elena' and password=='elena'):
            self.login.destroy()
            self.layout(username)
            rcv = threading.Thread(target=self.receive)
            rcv.start()
        else:
            showinfo(title="Eroare", message="Username sau parola gresita ")
           
    def setM(self, me):
        global m
        if (me != "" and me.isnumeric()):
            m = int(me, 10)
            if (m > 15):
                print("metrica nu poate fi mai mare decat 15!")
                m = 1
        else:
            m = 1

        print(m)

    def setV(self, ve):
        global v
        if (ve != "" and ve.isnumeric()):
            v = int(ve, 10)
            if (v > 5):
                print("ati introdus gresit vecinul")
                v = 0
        else:
            v = 0

        print(v)

    def setTimer(self, tm, button1, button2, button3):
        global timerr
        global threadRunning
        if (tm.isnumeric()):
            # proc.terminate()
            timerr = tm
            # proc=multiprocessing.Process(target=comm_thread, args=(button1,button2, button3))
            # proc.start()
            threadRunning = 0
            # t=threading.Thread(target=comm_thread, args=(button1,button2, button3)).start()
            threadRunning = 1
            t = threading.Thread(target=comm_thread, args=(self.getM, self.getV, self.get)).start()

    def update(self):
        global neighbours
        global v
        global m
        global old_m
        global g
        if v in neighbours:
            if (neighbours[v] != m):
                old_m = neighbours[v]
                neighbours[v] = m
                flag = 1
                if (True):
                    print(neighbours)
                    pack.stergereEntries()
                    g = Graph(6)

                    for key in neighbours:
                        print(v)
                        print(m)
                        g.addEdge(acestRuter, key, neighbours[key])

                    g.printare()
                    g.delEdge(acestRuter, v, old_m)
                    print(g.BellmanFord(acestRuter))
                    a = g.BellmanFord(acestRuter)
                    print("ssssssssssssssssssssssssss")
                    print(a[1], a[2], a[3], a[4], a[5])
                    if a[1] == float("Inf"):
                        a[1] = 16
                    if a[2] == float("Inf"):
                        a[2] = 16
                    if a[3] == float("Inf"):
                        a[3] = 16
                    if a[4] == float("Inf"):
                        a[4] = 16
                    if a[5] == float("Inf"):
                        a[5] = 16
                    entry1 = entry(1, a[1])
                    entry2 = entry(2, a[2])
                    entry3 = entry(3, a[3])
                    entry4 = entry(4, a[4])
                    entry5 = entry(5, a[5])
                    pack.stergereEntries()
                    pack.adaugareEntry(entry1)
                    pack.adaugareEntry(entry2)
                    pack.adaugareEntry(entry3)
                    pack.adaugareEntry(entry4)
                    pack.adaugareEntry(entry5)
                    pack.unpack()
                    s.sendto(("1:" + str(neighbours)).encode(), (p, 5000))
                    flag = 0
        else:
            s.sendto(("1:" + str(neighbours)).encode(), (p, 5000))

    def layout(self, name):

        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("Afisare tabela rutare")
        self.Window.resizable(width=True,
                              height=True)
        self.Window.configure(width=800,
                              height=800,
                              bg="#17202A")
        self.labelHead = Label(self.Window,
                               bg="#17202A",
                               fg="#EAECEE",
                               text=self.name,
                               font="Helvetica 13 bold",
                               pady=5)

        self.labelHead.place(relwidth=1)
        self.line = Label(self.Window,
                          width=450,
                          bg="#ABB2B9")

        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=0.012)

        self.textCons = Text(self.Window,
                             width=20,
                             height=2,
                             bg="#17202A",
                             fg="#EAECEE",
                             font="Helvetica 14",
                             padx=5,
                             pady=5)

        self.textCons.place(relheight=0.500,
                            relwidth=1,
                            rely=0.08)

        self.labelBottom = Label(self.Window,
                                 bg="#ABB2B9",
                                 height=80)

        self.labelBottom.place(relwidth=1,
                               rely=0.825)
        self.labelM = Label(self.Window, text="Costul: ", font="Helvetica 12")
        self.labelM.place(relwidth=0.1, relheight=0.04, relx=0., rely=0.9)
        self.entryM = Entry(self.Window,
                            font="Helvetica 14")

        self.entryM.place(relwidth=0.1, relheight=0.04,
                          relx=0.13, rely=0.9)

        self.labelV = Label(self.Window, text="Vecin: ", font="Helvetica 12")
        self.labelV.place(relwidth=0.1, relheight=0.04, relx=0, rely=0.7)
        self.entryV = Entry(self.Window,
                            font="Helvetica 14")

        self.entryV.place(relwidth=0.1, relheight=0.04,
                          relx=0.13,
                          rely=0.7)
        self.getM = Button(self.Window, text="Adauga Metrica", font="Helvetica 14 bold",
                           command=lambda: self.setM(self.entryM.get()))
        self.getM.place(relwidth=0.3, relheight=0.04, relx=0.25, rely=0.9)
        self.getV = Button(self.Window, text="Adauga Vecin", font="Helvetica 14 bold",
                           command=lambda: self.setV(self.entryV.get()))
        self.getV.place(relwidth=0.3, relheight=0.04,relx=0.25, rely=0.7)
        # tk.Label(self.Window, text="Metrica").grid(row=20)
        # e1=tk.Entry(self.Window)
        # e1.grid(row=20, column=30)
        self.get = Button(self.Window, text="update", font="Helvetica 14 bold", command=lambda: self.update())
        self.get.place(relx=0.75, rely=0.9)

        self.labelTimer = Label(self.Window, text="Timer: ", font="Helvetica 12")
        self.labelTimer.place(relwidth=0.1, relheight=0.04, relx=0, rely=0.8)
        self.entryTimer = Entry(self.Window,
                                font="Helvetica 14")

        self.entryTimer.place(relwidth=0.1,
                              relheight=0.04,
                              relx=0.13, rely=0.8)

        t = threading.Thread(target=comm_thread, args=(self.getM, self.getV, self.get)).start()
        # proc=multiprocessing.Process(target=comm_thread, args=(self.getM,self.getV, self.get))
        # proc.start()

        self.getT = Button(self.Window, text="Adauga Timer", font="Helvetica 14 bold",
                           command=lambda: self.setTimer(self.entryTimer.get(), self.getM, self.getV, self.get))
        self.getT.place(relwidth=0.3, relheight=0.04, relx=0.25, rely=0.8)

    def receive(self):
        deTrimis = []
        global g
        global v
        global m
        global old_m
        while 1:
            dat, addr = s.recvfrom(1024)
            data = dat.decode()
            print('adresa este: ', str(addr)[2:11])
            print(str(addr)[2:11])
            print(str('127.0.1.1'))

            if (str(addr)[2:11] == str('127.0.1.1')):

                pack.stergereEntries()
                g.delEdge(acestRuter, v, old_m)
                for key in neighbours:
                    print(key)
                    print(neighbours[key])
                    g.addEdge(acestRuter, key, neighbours[key])
                g.printare()
                print(g.BellmanFord(acestRuter))
                a = g.BellmanFord(acestRuter)
                print("ssssssssssssssssssssssssss")
                print(a[1], a[2], a[3], a[4], a[5])
                if a[1] == float("Inf"):
                    a[1] = 16
                if a[2] == float("Inf"):
                    a[2] = 16
                if a[3] == float("Inf"):
                    a[3] = 16
                if a[4] == float("Inf"):
                    a[4] = 16
                if a[5] == float("Inf"):
                    a[5] = 16
                entry1 = entry(1, a[1])
                entry2 = entry(2, a[2])
                entry3 = entry(3, a[3])
                entry4 = entry(4, a[4])
                entry5 = entry(5, a[5])
                pack.stergereEntries()
                pack.adaugareEntry(entry1)
                pack.adaugareEntry(entry2)
                pack.adaugareEntry(entry3)
                pack.adaugareEntry(entry4)
                pack.adaugareEntry(entry5)

                for add in addrs:
                    s.sendto(("1:" + ":" + str(data)).encode(), add)
                    print(("1:" + ":" + str(data)).encode())

                deTrimis.append("1" + ":" + str(data))
                print("1" + ":" + str(data))
                message = pack.unpack()
                self.textCons.config(state=NORMAL)
                self.textCons.insert(END, message + "\n\n")

                self.textCons.config(state=DISABLED)
                self.textCons.see(END)





            else:

                print("s-a receptionat" + str(data))
                s.sendto(str(neighbours).encode(), (p, 5000))
                print("Dictionarul este: ")
                start = (str(data)).find("{") + len("{")
                end = (str(data)).find("}")
                substring = (str(data))[start:end]
                res = ast.literal_eval("{" + substring + "}")
                print(res)

                if str(addr)[1:16] == "'192.168.0.104'":
                    addrsa = 2
                elif str(addr)[1:16] == "'192.168.0.107'":
                    addrsa = 1
                elif str(addr)[1:16] == "'192.168.0.111'":
                    addrsa = 5
                elif str(addr)[1:16] == "'192.168.0.109'":
                    addrsa = 4
                elif str(addr)[1:16] == "'192.168.0.108'":
                    addrsa = 3
                else:
                    addrsa = 0

                for add in addrs:
                    s.sendto(((str(addrsa)) + ":" + str(data)).encode(), add)

                for x in deTrimis:
                    s.sendto(x.encode(), addr)
                deTrimis.append(str(addrsa) + ":" + str(data))

                print(str(data)[0:1])
                for key in res:
                    if addrsa == 1:
                        g.addEdge(1, key, res[key])
                    if addrsa == 2:
                        g.addEdge(2, key, res[key])
                    if addrsa == 3:
                        g.addEdge(3, key, res[key])
                    if addrsa == 4:
                        g.addEdge(4, key, res[key])
                    if addrsa == 5:
                        g.addEdge(5, key, res[key])

                addrs.append(addr)
                print(g.BellmanFord(acestRuter))
                a = g.BellmanFord(acestRuter)
                if a[1] == float("Inf"):
                    a[1] = 16
                if a[2] == float("Inf"):
                    a[2] = 16
                if a[3] == float("Inf"):
                    a[3] = 16
                if a[4] == float("Inf"):
                    a[4] = 16
                if a[5] == float("Inf"):
                    a[5] = 16
                entry1 = entry(1, a[1])
                entry2 = entry(2, a[2])
                entry3 = entry(3, a[3])
                entry4 = entry(4, a[4])
                entry5 = entry(5, a[5])
                pack.stergereEntries()
                pack.adaugareEntry(entry1)
                pack.adaugareEntry(entry2)
                pack.adaugareEntry(entry3)
                pack.adaugareEntry(entry4)
                pack.adaugareEntry(entry5)

                message = pack.unpack()
                self.textCons.config(state=NORMAL)
                self.textCons.insert(END, message + "\n\n")

                self.textCons.config(state=DISABLED)
                self.textCons.see(END)


q = GUI()
