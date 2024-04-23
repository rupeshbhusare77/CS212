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
WAITING_FOR_CALL_0_FROM_ABOVE =0
WAITING_FOR_CALL_1_FROM_ABOVE =1
WAIT_FOR_ACK_0=2
WAIT_FOR_ACK_1=3
WAIT_FOR_PACKT_0=4
WAIT_FOR_PACKT_1=5




class rdt_Sender(object):

	def __init__(self,env):
		# Initialize variables
		self.env=env 
		self.channel=None
		
		# some state variables
		self.state = WAITING_FOR_CALL_0_FROM_ABOVE
		self.seq_num=0
		self.packet_to_be_sent=None

	
	def rdt_send(self,msg):

		if self.state==WAITING_FOR_CALL_0_FROM_ABOVE:
			# This function is called by the 
			# sending application.
			
			# create a packet, and save a copy of this packet
			# for retransmission, if needed
			self.packet_to_be_sent = Packet(seq_num=self.seq_num, payload=msg)
			# send it over the channel
			self.channel.udt_send(self.packet_to_be_sent)
			# wait for an ACK or NAK
			self.seq_num = 1
			self.state=WAIT_FOR_ACK_0
			return True
		elif self.state==WAITING_FOR_CALL_1_FROM_ABOVE:
			# This function is called by the 
			# sending application.
			
			# create a packet, and save a copy of this packet
			# for retransmission, if needed
			self.packet_to_be_sent = Packet(seq_num=self.seq_num, payload=msg)
			# send it over the channel
			self.channel.udt_send(self.packet_to_be_sent)
			self.seq_num = 0
			# wait for an ACK or NAK
			self.state=WAIT_FOR_ACK_1
			return True
		else:
			return False
	
	def rdt_rcv(self,packt):
		# This function is called by the lower-layer 
		# when an ACK/NAK packet arrives
		assert(self.state==WAIT_FOR_ACK_1 or self.state==WAIT_FOR_ACK_0)
		if self.state==WAIT_FOR_ACK_1:
			if(packt.payload=="ACK1"):
				# Received an ACK. Everything's fine.
				self.state=WAITING_FOR_CALL_0_FROM_ABOVE
			elif(packt.payload=="ACK0"):
				# Received a NAK. Need to resend packet.
				# self.seq_num=1-self.seq_num
				self.channel.udt_send(self.packet_to_be_sent)

			else:
				self.channel.udt_send(self.packet_to_be_sent)
			# 	print("ERROR! rdt_rcv() was expecting an ACK or a NAK. Received a corrupted packet.")
			# 	print("Halting simulation...")
			# 	sys.exit(0)
		if self.state==WAIT_FOR_ACK_0:
			if(packt.payload=="ACK0"):
				# Received an ACK. Everything's fine.
				self.state=WAITING_FOR_CALL_1_FROM_ABOVE
			elif(packt.payload=="ACK1"):
				# Received a NAK. Need to resend packet.
				# self.seq_num=1-self.seq_num
				self.channel.udt_send(self.packet_to_be_sent)
			else:
				self.channel.udt_send(self.packet_to_be_sent)
			# else:
			# 	print("ERROR! rdt_rcv() was expecting an ACK or a NAK. Received a corrupted packet.")
			# 	print("Halting simulation...")
			# 	sys.exit(0)
			

class rdt_Receiver(object):
	def __init__(self,env):
		# Initialize variables
		self.env=env 
		self.receiving_app=None
		self.channel=None
		self.seq_number=0
		self.state=WAIT_FOR_PACKT_0
	def rdt_rcv(self,packt):
		# This function is called by the lower-layer when a packet arrives
		# at the receiver
		if self.state == WAIT_FOR_PACKT_0:
		# check whether the packet is corrupted
			if(packt.corrupted) or (self.seq_number!=packt.seq_num):
				# send a NAK and discard this packet.
				response = Packet(seq_num=1, payload="ACK1")
				self.channel.udt_send(response)
	
				# if self.seq_num == 0:
				# 	response = Packet(seq_num=1 - self.seq_num, payload="ACK1")
				# 	self.channel.udt_send(response)
				# elif self.seq_num == 1:
				# 	response = Packet(seq_num=1 - self.seq_num, payload="ACK0")
				# 	self.channel.udt_send(response)
			else:
				response = Packet(seq_num=0, payload="ACK0")
				self.state=WAIT_FOR_PACKT_1
				self.channel.udt_send(response)
				self.seq_number=1
				# self.channel.udt_send(response)
				self.receiving_app.deliver_data(packt.payload)
		elif self.state == WAIT_FOR_PACKT_1:
		# check whether the packet is corrupted
			if (packt.corrupted) :
				# send a NAK and discard this packet.
				response = Packet(seq_num=0, payload="ACK0")
				self.channel.udt_send(response)
	
				# if self.seq_num == 0:
				# 	response = Packet(seq_num=1 - self.seq_num, payload="ACK1")
				# 	self.channel.udt_send(response)
				# elif self.seq_num == 1:
				# 	response = Packet(seq_num=1 - self.seq_num, payload="ACK0")
				# 	self.channel.udt_send(response)
			elif (self.seq_number!=packt.seq_num) : 
				# print("ererf")
				response = Packet(seq_num=0, payload="ACK0")
				self.channel.udt_send(response)
			
			else:
				response = Packet(seq_num=1, payload="ACK1")
				# print("HIhIHih",packt.corrupted, self.seq_number == 0)
				self.state=WAIT_FOR_PACKT_0
				self.channel.udt_send(response)
				self.seq_number=0
				# self.channel.udt_send(response)
				self.receiving_app.deliver_data(packt.payload)