import random
import time
from tkinter import *
from string import ascii_uppercase
from tools.Colours import Colours
from tools.Network import NetworkM
Colour = Colours()

# TODO: Server-side word and guess handling
# TODO: Guessing punishments - done
# TODO: Hints under word layout - done
# TODO: Chat system using new data format - done


class Hangman:
    def __init__(self):

        self._VERSION = 1.01
        self.GAME_CODE = ''
        self.GAME_WORD = ''
        self.GAME_LIVES = 10
        self.MISSING_WORD = ''
        self.BACKGROUND = '#141414'

        self.Window = Tk()
        self.Window.geometry('800x300')
        self.Window.config(bg=self.BACKGROUND)
        self.Window.title(f'Hangman - Version {self._VERSION}')

        self.Frame = Frame(self.Window, bg=self.BACKGROUND)

        self.Title = Label(self.Window, text='Hangman', font=('MS PGothic', 20, 'bold'), bg=self.BACKGROUND, fg='WHITE').place(relx=.05, rely=.1)
        self.Missing = Label(self.Window, text='H _ N G M _ N', width=40, height=1, font=('Tahoma', 25, 'bold'), bg=self.BACKGROUND, fg='WHITE', anchor='w')
        self.State = Label(self.Window, text='Waiting for match', font=('MS PGothic', 12, 'bold'), bg=self.BACKGROUND, width=16, fg=Colour.GREY, anchor='e')
        self.Lives = Label(self.Window, text='-- Lives remaining', font=('MS PGothic', 16, 'bold'), bg=self.BACKGROUND, width=16, fg=Colour.GREY, anchor='e')
        self.Subtitle = Label(self.Window, text='Warning', font=('Arial', 10, 'bold '), bg=self.BACKGROUND, width=30, fg=Colour.ORANGE, anchor='w')
        self.Warning = Label(self.Window, text='Submitting an incorrect guess will cost two lives for the whole team.', font=('Arial', 10, ' '), bg=self.BACKGROUND, fg=Colour.LIGHT_GREY)
        self.Host = Button(self.Window, text='Host match', font=('MS PGothic', 12, 'bold'), bg=self.BACKGROUND, fg=Colour.ORANGE, bd=0, command=lambda: self.word())
        self.Join = Button(self.Window, text='Join match', font=('MS PGothic', 12, 'bold'), bg=self.BACKGROUND, fg=Colour.LIGHT_BLUE, bd=0, command=lambda: self.code())
        self.Leave = Button(self.Window, text='Leave match', font=('MS PGothic', 12, 'bold'), bg=self.BACKGROUND, fg=Colour.RED, bd=0, command=lambda: self.leave())
        self.Guess = Button(self.Window, text='Submit guess', font=('MS PGothic', 12, 'bold'), bg=self.BACKGROUND, fg=Colour.DARK_SEA_GREEN, bd=0, command=lambda: self.allow())
        self.Chat = Button(self.Window, text='Toggle chat', font=('MS PGothic', 12, 'bold'), bg=self.BACKGROUND, fg=Colour.PURPLE, bd=0, command=lambda: self.toggle())
        self.Request = Button(self.Window, text='Request lives', font=('MS PGothic', 12, 'bold'), bg=self.BACKGROUND, fg=Colour.YELLOW, bd=0, command=lambda: self.request())
        self.Accept = Button(self.Window, text='Accept request', font=('MS PGothic', 12, 'bold'), bg=self.BACKGROUND, fg=Colour.YELLOW, bd=0, command=lambda: self.accept())
        self.Restart = Button(self.Window, text='Restart match', font=('MS PGothic', 12, 'bold'), bg=self.BACKGROUND, fg=Colour.LIGHT_ORANGE, bd=0, command=lambda: self.rebuild())
        self.Send = Button(self.Frame, text='→', font=('Courier new', 12, 'bold'), bg=self.BACKGROUND, fg='WHITE', bd=0, command=lambda: self.chat())
        self.Code = Entry(self.Window, font=('MS PGothic', 10, 'bold'), width=22, bg=self.BACKGROUND, fg='WHITE', bd=4)
        self.Word = Entry(self.Window, font=('MS PGothic', 10, 'bold'), width=22, bg=self.BACKGROUND, fg='WHITE', bd=4, show='*')
        self.Solved = Entry(self.Window, font=('MS PGothic', 10, 'bold'), width=11, bg=self.BACKGROUND, fg='WHITE', bd=4)
        self.Message = Entry(self.Frame, font=('Courier new', 10, 'bold'), width=30, bg=self.BACKGROUND, fg='WHITE', bd=4)
        self.History = Text(self.Frame, bg=self.BACKGROUND, bd=3, height=6, width=35)

        self.Missing.place(relx=.0495, rely=.25)
        self.Host.place(relx=.05, rely=.85)
        self.Join.place(relx=.20, rely=.85)
        self.State.place(relx=.75, rely=.85)
        self.Lives.place(relx=.615, rely=.27)

        self.History.place(relx=.006, rely=.0)
        self.Message.place(relx=.006, rely=.8)
        self.Send.place(relx=.89, rely=.8)

        self.Message.bind('<Return>', lambda event: self.chat())

        self.Letters = list(ascii_uppercase)
        self.Buttons = []
        self.build()

        self.Session = NetworkM('127.0.0.1', 6666, self)
        self.Session.run()
        self.Mode = ''
        self.Requested = True
        self.Restarting = False
        self.Chatting = False

        self.Window.mainloop()

    def build(self):
        self.Buttons = []
        Position = [0.05, 0.45]
        for Letter in self.Letters:
            Temp = Button(self.Window, text=Letter, font=('MS PGothic', 12, 'bold'), bg=self.BACKGROUND, fg='Yellow', bd=0, command=lambda: self.submit())
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
        self.Restart.place_forget()
        self.Lives.config(text='-- Lives remaining')
        self.Missing.config(text='H _ N G M _ N')
        self.build()

    def warn(self, m, t='Warning'):
        self.Subtitle.place(relx=.05, rely=.66)
        self.Subtitle.config(text=t)
        self.Warning.place(relx=.05, rely=.725)
        self.Warning.config(text=m)

    def clear(self):
        self.Subtitle.place_forget()
        self.Warning.place_forget()

    def solve(self):
        self.Session.send(str({'data-type': 'word-guess', 'word': self.Solved.get(), 'token': self.GAME_CODE}))
        self.Solved.delete(0, END)
        self.Solved.place_forget()
        self.clear()

    def allow(self):
        self.Solved.place(relx=.67, rely=.85)
        self.Solved.bind('<Return>', lambda event: self.solve())
        self.warn('Submitting an incorrect will cost the whole team two lives.', 'Guessing')

    def guess(self, l):
        for Letter in self.Buttons:
            if Letter.cget('text') == l.upper():
                Letter.place_forget()
                break
        self.validate()
        if '_' not in list(self.MISSING_WORD) or self.GAME_LIVES <= 0:
            self.state(2)

    def submit(self):
        print(self.Mode, self.GAME_WORD, self.MISSING_WORD)
        if self.Mode == 'Join':
            x, y = self.Window.winfo_pointerxy()
            widget = self.Window.winfo_containing(x, y)
            data = {'data-type': 'letter-guess', 'letter': widget.cget('text'), 'token': self.GAME_CODE}
            self.guess(widget.cget('text'))
            self.Session.send(str(data))

    def host(self):
        self.clear()
        self.layout()
        self.Chat.place(relx=.21, rely=.85)
        self.Mode = 'Host'
        self.Window.after(1, self.Session.send(str({'data-type': 'game-word', 'word': self.GAME_WORD, 'token': self.GAME_CODE})))
        self.MISSING_WORD = '_' * len(self.GAME_WORD)
        self.Window.after(250, lambda: self.Session.send(str({'data-type': 'missing-word', 'word': self.MISSING_WORD, 'token': self.GAME_CODE})))
        for Letter in self.Buttons:
            Letter.config(state=DISABLED)

    def lobby(self):
        pass

    def join(self):
        self.layout()
        self.Guess.place(relx=.515, rely=.85)
        self.Chat.place(relx=.21, rely=.85)
        self.Request.place(relx=.355, rely=.85)
        self.Mode = 'Join'
        self.Session.send(str({'data-type': 'refresh', 'token': self.GAME_CODE}))

    def restart(self):
        for Letter in self.Buttons:
            Letter.place_forget()
        self.build()
        self.Guess.place(relx=.515, rely=.85)
        self.Chat.place(relx=.21, rely=.85)
        self.Request.place(relx=.355, rely=.85)
        self.Missing.config(text='Waiting for game...')
        self.show('GAME: Host is choosing a new word.' )

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
        if str.isalpha(self.GAME_WORD):
            if not self.Restarting:
                self.GAME_CODE = str(random.randint(1000, 9999))
            self.Word.place_forget()
            self.host()
        else:
            self.warn('The word you entered is invalid (must contains letters only)', 'Word')

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

    def toggle(self):
        self.Chatting = not self.Chatting
        if self.Chatting:
            self.Frame.place(relx=.59, rely=.4, width=290, height=130)
        else:
            self.Frame.place_forget()

    def chat(self):
        if len(self.Message.get()) < 20:
            self.Session.send(str({'data-type': 'game-chat', 'chat': self.Message.get(), 'token': self.GAME_CODE}))
        self.Message.delete(0, END)

    def show(self, m, importance=0):
        if importance == 0:
            self.History.tag_config("message", foreground='Yellow', underline=0)
            self.History.insert(INSERT , '\n' + m, "message")
        else:
            self.History.tag_config("notification", foreground='Yellow', underline=1)
            self.History.insert(INSERT, '\n' + m, "notification")
        self.History.see(END)

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

    def validate(self):
        if '_' not in list(self.MISSING_WORD) or self.GAME_LIVES <= 0:
            self.state(2)


if __name__ == '__main__':
    Game = Hangman()
