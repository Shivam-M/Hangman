import random
import time
from tkinter import *
from string import ascii_uppercase
from tools.Colours import Colours
from tools.Network import NetworkM
Colour = Colours()


class Hangman:
    def __init__(self):

        self._VERSION = 0.99
        self.GAME_CODE = ''
        self.GAME_WORD = ''
        self.GAME_LIVES = 10
        self.MISSING_WORD = ''

        self.Window = Tk()
        self.Window.geometry('800x300')
        self.Window.config(bg='#141414')
        self.Window.title(f'Hangman - Version {self._VERSION}')

        self.Title = Label(self.Window, text='Hangman', font=('MS PGothic', 20, 'bold'), bg='#141414', fg='WHITE').place(relx=.05, rely=.1)
        self.Missing = Label(self.Window, text='H _ N G M _ N', width=40, height=1, font=('Tahoma', 25, 'bold'), bg='#141414', fg='WHITE', anchor='w')
        self.State = Label(self.Window, text='Waiting for match', font=('MS PGothic', 12, 'bold'), bg='#141414', width=16, fg=Colour.GREY, anchor='e')
        self.Lives = Label(self.Window, text='-- Lives remaining', font=('MS PGothic', 16, 'bold'), bg='#141414', width=16, fg=Colour.GREY, anchor='e')
        self.Host = Button(self.Window, text='Host match', font=('MS PGothic', 12, 'bold'), bg='#141414', fg=Colour.ORANGE, bd=0, command=lambda: self.word())
        self.Join = Button(self.Window, text='Join match', font=('MS PGothic', 12, 'bold'), bg='#141414', fg=Colour.LIGHT_BLUE, bd=0, command=lambda: self.code())
        self.Leave = Button(self.Window, text='Leave match', font=('MS PGothic', 12, 'bold'), bg='#141414', fg=Colour.RED, bd=0, command=lambda: self.leave())
        self.Guess = Button(self.Window, text='Submit guess', font=('MS PGothic', 12, 'bold'), bg='#141414', fg=Colour.DARK_SEA_GREEN, bd=0, command=lambda: self.allow())
        self.Chat = Button(self.Window, text='Toggle chat', font=('MS PGothic', 12, 'bold'), bg='#141414', fg=Colour.PURPLE, bd=0)
        self.Request = Button(self.Window, text='Request lives', font=('MS PGothic', 12, 'bold'), bg='#141414', fg=Colour.YELLOW, bd=0, command=lambda: self.request())
        self.Accept = Button(self.Window, text='Accept request', font=('MS PGothic', 12, 'bold'), bg='#141414', fg=Colour.YELLOW, bd=0, command=lambda: self.accept())
        self.Restart = Button(self.Window, text='Restart match', font=('MS PGothic', 12, 'bold'), bg='#141414', fg=Colour.LIGHT_ORANGE, bd=0, command=lambda: self.rebuild())
        self.Code = Entry(self.Window, font=('MS PGothic', 10, 'bold'), width=22, bg='#141414', fg='WHITE', bd=4)
        self.Word = Entry(self.Window, font=('MS PGothic', 10, 'bold'), width=22, bg='#141414', fg='WHITE', bd=4, show='*')
        self.Solved = Entry(self.Window, font=('MS PGothic', 10, 'bold'), width=11, bg='#141414', fg='WHITE', bd=4)

        self.Missing.place(relx=.0495, rely=.25)
        self.Host.place(relx=.05, rely=.85)
        self.Join.place(relx=.20, rely=.85)
        self.State.place(relx=.75, rely=.85)
        self.Lives.place(relx=.615, rely=.27)

        self.Letters = list(ascii_uppercase)
        self.Buttons = []
        self.build()

        self.Session = NetworkM('127.0.0.1', 6666, self)
        self.Session.run()
        self.Mode = ''
        self.Requested = True
        self.Restarting = False

        self.Window.mainloop()

    def build(self):
        self.Buttons = []
        Position = [0.05, 0.45]
        for Letter in self.Letters:
            Temp = Button(self.Window, text=Letter, font=('MS PGothic', 12, 'bold'), bg='#141414', fg=Colour.RED, bd=0, command=lambda: self.submit())
            Temp.place(relx=Position[0], rely=Position[1])
            self.Buttons.append(Temp)
            Position[0] += 0.042
            if Letter == 'M':
                Position[0] = 0.05
                Position[1] = 0.55
            elif Letter == 'Y':
                Position[0] += 0.003

    def leave(self):
        for Letter in self.Buttons:
            Letter.place_forget()
        self.GAME_WORD = ''
        self.MISSING_WORD = ''
        self.GAME_CODE = ''
        self.state(0)
        self.Host.place(relx=.05, rely=.85)
        self.Join.place(relx=.20, rely=.85)
        self.Leave.place_forget()
        self.Guess.place_forget()
        self.Chat.place_forget()
        self.Request.place_forget()
        self.Lives.config(text='-- Lives remaining')
        self.Missing.config(text='H _ N G M _ N')
        self.build()

    def solve(self):
        self.Session.send(str({'data-type': 'word-guess', 'word': self.Solved.get(), 'token': self.GAME_CODE}))

    def allow(self):
        self.Solved.place(relx=.67, rely=.85)
        self.Solved.bind('<Return>', lambda event: self.solve())

    def guess(self, l):
        for Letter in self.Buttons:
            if Letter.cget('text') == l.upper():
                Letter.place_forget()
                break
        if l.upper() not in list(self.GAME_WORD.upper()):
            if self.Mode == 'Host':
                self.GAME_LIVES -= 1
                self.Session.send(str({'data-type': 'game-lives', 'lives': str(self.GAME_LIVES), 'token': self.GAME_CODE}))
        self.validate(l)
        if '_' not in list(self.MISSING_WORD) or self.GAME_LIVES == 0:
            self.state(2)

    def submit(self):
        if self.Mode == 'Join':
            x, y = self.Window.winfo_pointerxy()
            widget = self.Window.winfo_containing(x, y)
            data = {'data-type': 'letter-guess', 'letter': widget.cget('text'), 'token': self.GAME_CODE}
            self.guess(widget.cget('text'))
            self.Session.send(str(data))

    def host(self):
        self.layout()
        self.Chat.place(relx=.21, rely=.85)
        self.Mode = 'Host'
        self.Session.send(str({'data-type': 'game-word', 'word': self.GAME_WORD, 'token': self.GAME_CODE}))
        self.MISSING_WORD = '_' * len(self.GAME_WORD)
        self.Session.send(str({'data-type': 'missing-word', 'word': self.MISSING_WORD, 'token': self.GAME_CODE}))
        for Letter in self.Buttons:
            Letter.config(state=DISABLED)

    def join(self):
        self.layout()
        self.Guess.place(relx=.515, rely=.85)
        self.Chat.place(relx=.21, rely=.85)
        self.Request.place(relx=.355, rely=.85)
        self.Mode = 'Join'
        self.Session.send(str({'data-type': 'refresh', 'token': self.GAME_CODE}))

    def restart(self):
        self.build()
        self.Guess.place(relx=.515, rely=.85)
        self.Chat.place(relx=.21, rely=.85)
        self.Request.place(relx=.355, rely=.85)
        self.Missing.config(text='Waiting for game...')

    def rebuild(self):
        self.Restarting = True
        self.Session.send(str({'data-type': 'refresh-game', 'token': self.GAME_CODE}))
        self.GAME_WORD = ''
        self.GAME_LIVES = 10
        self.MISSING_WORD = ''
        self.state(1)
        self.Host.place(relx=.05, rely=.85)
        self.Join.place(relx=.20, rely=.85)
        self.Leave.place_forget()
        self.Guess.place_forget()
        self.Chat.place_forget()
        self.Request.place_forget()
        self.build()
        self.word()

    def layout(self):
        self.state(1)
        self.Host.place_forget()
        self.Join.place_forget()
        self.Leave.place(relx=.05, rely=.85)

    def code(self):
        self.Code.place(relx=.345, rely=.85)
        self.Code.bind('<Return>', lambda event: self.check())

    def check(self):
        self.GAME_CODE = self.Code.get()
        self.Code.place_forget()
        self.join()

    def word(self):
        self.Word.place(relx=.345, rely=.85)
        self.Word.bind('<Return>', lambda event: self.start())

    def start(self):
        self.GAME_WORD = self.Word.get()
        if not self.Restarting:
            self.GAME_CODE = str(random.randint(1000, 9999))
        self.Word.place_forget()
        self.host()

    def refresh(self):
        self.Lives.config(text='10 Lives remaining')
        time.sleep(0.125)
        self.Session.send(str({'data-type': 'game-lives', 'lives': str(self.GAME_LIVES), 'token': self.GAME_CODE}))
        time.sleep(0.125)
        self.Session.send(str({'data-type': 'missing-word', 'word': self.MISSING_WORD, 'token': self.GAME_CODE}))
        time.sleep(0.125)
        self.Session.send(str({'data-type': 'game-word', 'word': self.GAME_WORD, 'token': self.GAME_CODE}))
        time.sleep(0.125)

    def handle(self):
        self.Missing.config(text=' '.join(list(self.MISSING_WORD)))

    def request(self):
        self.Session.send(str({'data-type': 'lives-request', 'token': self.GAME_CODE}))

    def accept(self):
        self.Accept.place_forget()
        self.GAME_LIVES += 1
        self.Session.send(str({'data-type': 'game-lives', 'lives': str(self.GAME_LIVES), 'token': self.GAME_CODE}))

    def draw(self):
        self.Accept.place(relx=.36, rely=.85)

    def chat(self):
        pass

    def state(self, state):
        if state == 0:
            self.State.config(text='Waiting for game', fg=Colour.GREY)
        elif state == 1:
            self.State.config(text=f'In game #{self.GAME_CODE}', fg=Colour.BLUE)
        elif state == 2:
            self.State.config(text='Game over', fg=Colour.RED)
            self.Missing.config(text=' '.join(list(self.GAME_WORD.upper())))
            for Letter in self.Buttons:
                Letter.config(state=DISABLED)
            if self.Mode == 'Join':
                self.Guess.place_forget()
                self.Request.place_forget()
                self.Solved.place_forget()
            elif self.Mode == 'Host':
                self.Restart.place(relx=.36, rely=.85)

    def validate(self, l):
        for x in range(len(list(self.GAME_WORD))):
            if list(self.GAME_WORD.upper())[x] == l.upper():
                Temp = list(self.MISSING_WORD.upper())
                Temp[x] = l
                self.MISSING_WORD = ''.join(Temp)
                self.handle()


if __name__ == '__main__':
    Game = Hangman()