import socket
import time
import struct
import socket
import threading
import socket
import struct
import time
import json

import ast


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
              self.virtualBoxId, " afi: ", self.afi, " tag: ", self.tag, " address: ", self.address, " subnetMask")

    def pack(self):
        return struct.pack('iii20sh20s13s', self.command, self.version, self.setUnused, self.virtualBoxId, self.tag,
                           self.address, self.subnetMask)

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
        header = struct.unpack('iii20sh20s13s', self.header)
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
        print("Command:" + str(header[0]) + "VERSION:" + str(header[1]) + "setUnused:" + str(
            header[2]) + "VirtualBoxID:" + str(
            header[3].decode()) + "tag:" + str(header[4]) + "address:" + str(header[5].decode()) + "subnetMask:" + str(
            header[6].decode()))
        string = string + "Command:" + str(header[0]) + "VERSION:" + str(header[1]) + "setUnused:" + str(
            header[2]) + "VirtualBoxID:" + str(header[3]) + "tag:" + str(header[4]) + "address:" + str(
            header[5]) + "subnetMask:" + str(header[6])
        print(line)
        # string = string + line
        for x in range(len(self.entries)):
            w = struct.unpack('ii', self.entries[x])
            print("NextHop:", str(w[0]), "Metric:", w[1])
            string = string + "NextHop:" + str(w[0]) + "Metric:" + str(w[1])
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

    def stergereEntries(self):
        # for entry in self.entries:
        self.entries[:] = []


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


def show_packet(packet):
    data = packet.unpack()


# Bellman-Ford de pe geeksforgeeks
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
        self.printArr(dist)
        return dist


adresa = '192.168.0.101'
neighbours2 = {"192.168.0.107": 1, "192.168.0.111": 1, "192.168.0.108": 1}
neighbours = {1: 1, 5: 1, 3: 1}
rute = []
acestRuter = 2
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
p2 = '192.168.0.107'
p = '224.0.0.251'
# s.connect(("192.168.0.107",5000))
# s.connect(("224.0.0.9",5000))
# s.sendall(str(neighbours) )
s.sendto(("2:" + str(neighbours)).encode(), (p, 5000))
print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
print(("2:" + str(neighbours)).encode())
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
header1 = header(1, '192.168.0.104'.encode(), 2, '192.168.0.104'.encode(), '255.255.255.0'.encode())
pack = tabelaRutare(header1)
pack.stergereEntries()
pack.adaugareEntry(entry1)
pack.adaugareEntry(entry2)
pack.adaugareEntry(entry3)
pack.adaugareEntry(entry4)
pack.adaugareEntry(entry5)
pack.unpack()

while True:
    data = s.recvfrom(2048)
    # data = dat.decode();
    print('Am receptionat:', data)
    rute.append(str(data))
    print('adresa ar trebuie sa fie: ', str(data)[2:3])
    start = (str(data)).find("{") + len("{")
    end = (str(data)).find("}")
    substring = (str(data))[start:end]
    print('si dictionarul: ', "{" + substring + "}")
    dictt = ast.literal_eval("{" + substring + "}")
    print("speram sa iasa")
    print(dictt)
    for key in dictt:
        if str(data)[2:3] == '1':
            g.addEdge(1, key, dictt[key])
        if str(data)[2:3] == '2':
            g.addEdge(2, key, dictt[key])
        if str(data)[2:3] == '3':
            g.addEdge(3, key, dictt[key])
        if str(data)[2:3] == '4':
            g.addEdge(4, key, dictt[key])
        if str(data)[2:3] == '5':
            g.addEdge(5, key, dictt[key])
    print("Incercare Bellman-Ford")
    a = g.BellmanFord(acestRuter)
    print(g.BellmanFord(acestRuter))
    if a[5] == float("Inf"):
        a[5] = 1000
    if a[4] == float("Inf"):
        a[4] = 1000
    if a[3] == float("Inf"):
        a[3] = 1000
    if a[2] == float("Inf"):
        a[2] = 1000
    if a[1] == float("Inf"):
        a[1] = 10000
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















