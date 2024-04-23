# This is a Python class for a Packet.
#
# A packet has three fields:
#	payload: the data contained in the packet,
#	seq_num: the packet sequence number,
#	corrupted: a flag, which can be True or False
#
# Author: Neha Karanjkar


class Packet(object):
	
	def __init__(self,payload, seq_num):
		self.payload=payload
		self.seq_num = seq_num
		self.corrupted=False
	
	# this function can be called
	# to mark a packet as "corrupted".
	def corrupt(self):
		self.corrupted=True
		self.payload="$H!T"

	# this function can be used to print a packet
	def __str__(self):
		return "Packet(seq_num=%d, payload=%s, corrupted=%s)"% (self.seq_num, self.payload, self.corrupted)

