# SimPy model for the Reliable Data Transport (rdt) Protocol 2.0 (Using ACK and NAK)

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
import sys

# the sender can be in one of these two states:
WAITING_FOR_CALL_FROM_ABOVE =0
WAIT_FOR_ACK_OR_NAK=1



class rdt_Sender(object):

	def __init__(self,env):
		# Initialize variables
		self.env=env 
		self.channel=None
		
		# some state variables
		self.state = WAITING_FOR_CALL_FROM_ABOVE
		self.seq_num=0
		self.packet_to_be_sent=None

	
	def rdt_send(self,msg):

		if self.state==WAITING_FOR_CALL_FROM_ABOVE:
			# This function is called by the 
			# sending application.
			
			# create a packet, and save a copy of this packet
			# for retransmission, if needed
			self.packet_to_be_sent = Packet(seq_num=self.seq_num, payload=msg)
			self.seq_num+=1
			# send it over the channel
			self.channel.udt_send(self.packet_to_be_sent)
			# wait for an ACK or NAK
			self.state=WAIT_FOR_ACK_OR_NAK
			return True
		else:
			return False
	
	def rdt_rcv(self,packt):
		# This function is called by the lower-layer 
		# when an ACK/NAK packet arrives
		assert(self.state==WAIT_FOR_ACK_OR_NAK)
		if(packt.payload=="ACK"):
			# Received an ACK. Everything's fine.
			self.state=WAITING_FOR_CALL_FROM_ABOVE
		elif(packt.payload=="NAK"):
			# Received a NAK. Need to resend packet.
			self.channel.udt_send(self.packet_to_be_sent)
		else:
			print("ERROR! rdt_rcv() was expecting an ACK or a NAK. Received a corrupted packet.")
			print("Halting simulation...")
			sys.exit(0)

			

class rdt_Receiver(object):
	def __init__(self,env):
		# Initialize variables
		self.env=env 
		self.receiving_app=None
		self.channel=None
		

	def rdt_rcv(self,packt):
		# This function is called by the lower-layer when a packet arrives
		# at the receiver
		
		# check whether the packet is corrupted
		if(packt.corrupted):
			# send a NAK and discard this packet.
			response = Packet(seq_num=0, payload="NAK") #Note: seq_num for the response can be arbitrary. It is ignored.
			# send it over the channel
			self.channel.udt_send(response)
		else:
			# The packet is not corrupted.
			# Send an ACK and deliver the data.
			response = Packet(seq_num=0, payload="ACK") 
			# send it over the channel
			self.channel.udt_send(response)
			self.receiving_app.deliver_data(packt.payload)

