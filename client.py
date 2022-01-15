import socket
import struct
import time


def unpack(header):
    return struct.unpack('iii',header.encode());

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect(('10.0.2.15',5000))
#s.connect(('192.168.0.107',5000))
s.connect(('127.0.0.1',5000))
for i in range(3,4):
    s.sendall(bytes('S-a conectatat',encoding="ascii"))
data=s.recv(2048)
print('Am receptionat:', data)
time.sleep(1)
s.close()