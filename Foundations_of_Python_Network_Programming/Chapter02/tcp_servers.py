"""
Forking TCP Servers stuff based on book material (but not 1:1)
"""
import socket
import argparse
import time
import os
from multiprocessing import Process
from functools import partial


def args_handle(handlers, string):
    if string in handlers.keys():
        return handlers.get(string)
    else:
        raise argparse.ArgumentTypeError("Invalid server type provided")


def parse_arguments():
    """
    Parse command line arguments
    :return: argparse.Namespace object holding the arguments
    """
    HANDLERS = {h: o for h, o in globals().items() if h.startswith('handle_')}
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help='The port on which the server will listen', type=int, default=51150)
    parser.add_argument('--mproc', help='The maximum allowed clients / processes at a given time', type=int, default=10)
    parser.add_argument('--type', help='The server type: ' + ', '.join(HANDLERS.keys()), default='handle_fixed_request',
                        type=partial(args_handle, HANDLERS))

    return parser.parse_args()


def handle_fixed_request(connection, address, size=512):
    """
    Fixed size request handler
    :param connection: the socket / connection object received
    :param address: the remote address
    :param size: The maximum size of each request
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


def handle_http_request(connection, address):
    """
    Deadly naive and simple HTTP handler.
    :param connection: The socket
    :param address: The remote-end address
    """
    REQUIRED_HEADERS = ['Content-Length']
    SUPPORTED_METHODS = ['GET', 'POST']
    HTTP_VERSIONS = ['HTTP/1.1']
    headers = dict()
    headers_raw = ''
    body = ''

    while True:
        h = connection.recv(1024)
        if not h:
            break
        elif '\r\n' in h:
            crlf_idx = h.rfind('\r\n')
            headers_raw += h[:crlf_idx]
            body = h[crlf_idx:]
            break
        headers_raw += h

    # Parse Headers
    request_line = headers_raw.split('\n')[0].split()
    # TODO: Validate the resource element
    if len(request_line) != 3 or request_line[0] not in SUPPORTED_METHODS or request_line[2] not in HTTP_VERSIONS:
        print("[ERROR]: Invalid HTTP request line: " + ' '.join(request_line))
        return

    headers = {e.split(':')[0].strip():e.split(':')[1].strip() for e in headers_raw.splitlines()[1:]}
    print(headers)
    # Get body


def server(port, mproc, server_type):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', port))
    s.listen(mproc)

    print("[SERVER]: Listening on {0}".format(s.getsockname()))
    while True:
        (connection, address) = s.accept()
        print("[SERVER]: Connection established with {0}".format(address))
        process = Process(target=server_type, args=(connection, address))
        process.daemon = True
        process.start()


if __name__ == "__main__":
    args = parse_arguments()
    server(port=args.port, mproc=args.mproc, server_type=args.type)
