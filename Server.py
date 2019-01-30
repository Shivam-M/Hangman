import socket
import select
import time
from ast import literal_eval
from threading import Thread
from tools.Logger import Logger


class Host:
    def __init__(self):
        self.connectionIP = '0.0.0.0'
        self.connectionPort = 6666

        self.LIST = []
        self.connectedUsers = {}
        self.gameWords = {}
        self.gameTokens = []
        self.gameSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.gameSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

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
                            print(receivedData)
                            try:
                                sessionData = literal_eval(receivedData)
                            except:
                                continue
                            if sessionData['token'] not in self.gameTokens:
                                self.gameTokens.append(sessionData['token'])
                                self.gameWords[sessionData['token']] = ''
                            if sessionData['data-type'] == 'game-word':
                                try:
                                    if self.gameWords[sessionData['token']]['game-word']:
                                        try:
                                            if self.gameWords[sessionData['token']]['over'] == 'true':
                                                self.gameWords[sessionData['token']] = {'game-word': sessionData['word']}
                                                self.gameWords[sessionData['token']]['missing-word'] = '_' * len(sessionData['word'])
                                                self.gameWords[sessionData['token']]['over'] = 'false'
                                                self.gameWords[sessionData['token']]['game-lives'] = '10'
                                        except:
                                            pass
                                except:
                                    self.gameWords[sessionData['token']] = {'game-word': sessionData['word']}
                                    self.gameWords[sessionData['token']]['missing-word'] = '_' * len(sessionData['word'])
                                    print(str(self.gameWords))
                            elif sessionData['data-type'] == 'game-lives':
                                self.gameWords[sessionData['token']]['game-lives'] = sessionData['lives']
                                continue
                            elif sessionData['data-type'] == 'letter-guess':
                                gameWord = self.gameWords[sessionData['token']]['game-word']
                                print(gameWord)
                                if sessionData['letter'].upper() not in list(gameWord.upper()):
                                    time.sleep(0.3)
                                    gameLives = int(self.gameWords[sessionData['token']]['game-lives']) - 1
                                    self.gameWords[sessionData['token']]['game-lives'] = str(gameLives)
                                    self.send(str({'data-type': 'game-lives', 'lives': str(gameLives), 'token': sessionData['token'], 'override': 'true'}))
                                else:
                                    for x in range(len(list(gameWord))):
                                        if list(gameWord.upper())[x] == sessionData['letter'].upper():
                                            Temp = list(self.gameWords[sessionData['token']]['missing-word'].upper())
                                            Temp[x] = sessionData['letter']
                                            missingWord = ''.join(Temp)
                                            self.gameWords[sessionData['token']]['missing-word'] = missingWord
                                            if '_' not in list(missingWord) or int(self.gameWords[sessionData['token']]['game-lives']) <= 0:
                                                self.gameWords[sessionData['token']]['over'] = 'true'
                                            self.send(str({'data-type': 'missing-word', 'word': missingWord, 'token': sessionData['token']}))
                                continue
                            self.send(receivedData)
            except Exception as error:
                Logger.error(error)


if __name__ == '__main__':
    Server = Host()
    Server.run()
