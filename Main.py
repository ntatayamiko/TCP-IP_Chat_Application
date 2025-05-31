import socket
import threading
import sys
from _thread import *

##### SERVER #####

server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

IP_address="localhost"
Port=6060

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

#function to broadcast message to all clients whos object is not the same as the one sending the message
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

#Accept a connection request and store two parameters, conn=socket_object for that user, addr= connected client address
def receive():
    while True:
        conn, addr = server.accept()
        list_of_clients.append(conn)  # Maintains a list of clients for ease of broadcasting to available people
        print(addr[0] + "connected")  # Prints the address of the user that just connected
        start_new_thread(client_thread, (conn, addr))  # Creates an individual thread for every user that connects
        conn.close()

server.close()

