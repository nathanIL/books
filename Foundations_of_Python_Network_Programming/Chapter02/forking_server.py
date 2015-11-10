"""
A forking TCP server
"""
import socket
import argparse
import time
import os
from multiprocessing import Process


def parse_arguments():
    """
    Parse command line arguments
    :return: argparse.Namespace object holding the arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help='The port on which the server will listen', type=int, default=51150)
    parser.add_argument('--mproc', help='The maximum allowed clients / processes at a given time', type=int, default=10)

    return parser.parse_args()


def handle_request(connection, address, size=512):
    """
    Asynchronously handle each request
    :param connection: the socket / connection object received
    :param address: the remote address
    """
    start = time.time()
    total_data = ''
    try:
        while len(total_data) < size:
            data = connection.recv(size - len(total_data))
            if not data:
                break
            print("[SERVER | PID {0}]: {1}".format(os.getpid(), data.rstrip()))
            total_data += data
    except Exception as e:
        print("Error ", e.message)
    finally:
        connection.close()
        end = time.time() - start
        print("[SERVER]: {0} closed connection after {1:.2f} seconds".format(address, end))


def server(port, mproc):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', port))
    s.listen(mproc)

    print("[SERVER]: Listening on {0}".format(s.getsockname()))
    while True:
        (connection, address) = s.accept()
        print("[SERVER]: Connection established with {0}".format(address))
        process = Process(target=handle_request, args=(connection, address))
        process.daemon = True
        process.start()


if __name__ == "__main__":
    args = parse_arguments()
    server(port=args.port, mproc=args.mproc)
