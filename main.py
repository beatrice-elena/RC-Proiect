import socket
import threading
import socket
import struct
import time
from turtle import update
import ast


class header:
    def __init__(self, command, virtualBoxId,tag,address,subnetMask):
        self.command = command
        self.version = 2
        self.setUnused = 0
        self.virtualBoxId = virtualBoxId
        self.afi = 2
        self.tag = tag
        self.address = address
        self.subnetMask = subnetMask

    def pack(self):
        return struct.pack('iii20sh20s13s13', self.command, self.version, self.setUnused, self.virtualBoxId, self.tag, self.address, self.subnetMask)

    def isValid(self):
        if (self.command not in [1, 2]):
            print("Invalid command in header")
            return False


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


class tabelaRutare:
    entries = []

    def __init__(self, header):
        self.header = header.pack()
        self.entries = []
        self.periodic = update

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
        header = struct.unpack('iii20sh20s13s13', self.header)
        print("HEADERUL!")
        print(header)
        data.append(header)
        line = "+-----------+----------+-----------+---------------+----------+-------------+"
        #string = string + line
        print(line)
        #string = string + line
        print("|                              Routing Table                                |")
        print(line)
        #string = string + line
        print("Command:"+str(header[0])+ "VERSION:"+ str(header[1])+ "setUnused:"+ str(header[2])+"VirtualBoxID:"+ str(header[3])+"tag:"+str(header[4])+"address:"+str(header[5])+"subnetMask:"+str(header[6]))
        string=string+"Command:"+str(header[0])+ "VERSION:"+ str(header[1])+ "setUnused:"+ str(header[2])+"VirtualBoxID:"+ str(header[3])+"tag:"+str(header[4])+"address:"+str(header[5])+"subnetMask:"+str(header[6])
        print(line)
        #string = string + line
        for x in range(len(self.entries)):
            w=struct.unpack('ii', self.entries[x])
            print("NextHop:", str(w[0]), "Metric:", w[1])
            string = string +"NextHop:"+ str(w[0])+ "Metric:"+ str(w[1])
            print(line)
            #string = string + line
            # k=k+1
        return string

    def set_nexthop(self, nextHop):
        self.nextHop = nextHop

    def updateTable(self, entry, flag):
        if (flag == 1):
            self.adaugareEntry(entry)
        if (flag == 0):
            self.deleteEntry(entry)
    def stergereEntries(self):
    	#for entry in self.entries:
    	self.entries[:]=[]




class ruter:
    def __init__(self, inputPorts, outputPorts, tabelaRutare):
        self.inputPorts = []
        self.inputPorts.append(inputPorts)
        self.outputPorts = []
        self.outputPorts.append(outputPorts)
        self.index = 0
        self.neighbours = []

        self.create_sockets()

        self.conexiuni = {}
        self.lista_conexiuni = []
        self.conexiuni_output = []
        self.tabelaRutare = tabelaRutare

    def add_neighbours(self):
        self.index = self.index + 1
        for x in range(len(self.outputPorts)):
            self.neighbours.append(self.outputPorts[x])

    def show_neighbours(self):
        for x in range(len(self.neighbours)):
            print(self.neighbours[x])

    def periodic_updates(self):
        global running
        while running:
            for x in range(len(tabelaRutare.entries)):
                self.send(tabelaRutare.entries[x])
            time.sleep(30)

    def send(self, x):
        pass

    def populate_table(self, data, entry):
        port = data[1][1]
        if port not in self.tabelaRutare.get_addresses():
            print(port, self.outputPorts)
            for metric, id in self.outputPorts:
                cost = metric
            entry.setMetric(cost)
            self.tabelaRutare.adaugareEntry(entry)


class Connection:
    def __init__(self, port, sockt):
        self.port = port
        self.sockt = sockt

    def __repr__(self):
        return "Conexiune".format(self.port)


class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = []

    def addEdge(self, u, v, w):
        self.graph.append([u, v, w])

    def printArr(self, dist):
        print("Vertex distance from source")
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
                print("Graph contains negative weight cycle")
                return
        print("aici")
        print(dist)

        self.printArr(dist)
        return dist


# Creaza un socket IPv4, TCP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# Asociere la adresa locala, portul 5000

# Coada de asteptare pentru conexiuni de lungime 1
# s.listen(5)
# Asteapta conexiuni
p = '224.0.0.251'
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
IS_ALL_GROUPS = True

s.bind((p, 5000))

# mreq=struct.pack("4sl", socket.inet_aton('224.0.0.9'), socket.INADDR_ANY)
host = socket.gethostbyname(socket.gethostname())
s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
s.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(p) + socket.inet_aton(host))
nghbs = {}
addrs = []
dict = {}
print('Asteapta conexiuni (oprire server cu Ctrl-C)')
header1 = header(1, '192.168.0.107', 2, '192.168.0.107', '255.255.255.0')
neighbours = {2: 1, 5: 1}
s.sendto(str(neighbours), (p, 5000))
acestRuter = 1
g = Graph(6)
for key in neighbours:
    g.addEdge(acestRuter, key, neighbours[key])
print(g.BellmanFord(acestRuter))
a = g.BellmanFord(acestRuter)
print("ssssssssssssssssssssssssss")
print(a[1], a[2], a[3], a[4], a[5])
if a[1] == float("Inf"):
    a[1] = 1000
if a[2] == float("Inf"):
    a[2] = 1000
if a[3] == float("Inf"):
    a[3] = 1000
if a[4] == float("Inf"):
    a[4] = 1000
if a[5] == float("Inf"):
    a[5] = 1000
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
while 1:
    data, addr = s.recvfrom(1024)
    print('adresa este: ', str(addr)[1:16])
    print("s-a receptionat" + str(data))

    print("Dictionarul este: ")
    start = (str(data)).find("{") + len("{")
    end = (str(data)).find("}")
    substring = (str(data))[start:end]
    res = ast.literal_eval("{" + substring + "}")
    print(res)
    if str(addr)[1:16] == "'192.168.0.101'":
        addrsa = 2
    elif str(addr)[1:16] == "'192.168.0.107'":
        addrsa = 1
    elif str(addr)[1:16] == "'192.168.0.111'":
        addrsa = 5
    elif str(addr)[1:16] == "'192.168.0.109'":
        addrsa = 4
    elif str(addr)[1:16] == "'192.168.0.108'":
        addrsa = 3

    for add in addrs:
        s.sendto(str(addrsa) + ":" + str(data), add)
    print("fsssssssssssssssssssssssss")
    print(str(data)[0:1])
    for key in res:
        if str(data)[0:1] == '1':
            g.addEdge(1, key, res[key])
        if str(data)[0:1] == '2':
            g.addEdge(2, key, res[key])
        if str(data)[0:1] == '3':
            g.addEdge(3, key, res[key])
        if str(data)[0:1] == '4':
            g.addEdge(4, key, res[key])
        if str(data)[0:1] == '5':
            g.addEdge(5, key, res[key])
    addrs.append(addr)
    print(g.BellmanFord(acestRuter))
    a = g.BellmanFord(acestRuter)
    if a[1] == float("Inf"):
        a[1] = 1000
    if a[2] == float("Inf"):
        a[2] = 1000
    if a[3] == float("Inf"):
        a[3] = 1000
    if a[4] == float("Inf"):
        a[4] = 1000
    if a[5] == float("Inf"):
        a[5] = 1000
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