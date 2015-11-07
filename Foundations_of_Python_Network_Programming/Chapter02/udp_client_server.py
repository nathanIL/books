"""
 Foundations of Python Network Programming
 ------------------------------------------
 Chapter 02 -   Super naive Client / Server with basic backoff support (for UDP client) to avoid congestion.
                The server (when used with UDP) randomly drops packets to simulate a packet loss.
"""
import socket
import argparse
import time
import random
from collections import deque


def parse_arguments():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='type')
    server_parser = subparsers.add_parser('server', help='Run as a server')
    client_parser = subparsers.add_parser('client', help='Run as a UDP (only) client')  # TCP is boring
    server_protocol = server_parser.add_mutually_exclusive_group()
    #server_protocol.add_argument('--tcp', help='Run a as TCP server', action='store_const', const=socket.SOCK_STREAM)
    server_protocol.add_argument('--udp', help='Run as a UDP server', action='store_const', const=socket.SOCK_DGRAM)
    server_parser.add_argument('--port', help='The port on which we listen', default=51150)
    client_parser.add_argument('--server', help='The server IP')
    client_parser.add_argument('--port', help='The server port', default=51150)
    return parser.parse_args()


def server(port, protocol=socket.SOCK_STREAM, address='0.0.0.0'):
    s = socket.socket(socket.AF_INET, protocol)
    if protocol == socket.SOCK_STREAM:
        pass
        # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # s.bind((address, port))
        # s.listen(1)
        # print("[TCP]: Server is listening on {0}:{1}".format(*s.getsockname()))
        # while True:
        #     (conn, addr) = s.accept()
        #     print("Connected Established from %s" % str(addr))
        #     while True:
        #         data = conn.recv(1024)
        #         print(data.rstrip())
        #         if not data: break
    elif protocol == socket.SOCK_DGRAM:
        s.bind((address, port))
        print("[UDP]: Server is listening on {0}:{1}".format(*s.getsockname()))
        while True:
            (data, addr) = s.recvfrom(1024)
            print(data.rstrip())
            if random.randint(0, 1):
                s.sendto("[Server]: Replying back", addr)


def client(server_address, port, timeout=1):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((server_address, int(port)))
    message = "[Client][%d] Congestion timeout: %.4f" % (time.time(), timeout)
    successful_requests_times = deque(maxlen=10)

    while True:
        time.sleep(timeout)
        s.settimeout(timeout)
        try:
            s.send(message)
            start = time.time()
            s.recv(1024)
            successful_requests_times.append(time.time() - start)
            timeout = sum(successful_requests_times) / len(successful_requests_times)
            message = "[Client][%d] Congestion timeout: %.4f" % (time.time(), timeout)
        except socket.timeout:
            if timeout < 5.0:
                timeout += 0.2
        except socket.error:
            if timeout < 5.0:
                timeout += 0.5


if __name__ == "__main__":
    arguments = parse_arguments()
    if arguments.type == 'server':
        proto = socket.SOCK_STREAM if arguments.tcp else socket.SOCK_DGRAM
        server(port=arguments.port, protocol=proto)
    elif arguments.type == 'client':
        client(arguments.server, arguments.port)
