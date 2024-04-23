# SimPy model for the Reliable Data Transport (rdt) Protocol 1.0.
#
# Sender-side (rdt_Sender)
#	- receives messages to be delivered from the upper layer 
#	  (SendingApplication) 
#	- Implements the protocol for reliable transport
#	 using the udt_send() function provided by an unreliable channel.
#
# Receiver-side (rdt_Receiver)
#	- receives packets from the unrealible channel via calls to its
#	rdt_rcv() function.
#	- implements the receiver-side protocol and delivers the collected
#	data to the receiving application.

# Author: Neha Karanjkar


import simpy
import random
from Packet import Packet

class rdt_Sender(object):

	def __init__(self,env):
		# Initialize variables
		self.env=env 
		self.channel=None
		self.seq_num=0
	
	def rdt_send(self,msg):
		# This function is called by the 
		# sending application.
		#
		# create a packet
		packt= Packet(seq_num=self.seq_num, payload=msg)
		self.seq_num+=1
		# send it over the channel
		self.channel.udt_send(packt)
		return True
	
	def rdt_rcv(self,packt):
		# This function is called by the lower-layer when an ACK/NAK packet arrives
		# It is not used in Protocol 1. Just ignore this for now..
		pass	

class rdt_Receiver(object):
	def __init__(self,env):
		# Initialize variables
		self.env=env 
		self.receiving_app=None
		self.channel=None

	def rdt_rcv(self,packt):
		# This function is called by the lower-layer when a packet arrives
		# at the receiver
		
		# deliver the packet to the layer above.
		if not (packt.corrupted):
			self.receiving_app.deliver_data(packt.payload)

