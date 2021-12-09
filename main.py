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
 
