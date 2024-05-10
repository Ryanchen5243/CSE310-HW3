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
            # obtain the usernmae for the given sender
            key_list = list(self.active_clients.keys())
            val_list = list(self.active_clients.values())
            sender_username = None
            try:
                sender_username = key_list[val_list.index(client)]
            except ValueError: # when join hasnt been processed yet
                pass

            if packet_type == util.DATA_PACKET_TYPE:
                message = data.split()[0]

                if message == util.JOIN_MESSAGE:
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
                elif message == util.REQUEST_USERS_LIST_MESSAGE:
                    response = util.make_packet(util.DATA_PACKET_TYPE,0,
                                                util.make_message(util.RESPONSE_USERS_LIST_MESSAGE,
                                                util.TYPE_THREE_MSG_FORMAT,
                                                ' '.join(sorted(self.active_clients.keys()))))
                    self.sock.sendto(response.encode(), client)
                    print("request_users_list: {}".format(sender_username))
                elif message == util.SEND_MESSAGE_MESSAGE:
                    # forward message to corresponding recipient clients

                    num_recipients = int(data.split()[2])
                    data = data.split()[3:]
                    recipients = data[0:num_recipients]
                    message = ' '.join(data[num_recipients:])

                    invalid_clients = []
                    for r in recipients:
                        if r in self.active_clients:
                            recipient_addr,recipient_port = self.active_clients.get(r)
                            # forward message
                            fwd_response_msg = "1 {} {}".format(sender_username,message)
                            response = util.make_packet(util.DATA_PACKET_TYPE,0,util.make_message(
                                util.FORWARD_MESSAGE_MESSAGE,util.TYPE_FOUR_MSG_FORMAT,fwd_response_msg
                            ))
                            self.sock.sendto(response.encode(), (recipient_addr,recipient_port))
                            print("msg: {}".format(sender_username))
                        else:
                            invalid_clients.append(r)

                    for non_existent_client in invalid_clients:
                        print("msg: {} to non-existent user {}".format(
                            sender_username,non_existent_client
                        ))

                elif message == util.DISCONNECT_MESSAGE:
                    self.active_clients.pop(sender_username, None)
                    print("disconnected: {}".format(sender_username))
                else:
                    pass

            elif packet_type == util.START_PACKET_TYPE:
                pass
            elif packet_type == util.END_PACKET_TYPE:
                pass
            elif packet_type == util.ACK_PACKET_TYPE:
                pass
            else:
                pass

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
