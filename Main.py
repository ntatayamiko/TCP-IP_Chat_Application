import socket
from os import remove

import select
import sys
from _thread import *

##### SERVER #####

server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

#Check whether sufficient arguments have been provided
if len(sys.argv)!=3:
    print("Correct usage: Script, IP address, Port number")
    exit()

#Take the first and 2nd arg from prompt as IP address & Port number
IP_address=str(sys.argv[1])
Port=str(sys.argv[2])

#Bind the server to Ip address & port# (the client must be aware of these parameters)
server.bind((IP_address,Port))

#Listen to 5 active connections
server.listen(5)
list_of_clients=[]

def client_thread(conn,addr):
    conn.send("Welcome to this chart room")
    while True:
        try:
            message=conn.recv(2048)
            if message: #Prints the message & addr of the user who sent the message on the server
                print("<" + addr[0] + ">" + message)
                #Calls broadcast func to send message to all
                message_to_send= "<" + addr[0] + ">" + message
                broadcast(message_to_send,conn)

            else: #Message may have no content if the connection is broken in this case we remove the connection
                remove(conn)

        except:
            continue

#function to broadcast message to all clients who's object is not the same as the one sending the message
def broadcast(message,connection):
    for clients in list_of_clients:
        if clients != connection:
            try:
                clients.send(message)
            except:
                clients.close()
                remove(clients) #If the link is broken we remove the client

#Function that removes the object from the list that was created at the beginning of the program
def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)

#Accept a connection request and store two parameters, conn=socket object for that user, addr= connected client address
while True:
    conn,addr=server.accept()
    list_of_clients.append(conn) #Maintains a list of clients for ease of broadcasting to available people
    print(addr[0] + "connected") #Prints the address of the user that just connected
    start_new_thread(client_thread,(conn,addr)) #Creates an individual thread for every user that connects

conn.close()
server.close()

#########Client script
client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 3:
    print("correct usage: script, IP address, port#")
    exit()

IP_address=str(sys.argvv[1])
port=int(sys.argv[2])
server.connect((IP_address,port))

while True:
    sockets_list=[sys.stdin, server] #maintains a list of possible input streams
    """There are two possible input situations. Either the user wants to give manual input to send to other
    people, or the server is sending a message to be printed on the screen. Select returns from sockets_list, the
    stream that is reader for input. eg., if the server wants to send a message, then the if condition will
    hold true below. if the user wants to send a message, the else statement will evaluate as true"""
    read_sockets,write_socket,error_socket=select.select(sockets_list,[],[])
    for socks in read_sockets:
        if socks==server:
            message= socks.recv(2048)
            print(message)
        else:
            message=sys.stdin.readline()
            server.send(message)
            sys.stdout.write("<you>")
            sys.stdout.write(message)
            sys.stdout.flush()
server.close()
