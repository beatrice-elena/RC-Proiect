import socket
import threading
import socket
import struct
import time
from turtle import update


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
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Asociere la adresa locala, portul 5000
s.bind(('0.0.0.0', 5000))

print('Asteapta conexiuni (oprire server cu Ctrl-C)')
while 1:
    data,addr=s.recvfrom(1024)
    s.sendto("Transmitere mesaj",addr)