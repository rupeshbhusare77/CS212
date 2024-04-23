# A simple program to test the Packet class

from Packet import Packet


p1 = Packet(seq_num=3, payload="A")
print (p1)

p2 = Packet(seq_num=4, payload="B")
print (p2)
p2.corrupt()

print (p2)

