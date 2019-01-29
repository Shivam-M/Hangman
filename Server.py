import socket
import select
from threading import Thread
from tools.Logger import Logger


class Host:
    def __init__(self):
        self.connectionIP = '0.0.0.0'
        self.connectionPort = 6666

        self.LIST = []
        self.connectedUsers = {}
        self.gameSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gameSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        self.THREAD_LISTEN = Thread(target=self.listen)

    def run(self):
        Logger.log(f'Starting server on {self.connectionIP}:{self.connectionPort}')
        self.gameSocket.bind((self.connectionIP, self.connectionPort))
        self.gameSocket.listen(10)
        self.LIST.append(self.gameSocket)
        self.THREAD_LISTEN.start()

    def send(self, m):
        try:
            for connectedSocket in self.LIST:
                if connectedSocket != self.gameSocket:
                    connectedSocket.send(str.encode(m))
        except Exception as error:
            Logger.error(error)
        Logger.log(m, 'MESSAGE')

    def listen(self):
        while True:
            try:
                read_sockets, write_sockets, error_sockets = select.select(self.LIST, [], [])
                for sock in read_sockets:
                    if sock == self.gameSocket:
                        sockfd, address = self.gameSocket.accept()
                        self.LIST.append(sockfd)
                        Logger.log(f'Client [{address[0]}:{address[1]}] connected to the server.', 'CONNECT')
                    else:
                        try:
                            receivedData = sock.recv(100).decode()
                        except:
                            try:
                                Logger.log(f'Client [{address[0]}:{address[1]}] disconnected from the server.', 'DISCONNECT')
                            except Exception as error:
                                Logger.error(error)
                            sock.close()
                            self.LIST.remove(sock)
                            continue
                        if receivedData:
                            self.send(receivedData)
            except Exception as error:
                Logger.error(error)


if __name__ == '__main__':
    Server = Host()
    Server.run()