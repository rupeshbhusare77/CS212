# Simulation Testbench
#
# Author: Rupesh Bhusare, Vaibhav Gupta


import simpy
from q5_Applications import SendingApplication,ReceivingApplication
from Channel import UnreliableChannel
# from Protocol_rdt3 import *
import Protocol_rdt3 
from Protocol_rdt3 import *

# Create a simulation environment
probability = 0 
listofT = [] 
for i in range(10): 
    env=simpy.Environment()
    # total_messages = 1000
    # Populate the simulation environment with objects:
    sending_app	  = SendingApplication(env)
    receiving_app = ReceivingApplication(env)
    rdt_sender = rdt_Sender(env)
    rdt_receiver  = rdt_Receiver(env)

    channel_for_data  = UnreliableChannel(env=env,Pc=0.2,Pl=probability,delay=2,name="DATA_CHANNEL")
    channel_for_ack	  = UnreliableChannel(env=env,Pc=0.2,Pl=probability,delay=2,name="ACK_CHANNEL")

    # connect the objects together
    # .....forward path...
    sending_app.rdt_sender = rdt_sender
    rdt_sender.channel = channel_for_data
    channel_for_data.receiver = rdt_receiver
    rdt_receiver.receiving_app = receiving_app
    # ....backward path...for acks
    rdt_receiver.channel = channel_for_ack
    channel_for_ack.receiver = rdt_sender
    
#  Run simulation
# env.run(until=100)

# run the simulation until all 1000 messages are positively ack


    env.run()
    listofT.append(sum(sending_app.rdt_sender.time_avg_list)/100)
    probability += 0.1
print(listofT)
# to calculate and print avg round-trip-time(RTT avg)
# T_total = env.now
# T_avg = T_total / 1000
# print(f"Avg Round-trip time (RTT avg): {T_avg} ")
