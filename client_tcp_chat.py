import socket
import logging
import threading
from echo_server_with_threads_and_queue import IS_ALIVE_RETURN_MSG, IS_ALIVE_MSG

logging.basicConfig(level=logging.DEBUG)


def read_function(client_socket):
    while True:
        data = client_socket.recv(1024).decode()
        if data == IS_ALIVE_MSG:
            client_socket.send(IS_ALIVE_RETURN_MSG.encode())
        else:
            print(data)


def write_function(client_socket):
    while True:
        logging.debug("WRITE_FUNCTION: waiting for input")
        message = input("-> ")
        logging.debug("Got message '%s'", message)
        if message != "STOP":
            client_socket.send(message.encode())
            logging.debug("sending to server: %s", message)
        else:
            logging.info("closing connection")
            client_socket.close()


def client_program():
    port = 5000
    client_socket = socket.socket()
    client_socket.connect(("127.0.0.1", port))

    data = client_socket.recv(1024)
    logging.info(data.decode())

    name = input(" -> ")  # take name
    client_socket.send(name.encode())

    read_thread = threading.Thread(target=read_function, args=(client_socket,))
    read_thread.daemon = True
    read_thread.start()

    write_thread = threading.Thread(target=write_function, args=(client_socket,))
    write_thread.daemon = True
    write_thread.start()

    write_thread.join()
    read_thread.join()


if __name__ == '__main__':
    client_program()
