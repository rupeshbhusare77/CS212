# SimPy model for an unreliable communication channel.
#
#	A packet sent over this channel:
#		- can get corrupted, with probability Pc
#		- can get lost, with probability Pl
#		- reaches the other end after "delay" amount of time, if it is not lost.
#
# Author: Neha Karanjkar


import simpy
import random
from Packet import Packet
import copy
class UnreliableChannel(object):

	def __init__(self,env,Pc,Pl,delay,name):
		# Initialize variables
		self.env=env 
		self.Pc=Pc
		self.Pl=Pl
		self.delay=delay
		self.receiver=None
		self.name=name
	
	def udt_send(self,packt_to_be_sent):
		# this function is called by the sending-side 
		# to send a new packet over the channel.
		packt=copy.copy(packt_to_be_sent) #!!! BEWARE: Python uses pass-by-reference by default.Thus a copy() is necessary
		print("TIME:",self.env.now,self.name,": udt_send called for",packt)
		# start a process to deliver this packet across the channel.
		self.env.process(self.deliver_packet_over_channel(self.delay, packt)) 
		


	def deliver_packet_over_channel(self, delay, packt_to_be_delivered):
		packt=copy.copy(packt_to_be_delivered)
		# Is this packet lost?
		if random.random()<self.Pl:
			print("TIME:",self.env.now,self.name,":",packt,"was lost!")
		else:
			# Is this packet corrupted?
			if random.random()<self.Pc:
				packt.corrupt()
				print("TIME:",self.env.now,self.name,":",packt,"was corrupted!")
			# Now wait for "delay" amount of time
			delay= random.randint(0,3*self.delay)
			yield self.env.timeout(delay)
			# deliver the packet by calling the rdt_rcv()
			# function on the receiver side.
			self.receiver.rdt_rcv(packt)
		
