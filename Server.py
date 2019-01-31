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

    def gameUpdate(self, t):
        self.send(str({'data-type': 'game-update',
                       'lives': self.gameWords[t]['lives'],
                       'missing': self.gameWords[t]['missing'],
                       'token': t}))

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
                            if sessionData['data-type'] == 'game-start':
                                gameToken = sessionData['token']
                                gameLives = sessionData['lives']
                                gameWord = sessionData['word']
                                missingWord = len(gameWord) * '_'
                                self.gameWords[gameToken] = {'lives': gameLives, 'word': gameWord, 'missing': missingWord, 'letters': []}
                                Logger.log(F'Started match with word: {gameWord} [{gameToken}] lives: {gameLives}', 'GAME')
                                continue
                            elif sessionData['data-type'] == 'refresh':
                                self.send(str({'data-type': 'game-update', 'word': self.gameWords[sessionData['token']]['word'], 'lives': self.gameWords[sessionData['token']]['lives'], 'missing': self.gameWords[sessionData['token']]['missing'], 'token': sessionData['token']}))
                                continue
                            elif sessionData['data-type'] == 'letter-guess':
                                gameLetter = sessionData['letter'].upper()
                                gameLetters = self.gameWords[sessionData['token']]['letters']
                                gameWord = self.gameWords[sessionData['token']]['word'].upper()
                                gameLives = int(self.gameWords[sessionData['token']]['lives'])
                                gameMissing = self.gameWords[sessionData['token']]['missing'].upper()
                                if gameLetter not in list(gameWord):
                                    self.gameWords[sessionData['token']]['lives'] = str(int(gameLives) - 1)
                                    self.gameUpdate(sessionData['token'])
                                else:
                                    missingWord = gameMissing
                                    if gameLetter not in gameLetters:
                                        for x in range(len(list(gameWord))):
                                            if list(gameWord)[x] == gameLetter:
                                                Temp = list(missingWord)
                                                Temp[x] = gameLetter
                                                missingWord = ''.join(Temp)
                                        self.gameWords[sessionData['token']]['missing'] = missingWord
                                        self.gameUpdate(sessionData['token'])
                                    if '_' not in list(missingWord):
                                        self.send(str({'data-type': 'over', 'word': self.gameWords[sessionData['token']]['word'], 'token': sessionData['token']}))
                                if int(self.gameWords[sessionData['token']]['lives']) <= 0:
                                    self.send(str({'data-type': 'over', 'word': self.gameWords[sessionData['token']]['word'], 'token': sessionData['token']}))
                                continue
                            elif sessionData['data-type'] == 'word-guess':
                                guessedWord = sessionData['word'].upper()
                                gameWord = self.gameWords[sessionData['token']]['word'].upper()
                                if guessedWord == gameWord:
                                    self.send(str({'data-type': 'over', 'word': self.gameWords[sessionData['token']]['word'], 'token': sessionData['token']}))
                                else:
                                    self.send(str({'data-type': 'game-notification', 'chat': 'Someone guessed incorrectly!', 'token': sessionData['token']}))
                                continue
                            self.send(receivedData)
            except Exception as error:
                Logger.error(error)


if __name__ == '__main__':
    Server = Host()
    Server.run()
