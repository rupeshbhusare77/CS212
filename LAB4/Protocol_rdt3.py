
# Author: Rupesh Bhusare (2203106), Vaibhav Gupta(2203134)

from os import stat
import simpy
import random
from Packet import Packet
import sys

# the sender can be in any of the first 4 and reciver will be in last 2 states:
SENDER_WAITING_FOR_CALL_ZERO_FROM_ABOVE = 0
SENDER_WAITING_FOR_CALL_ONE_FROM_ABOVE = 1
WAIT_FOR_ACK_ZERO = 2
WAIT_FOR_ACK_ONE = 3
RECIEVER_WAITING_FROM_CALL_ZERO_FROM_ABOVE = 4
RECIEVER_WAITING_FROM_CALL_ONE_FROM_ABOVE = 5

# some global variables
total_pkts_ack = 0   # Number of ACK recieved
T_avg = 0   # Total Round-Trip-Time (RTT)


class rdt_Sender(object):
    def __init__(self,env):
        # Initialize variables
        self.env=env 
        self.channel=None
        self.start_time=0 
        self.end_time=0
		# some state variables
        self.state = SENDER_WAITING_FOR_CALL_ZERO_FROM_ABOVE
        self.packet_to_be_sent=None
        self.time_avg_list = [] 
        # some additional timer-related variables
        self.timeout_value=10
        self.timer_is_running=False
        self.timer=None
    
    # this function models the timer's behaviour
    def timer_behaviour(self):
        try:
            # start timer
            self.timer_is_running = True
            yield self.env.timeout(self.timeout_value)
            # stop timer
            self.timer_is_running = False
            self.timeout_actions() # take some actions
        except simpy.Interrupt:
            # stop timer
            self.timer_is_running = False

    # this function can be called to start the timer
    def start_timer(self):
        assert(self.timer_is_running == False)
        self.timer = self.env.process(self.timer_behaviour())

    # this function can be called to stop the timer
    def stop_timer(self):
        assert(self.timer_is_running == True)
        self.timer.interrupt()

    # actions to be performed upon a timeout event
    def timeout_actions(self):
        self.channel.udt_send(self.packet_to_be_sent)
        print("Time: ",self.env.now," Timeout! Sending again ...")
        self.start_timer()

    def rdt_send(self,msg):
        if self.state==SENDER_WAITING_FOR_CALL_ZERO_FROM_ABOVE:
			# This function is called by the 
			# sending application.
			# create a packet, and save a copy of this packet
			# for retransmission, if needed
            self.packet_to_be_sent = Packet(seq_num=0, payload=msg)
			# send it over the channel
            self.start_time = self.env.now 
            self.channel.udt_send(self.packet_to_be_sent)
            # wait for an ACK or NAK
            self.start_timer()
            self.state=WAIT_FOR_ACK_ZERO
            return True
        
        elif self.state==SENDER_WAITING_FOR_CALL_ONE_FROM_ABOVE:
            # This function is called by the 
			# sending application.
			# create a packet, and save a copy of this packet
			# for retransmission, if needed
            self.packet_to_be_sent = Packet(seq_num=1, payload=msg)
			# send it over the channel
            self.start_time = self.env.now 
            self.channel.udt_send(self.packet_to_be_sent)
            # wait for an ACK or NAK
            self.start_timer()
            self.state=WAIT_FOR_ACK_ONE
            return True
        
        else:
            return False
            
    def rdt_rcv(self,packt):
        global total_pkts_ack, T_avg
		# This function is called by the lower-layer 
		# # when an ACK=0/ACK=1 packet arrives
        # assert(self.state==WAIT_FOR_ACK_ZERO or self.state==WAIT_FOR_ACK_ONE)

        if (self.state==WAIT_FOR_ACK_ZERO):
            if (not packt.corrupted and (packt.payload=="ACK" and packt.seq_num==0) and self.timer_is_running):
			    # Received an ACK,0. Everything's fine.
                self.end_time = self.env.now
                T_avg =  self.end_time - self.start_time
                self.time_avg_list.append(T_avg)
                self.stop_timer()
                self.state=SENDER_WAITING_FOR_CALL_ONE_FROM_ABOVE
                total_pkts_ack+=1
                if(total_pkts_ack == 1000):
                    print("1000 pkts ACKNOWLEGDED. Simulation Completed...")
                    print(f"T_avg = {T_avg/1000}")
                    sys.exit(0)

        elif (self.state==WAIT_FOR_ACK_ONE):
            if (not packt.corrupted and (packt.payload=="ACK" and packt.seq_num==1) and self.timer_is_running):
			    # Received an ACK,1. Everything's fine.
                self.stop_timer()
                self.state=SENDER_WAITING_FOR_CALL_ZERO_FROM_ABOVE
                

class rdt_Receiver(object):
    def __init__(self,env):
        # Initialize variables
        self.env=env
        self.state=RECIEVER_WAITING_FROM_CALL_ZERO_FROM_ABOVE
        self.receiving_app=None
        self.channel=None
        self.packet_to_be_sent=None
		
    def rdt_rcv(self,packt):
		# This function is called by the lower-layer when a packet arrives
		# at the receiver
		
        if(self.state==RECIEVER_WAITING_FROM_CALL_ZERO_FROM_ABOVE):
            if(packt.corrupted or packt.seq_num==1):
                # Recieved a seq=1 or pkt is corrupted. Need to resend packet.
                self.packet_to_be_sent = Packet(seq_num=1, payload="ACK")
                self.channel.udt_send(self.packet_to_be_sent)
            
            elif(not packt.corrupted and packt.seq_num==0):
                # send it over the channel
                self.receiving_app.deliver_data(packt.payload)
                # The packet is not corrupted.
                # Send an ACK,0 and deliver the data.
                self.packet_to_be_sent = Packet(seq_num=0, payload="ACK") 
                self.channel.udt_send(self.packet_to_be_sent)
                self.state=RECIEVER_WAITING_FROM_CALL_ONE_FROM_ABOVE

        elif(self.state==RECIEVER_WAITING_FROM_CALL_ONE_FROM_ABOVE):
            if(packt.corrupted or packt.seq_num==0):
                # Recieved a seq=0 or pkt is corrupted. Need to resend packet.
                self.packet_to_be_sent = Packet(seq_num=0, payload="ACK")
                self.channel.udt_send(self.packet_to_be_sent)
            
            elif(not packt.corrupted and packt.seq_num==1):
                # send it over the channel
                self.receiving_app.deliver_data(packt.payload)
                # The packet is not corrupted.
                # Send an ACK,1 and deliver the data.
                self.packet_to_be_sent = Packet(seq_num=1, payload="ACK") 
                self.channel.udt_send(self.packet_to_be_sent)
                self.state=RECIEVER_WAITING_FROM_CALL_ZERO_FROM_ABOVE