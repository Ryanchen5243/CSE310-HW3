'''
This module defines the behaviour of a client in your Chat Application
'''
import sys
import getopt
import socket
import random
from threading import Thread
import os
import util


'''
Write your code inside this class. 
In the start() function, you will read user-input and act accordingly.
receive_handler() function is running another thread and you have to listen 
for incoming messages in this function.
'''

class Client:
    '''
    This is the main Client Class. 
    '''
    def __init__(self, username, dest, port, window_size):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(None)
        self.sock.bind(('', random.randint(10000, 40000)))
        self.name = username

        # additional variables
        # self.close_connection = False

    def start(self):
        '''
        Main Loop is here
        Start by sending the server a JOIN message. 
        Use make_message() and make_util() functions from util.py to make your first join packet
        Waits for userinput and then process it
        '''
        # implementation
        print("username is ", USER_NAME)
        message = util.make_message(util.JOIN_MESSAGE,util.TYPE_ONE_MSG_FORMAT,USER_NAME)
        packet = util.make_packet(util.DATA_PACKET_TYPE,0,message)
        self.sock.sendto(packet.encode(), (self.server_addr, self.server_port))

        # listens for messages from server
        self.receive_handler()

    def receive_handler(self):
        '''
        Waits for a message from server and process it accordingly
        '''
        # implementation
        while True:
            print("waiting for message from server...")
            msg, _ = self.sock.recvfrom(util.CHUNK_SIZE)
            packet_type, seqno, data, checksum = util.parse_packet(msg.decode())
            match packet_type:
                case util.DATA_PACKET_TYPE:
                    message = data.split()[0]
                    match message:
                        case util.ERR_SERVER_FULL_MESSAGE:
                            print("received ERR_SERVER_FULL_MESSAGE from server")
                            # close the connection to server and shut down
                            print("disconnected: server full")
                        case util.ERR_USERNAME_UNAVAILABLE_MESSAGE:
                            print("received err username unavailable msg from server")
                            # close the connection to server and shut down
                            print("disconnected: username not available")
                        case _:
                            print("other message kind")
                case util.START_PACKET_TYPE:
                    print("Start packet type")
                case util.END_PACKET_TYPE:
                    print("End packet type")
                case util.ACK_PACKET_TYPE:
                    print("Ack packet type")
                case _:
                    print("invalid packet type")

            print("Received msg from server:: ",msg)
        # close connection
        # self.sock.close()

# Do not change below part of code
if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our Client module completion
        '''
        print("Client")
        print("-u username | --user=username The username of Client")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW_SIZE | --window=WINDOW_SIZE The window_size, defaults to 3")
        print("-h | --help Print this help")
    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "u:p:a:w", ["user=", "port=", "address=","window="])
    except getopt.error:
        helper()
        exit(1)

    PORT = 15000
    DEST = "localhost"
    USER_NAME = None
    WINDOW_SIZE = 3
    for o, a in OPTS:
        if o in ("-u", "--user="):
            USER_NAME = a
        elif o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a
        elif o in ("-w", "--window="):
            WINDOW_SIZE = a

    if USER_NAME is None:
        print("Missing Username.")
        helper()
        exit(1)

    S = Client(USER_NAME, DEST, PORT, WINDOW_SIZE)
    try:
        # Start receiving Messages
        T = Thread(target=S.receive_handler)
        T.daemon = True
        T.start()
        # Start Client
        S.start()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
