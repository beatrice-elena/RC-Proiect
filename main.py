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