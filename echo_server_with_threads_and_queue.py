import socket
import logging
import threading
import queue

logging.basicConfig(level=logging.DEBUG)

q = queue.Queue()
client_data = {}

EXIT_MSG = " has left the chat"
DISCONNECTED_MSG = "The connection with %s is broken"
IS_ALIVE_MSG = "ARE_YOU_ALIVE"
IS_ALIVE_RETURN_MSG = "CONNECTION_ALIVE"


def connection_to_socket_is_alive(socket):
    socket.send(IS_ALIVE_MSG.encode())
    data = socket.recv(1024).decode()
    if data == IS_ALIVE_RETURN_MSG:
        return True
    return False


def recv_data_from_user(client_name, client_socket):
    logging.info("Started thread for %s", client_name)
    global client_data, q
    while connection_to_socket_is_alive(client_socket):

        data = client_socket.recv(1024).decode()
        if data.strip() == "":  # empty strings are not allowed
            continue
        logging.info("%s RECEIVE THREAD: Received %s", client_name, data)
        string = client_name + ": " + data
        if not string == "%s: DISCONNECT" % client_name:
            q.put(string)

        else:
            logging.info("%s is exiting the chat", client_name)
            q.put(client_name + EXIT_MSG)
            del client_data[client_socket]
            break

    logging.info("connection with %s is broken")
    q.put(DISCONNECTED_MSG % client_name)
    del client_data[client_socket]


def echo_msg_to_connected_clients():
    while True:
        global q, client_data
        msg = q.get()
        logging.info("Echoing MSG: %s", msg)
        for sock in client_data:
            sock.send(msg.encode())


def run_server():
    threads = []
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listening_addr = "127.0.0.1"
    port = 5000
    server_socket.bind((listening_addr, port))

    logging.info("Server listening on %s:%d", listening_addr, port)
    server_socket.listen(5)

    echo_thread = threading.Thread(target=echo_msg_to_connected_clients)
    threads.append(echo_thread)
    echo_thread.start()

    while True:
        logging.info("waiting for new connection")

        sock, addr = server_socket.accept()
        logging.info("Accepted connection from %s", addr)

        message = "Please enter your name: "
        sock.send(message.encode())
        name = sock.recv(1024).decode()
        client_data[sock] = {}
        client_data[sock]['name'] = name
        client_data[sock]['address'] = addr

        client_connection_thread = threading.Thread(target=recv_data_from_user, args=(name, sock))
        client_connection_thread.daemon = True
        threads.append(client_connection_thread)
        client_connection_thread.start()


if __name__ == '__main__':
    run_server()
