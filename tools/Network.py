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
        # self.gameSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
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
                receivedData = self.gameSocket.recv(150).decode()
            except:
                receivedData = None
            if receivedData:
                print(receivedData)
                try:
                    sessionData = literal_eval(receivedData)
                except Exception:
                    continue
                if sessionData['token'] == self.gameInstance.GAME_CODE:
                    if sessionData['data-type'] == 'game-update':
                        self.gameInstance.MISSING_WORD = sessionData['missing']
                        self.gameInstance.GAME_LIVES = sessionData['lives']
                        self.gameInstance.update()
                    elif sessionData['data-type'] == 'lives-request':
                        if self.gameInstance.Mode == 'Host':
                            self.gameInstance.draw()
                    elif sessionData['data-type'] == 'refresh-game':
                        if self.gameInstance.Mode == 'Join':
                            self.gameInstance.restart()
                    elif sessionData['data-type'] == 'game-chat':
                        self.gameInstance.show('CHAT: ' +  sessionData['chat'])
                    elif sessionData['data-type'] == 'game-notification':
                        self.gameInstance.show('GAME: ' +  sessionData['chat'])
                    elif sessionData['data-type'] == 'game-priority':
                        self.gameInstance.show('GAME: ' + sessionData['chat'], 1)
                    elif sessionData['data-type'] == 'over':
                        self.gameInstance.GAME_WORD = sessionData['word']
                        self.gameInstance.state(2)
                    elif sessionData['data-type'] == 'lobby-data':
                        if self.gameInstance.Asked:
                            self.gameInstance.list(sessionData)

        Logger.log('Connection error - no longer listening.', 'ERROR')


