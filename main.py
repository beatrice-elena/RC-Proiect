import interfata
import socket
import struct
import time
INPUT_PORTS = []
OUTPUT_PORTS = {}
update=30
IP_ADDR="170.0.0.1"

class header:

    def __init__(self, command, virtualBoxId):
        self.command = command
        self.version = 2
        self.setUnused = 0
        self.virtualBoxId = virtualBoxId

    def showH(self):
        print("Command:", self.command, " Version:", self.version, " setUnused:", self.setUnused, " VirtualBoxID:",
              self.virtualBoxId)

    def pack(self):
        return struct.pack('iiii', self.command, self.version, self.setUnused, self.virtualBoxId)
    def isValid(self):
        if(self.command not in [1,2]):
            print("Invalid command in header")
            return False
class entry:
    def __init__(self, tag, address, subnetMask, nextHop, metric):
        self.afi = 2
        self.tag = tag
        self.address = address
        self.subnetMask = subnetMask
        self.nextHop = nextHop
        self.metric = metric


    def returnareEntry(self):
        return struct.pack('hiiii', self.tag, self.address, self.subnetMask, self.nextHop, self.metric)
    def isValidEntry(self):
        if(self.metric>15):
            print("Metrica nu trebuie sa fie mai mare decat 16!")
            return False
        else:
            return True
    def setMetric(self, x):
        self.metric=x
class tabelaRutare:
    entries =[]
    def __init__(self, header):
        self.header = header.pack()
        self.entries = []
        self.periodic=update
 
 
    def adaugareEntry(self, entry):
        self.entries.append(entry.returnareEntry())
 
    def clear(self):
        self.entries = []
 
    def deleteEntry(self, entry):
        self.entries.remove(entry.returnareEntry())
 
    def unpack(self):
        data = []
        string=""
        k = 1
        header = struct.unpack('iiii', self.header)
        data.append(header)
        line = "+-----------+----------+-----------+---------------+----------+-------------+"
        string=string+line
        print(line)
        string=string+line
        print("|                              Routing Table                                |")
        print(line)
        string=string+line
        print("Command:", data[0][0], "VERSION:", data[0][1], "setUnused:", data[0][2], "VirtualBoxID:", data[0][3])
        print(line)
        string=string+line
        for x in range(len(self.entries)):
            data.append(struct.unpack('hiiii', self.entries[x]))
            print("AFI:", 2, "Tag:", data[x + k][0], "Address:", data[x + k][1], "SubnetMask:", data[x + k][2],
                  "NextHop:", data[x + k][3], "Metric:", data[x + k][4])
            string=string+("AFI: 2 Tag:"+ str(data[x + k][0])+"Address:"+str(data[x + k][1])+ "SubnetMask:"+str(data[x + k][2])+ "NextHop:"+ str(data[x + k][3])+ "Metric:"+ str(data[x + k][4]))
            print(line)
            string=string+line
            # k=k+1
        return string
 
    def set_nexthop(self, nextHop):
        self.nextHop = nextHop
    def updateTable(self,entry,flag):
        if(flag==1):
            self.adaugareEntry(entry)
        if(flag==0):
            self.deleteEntry(entry)
class ruter:
    def __init__(self, inputPorts, outputPorts, tabelaRutare):
        self.inputPorts=[]
        self.inputPorts.append(inputPorts)
        self.outputPorts=[]
        self.outputPorts.append(outputPorts)
        self.index = 0
        self.neighbours=[]

        self.create_sockets()

        self.conexiuni = {}
        self.lista_conexiuni = []
        self.conexiuni_output=[]
        self.tabelaRutare=tabelaRutare


    def add_neighbours(self):
        self.index = self.index + 1
        for x in range(len(self.outputPorts)):
            self.neighbours.append(self.outputPorts[x])

    def show_neighbours(self):
        for x in range(len(self.neighbours)):
            print(self.neighbours[x])

    def create_sockets(self):
        for port in self.inputPorts:
            peer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            peer.bind((IP_ADDR, port))
            self.conexiuni[port]=Connection(port,peer)
            self.lista_conexiuni.append(peer)
        self.conexiuni_output=self.conexiuni[self.inputPorts[0]]

    def periodic_updates(self):
        global running
        while running:
            for x in range(len(tabelaRutare.entries)):
                self.send(tabelaRutare.entries[x])
            time.sleep(30)
    def send(self,x):
        pass
    def populate_table(self,data,entry):
        port=data[1][1]
        if port not in self.tabelaRutare.get_addresses():
            print(port,self.outputPorts)
            for metric, id in self.outputPorts:
                cost=metric
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



if __name__ == '__main__':
    header1 = header(1, 3)
    packet1 = tabelaRutare(header1)
    entry1 = entry(2, 4, 5, 6, 7)
    entry2 = entry(2, 4, 6, 3, 4)
    packet1.adaugareEntry(entry1)
    packet1.adaugareEntry(entry2)
    show_packet(packet1)
    interfata.MainWindow().creareFereastra(packet1.unpack())
 
