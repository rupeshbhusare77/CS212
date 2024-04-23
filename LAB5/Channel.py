# SimPy model for an unreliable communication channel.
#
#	A packet sent over this channel:
#		- can get corrupted, with probability Pc
#		- can get lost, with probability Pl
#		- reaches the other end after a "propagation_delay" amount of time, if it is not lost.
#
# Author: Neha Karanjkar


import simpy
import random
from Packet import Packet
import copy


class UnreliableChannel(object):

	def __init__(self,env,name,Pc,Pl,propagation_delay,transmission_rate):
		# Initialize variables
		self.env=env 
		self.name=name
		self.Pc=Pc
		self.Pl=Pl
		self.propagation_delay=propagation_delay
		self.transmission_rate=transmission_rate
		self.receiver=None

		# some variables to maintain stats
		self.channel_utilization_time=0.0 # total amount of time for which the channel was utilized for transmission
	
	def udt_send(self,packt_to_be_sent):
		# this function is called by the sending-side 
		# to send a new packet over the channel.
		packt=copy.copy(packt_to_be_sent) #!!! BEWARE: Python uses pass-by-reference by default.Thus a copy() is necessary
		print("TIME:",self.env.now,self.name,": udt_send called for",packt)
		# start a process to deliver this packet across the channel.
		self.env.process(self.deliver_packet_over_channel(self.propagation_delay, packt))
		
		# update stats
		transmission_delay_for_packet = packt.packet_length / self.transmission_rate
		self.channel_utilization_time += transmission_delay_for_packet
		


	def deliver_packet_over_channel(self, propagation_delay, packt_to_be_delivered):
		packt=copy.copy(packt_to_be_delivered)
		
		# Is this packet corrupted?
		if random.random()<self.Pc:
			packt.corrupt()
			print("TIME:",self.env.now,self.name,":",packt,"was corrupted!")

		# Is this packet lost?
		if random.random()<self.Pl:
			print("TIME:",self.env.now,self.name,":",packt,"was lost!")
		else:
			# If the packet isn't lost, it should reach the destination.
			# Now wait for "propagation_delay" amount of time
			yield self.env.timeout(propagation_delay)
			# deliver the packet by calling the rdt_rcv()
			# function on the receiver side.
			self.receiver.rdt_rcv(packt)
		
