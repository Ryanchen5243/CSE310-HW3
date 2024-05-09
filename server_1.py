'''
This module defines the behaviour of server in your Chat Application
'''
import sys
import getopt
import socket
import util

class Server:
    '''
    This is the main Server Class. You will  write Server code inside this class.
    '''
    def __init__(self, dest, port, window):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(None)
        self.sock.bind((self.server_addr, self.server_port))

        # additional variables
        self.active_clients = {} # username : (client_ip_addr,client_port)

    def start(self):
        '''
        Main loop.
        continue receiving messages from Clients and processing it.

        '''
        # implementation
        while True:
            # listen for messages from clients
            msg,client = self.sock.recvfrom(util.CHUNK_SIZE)
            packet_type, seqno, data, checksum = util.parse_packet(msg.decode())
            match packet_type:
                case util.DATA_PACKET_TYPE:
                    message = data.split()[0]
                    match message:
                        case util.JOIN_MESSAGE:
                            print("join messaged detected")
                            # check for server full
                            if len(self.active_clients) == util.MAX_NUM_CLIENTS:
                                response = util.make_packet(util.DATA_PACKET_TYPE,0,
                                                            util.make_message(util.ERR_SERVER_FULL_MESSAGE,
                                                                              util.TYPE_TWO_MSG_FORMAT))
                                self.sock.sendto(response.encode(), client)
                                print("disconnected: server full")
                                continue

                            # check for existing username
                            client_username = data.split()[-1]
                            if client_username in self.active_clients:
                                response = util.make_packet(util.DATA_PACKET_TYPE,0,
                                                            util.make_message(util.ERR_USERNAME_UNAVAILABLE_MESSAGE,
                                                                              util.TYPE_TWO_MSG_FORMAT))
                                self.sock.sendto(response.encode(), client)
                                print("disconnected: username not available")
                                continue
                            # add user
                            self.active_clients[client_username] = client
                            print("join: {}".format(client_username))
                        case util.REQUEST_USERS_LIST_MESSAGE:
                            print("request user list msg detected")
                            response = util.make_packet(util.DATA_PACKET_TYPE,0,
                                                      util.make_message(util.RESPONSE_USERS_LIST_MESSAGE,
                                                        util.TYPE_THREE_MSG_FORMAT,
                                                        sorted(self.active_clients.keys())))
                            self.sock.sendto(response.encode(), client)
                            print("request_users_list: {}".format(client_username))
                        case util.SEND_MESSAGE_MESSAGE:
                            print("server receved.. ",data)

# Receiver Action: The server forwards this message to each user whose name is specified in the
# request. It will also print:
# msg: <sender username>
# For each username that does not correspond to any client, the server will print:
# msg: <sender username> to non-existent user <recv. username>
                        case _:
                            print("other message detected")

                case util.START_PACKET_TYPE:
                    print("Start packet type")
                case util.END_PACKET_TYPE:
                    print("End packet type")
                case util.ACK_PACKET_TYPE:
                    print("Ack packet type")
                case _:
                    print("invalid packet type")

# Do not change below part of code

if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our module completion
        '''
        print("Server")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW | --window=WINDOW The window size, default is 3")
        print("-h | --help Print this help")

    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "p:a:w", ["port=", "address=","window="])
    except getopt.GetoptError:
        helper()
        exit()

    PORT = 15000
    DEST = "localhost"
    WINDOW = 3

    for o, a in OPTS:
        if o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a
        elif o in ("-w", "--window="):
            WINDOW = a

    SERVER = Server(DEST, PORT,WINDOW)
    try:
        SERVER.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
