import socket
import time
from threading import Thread
from ast import literal_eval
try:
    from Logger import Logger
except ImportError:
    from tools.Logger import Logger


# Network Manager for Hangman game: https://github.com/Shivam-M/Hangman
class NetworkM:
    def __init__(self, i, p, g):
        self.connectionIP = i
        self.connectPort = p
        self.gameInstance = g

        self.gameSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gameSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.gameSocket.settimeout(None)

        self.listeningThread = Thread(target=self.listen)
        self.activeConnection = True

    def connect(self):
        try:
            self.gameSocket.connect((self.connectionIP, self.connectPort))
            return True
        except:
            return False

    def run(self):
        if self.connect():
            Logger.log(f'Successfully connected to {self.connectionIP}:{self.connectPort}')
            self.listeningThread.start()
        else:
            Logger.log(f'Failed to connect to {self.connectionIP}:{self.connectPort}', 'ERROR')

    def send(self, m):
        try:
            self.gameSocket.send(str.encode(m))
            time.sleep(0.0125)
        except:
            Logger.log('Client is not currently connected to a game server', 'WARNING')

    def listen(self):
        while self.activeConnection:
            try:
                receivedData = self.gameSocket.recv(70).decode()
            except:
                receivedData = None
            if receivedData:
                try:
                    sessionData = literal_eval(receivedData)
                except:
                    continue
                if sessionData['token'] == self.gameInstance.GAME_CODE:
                    if sessionData['data-type'] == 'letter-guess':
                        self.gameInstance.guess(sessionData['letter'])
                    elif sessionData['data-type'] == 'game-lives':
                        self.gameInstance.GAME_LIVES = int(sessionData['lives'])
                        self.gameInstance.Lives.config(text=f'{sessionData["lives"]} Lives remaining')
                        if self.gameInstance.GAME_LIVES == 0:
                            self.gameInstance.state(2)
                    elif sessionData['data-type'] == 'game-word':
                        self.gameInstance.GAME_WORD = sessionData['word']
                        self.gameInstance.handle()
                    elif sessionData['data-type'] == 'word-guess':
                        if sessionData['word'].upper() == self.gameInstance.GAME_WORD.upper():
                            self.gameInstance.state(2)
                    elif sessionData['data-type'] == 'missing-word':
                        self.gameInstance.MISSING_WORD = sessionData['word']
                        self.gameInstance.handle()
                    elif sessionData['data-type'] == 'lives-request':
                        if self.gameInstance.Mode == 'Host':
                            self.gameInstance.draw()
                    elif sessionData['data-type'] == 'refresh':
                        if self.gameInstance.Mode == 'Host':
                            self.gameInstance.refresh()
                    elif sessionData['data-type'] == 'refresh-game':
                        if self.gameInstance.Mode == 'Join':
                            self.gameInstance.restart()

        Logger.log('Connection error - no longer listening.', 'ERROR')

