from Account import *
from GenerateKeyWindow import *
from FriendsListWindow import *
from ShareKeyWindow import *
from MailBoxWindow import *
from tkinter.messagebox import _show
from MainWindow import *

class LoggedWindow(MainWindow):
    root = None
    frame = None
    canvas = None
    account = None
    validityKey = True

    def __init__(self, account):
        MainWindow.__init__(self)
        self.account = account
        self.friendsList = None
        self.mailBox = None
        self.shareKeyWindow = None
        self.generateKeyWindow = None
        self.createWindow()

    def createWindow(self):
        self.generateKeyWindow = GenerateKeyWindow(
            self.account, False, self.root)
        self.logouted = False
        self.root.title("Mail Encryption")
        self.createButtonToGenerateKeys()
        self.createUserNameText()
        self.createButtonShowFriendsList()
        self.createLogoutButton()
        self.createButtonToShareKeys()
        self.createButtonToMailBox()
        self.createTextArea()
        self.canvas.addtag_all("all")
        self.account.downloadFilesAndKeys.start()

    def onClosing(self):
        if(self.account.isDownloaded == True):
            if messagebox.askokcancel("Wyjście", "Czy chcesz zamknąć aplikację?"):
                self.root.destroy()
                sys.exit(0)
        else:
            self.root.after(10, lambda: _show('Powiadomienie',
                            'Trwa pobieranie plików, spróbuj za chwilę'))

    def destroy(self):
        self.root.quit()
        self.account.logout()
        self.canvas.delete()
        self.root.destroy()
        if(self.friendsList != None and self.friendsList.root.state == "normal"):
            self.friendsList.canvas.delete()
            self.friendsList.root.destroy()
        if(self.mailBox != None and self.mailBox.root.state == "normal"):
            self.mailBox.canvas.delete()
            self.mailBox.root.destroy()
        if(self.shareKeyWindow != None and self.shareKeyWindow.root.state == "normal"):
            self.shareKeyWindow.canvas.delete()
            self.shareKeyWindow.root.destroy()

    def logout(self):
        if(self.account.isDownloaded == True):
            self.logouted = True
            self.root.quit()
        else:
            self.root.after(10, lambda: _show('Powiadomienie',
                            'Trwa pobieranie plików, spróbuj za chwilę'))

    def showFriendsList(self):
        self.friendsList = FriendsListWindow(self.account)

    def showMailBox(self):
        self.mailBox = MailBoxWindow(self.account)

    def shareKey(self):
        self.shareKeyWindow = ShareKeyWindow(self.account)

    def generateKey(self):
        self.generateKeyWindow = GenerateKeyWindow(
            self.account, True, self.root)

    def createUserNameText(self):
        self.userNameText = self.canvas.create_text(int(self.canvas.width/25), int(
            self.canvas.height/18), anchor='center', fill='#FCFBF4', font=("Adobe Caslon Pro", 15), text=self.account.username)

    def createButtonToGenerateKeys(self):
        self.generateButton = Button(self.root, text=' Generowanie kluczy ', font=(
            "Adobe Caslon Pro", 10), command=self.generateKey, bg='#FCFBF4', fg='#18191A', borderwidth=5)
        self.generateButtonId = self.canvas.create_window(self.canvas.width/16*5-self.generateButton.winfo_width(), self.canvas.height/4,
                                                          anchor='center',
                                                          window=self.generateButton)

    def createButtonToShareKeys(self):
        self.shareButton = Button(self.root, text='Udostępnianie klucza', font=(
            "Adobe Caslon Pro", 10), command=self.shareKey, bg='#FCFBF4', fg='#18191A', borderwidth=5)
        self.shareButtonId = self.canvas.create_window(self.canvas.width/5-30, 130,
                                                       anchor='center',
                                                       window=self.shareButton)

    def createButtonShowFriendsList(self):
        self.friendsListButton = Button(self.root, text='    Lista znajomych   ', font=(
            "Adobe Caslon Pro", 10), command=self.showFriendsList, bg='#FCFBF4', fg='#18191A', borderwidth=5)
        self.friendsListButtonId = self.canvas.create_window(self.canvas.width/1.3444, 50,
                                                             anchor='center',
                                                             window=self.friendsListButton)

    def createLogoutButton(self):
        self.logoutButton = Button(self.root, text='Wyloguj', font=(
            "Adobe Caslon Pro", 10), command=self.logout, bg='#FCFBF4', fg='#18191A', borderwidth=5)
        self.logoutButtonId = self.canvas.create_window(int(self.canvas.width/1.05), int(self.canvas.height/25),
                                                        anchor='center',
                                                        window=self.logoutButton)

    def createButtonToMailBox(self):
        self.mailBoxButton = Button(self.root, text=' Skrzynka odbiorcza ', font=(
            "Adobe Caslon Pro", 10), command=self.showMailBox, bg='#FCFBF4', fg='#18191A', borderwidth=5)
        self.mailBoxButtonId = self.canvas.create_window(self.canvas.width/1.3444, 80,
                                                         anchor='center',
                                                         window=self.mailBoxButton)
        self.mailBoxButton.bind("<Configure>", self.onResize)

    def createTextArea(self):
        self.output = Text(self.root, width=int(
            self.canvas.width/22), height=int(self.canvas.height/54),  bg='black', foreground="green", font=("Adobe Caslon Pro", int(20)), borderwidth=10)
        self.outputId = self.canvas.create_window(self.canvas.width/2, int(self.canvas.height/1.4),
                                                  anchor='center',
                                                  window=self.output)
        self.output.config(state=DISABLED)
        self.updateInfo()

    def updateInfo(self):
        database = Database()

        self.output.configure(state='normal')
        self.output.delete(1.0, END)
        self.output.insert('end', '\n')
        self.output.insert('end', '     Zalogowany użytkownik: ' +
                           database.getValue(self.account.username, "USER", 'mail') + '\n')
        ifGenerate, validityDate, difference = self.account.validateKey()
        if(ifGenerate == False):
            self.validityKey = True
            self.output.insert('end', '     Data wygaśnięcia ważności klucza: ' + validityDate.strftime(
                '%Y-%m-%d %H:%M:%S')+'(UTC). Pozostało: ' + str(difference) + ' minut.' + '\n''\n')
        else:
            if(self.validityKey == True):
                self.generateKeyWindow = GenerateKeyWindow(
                    self.account, False, self.root)
                self.generateKeyWindow.generateKeyThread.start()
            self.output.insert('end', '     Data wygaśnięcia ważności klucza: ' +
                               'Klucze nieważne, trwa generownie nowej pary' '\n''\n')
            self.validityKey = False

        self.output.insert(
            'end', '     Lista adresów, pod które będą automatycznie wysyłane nowe wersje klucza: ' '\n')

        listOfReceivers = database.getReceivers(self.account.username)
        if(listOfReceivers):
            for receiver in listOfReceivers:
                self.output.insert('end', '     '+"".join(receiver)+'\n')
        else:
            self.output.insert('end', '     Brak zapisanych adresów ' '\n')
        self.output.configure(state='disabled')
        self.root.after(1000, self.updateInfo)

    def onResize(self, event):
        scale = 1 / max(self.width/self.canvas.width,
                        self.height/self.canvas.height)

        if(scale < (1/2)):
            scale = 1/2

        height = self.canvas.height/8
        width = self.canvas.width/16

        self.output.config(width=int(
            self.canvas.width/22), height=int(self.canvas.height/54), font=("Adobe Caslon Pro", int(15*scale)))
        self.friendsListButton.config(font=("Adobe Caslon Pro", int(20*scale)))
        self.shareButton.config(font=("Adobe Caslon Pro", int(20*scale)))
        self.generateButton.config(font=("Adobe Caslon Pro", int(20*scale)))
        self.mailBoxButton.config(font=("Adobe Caslon Pro", int(20*scale)))
        self.logoutButton.config(font=("Adobe Caslon Pro", int(20*scale)))

        self.canvas.moveto(self.generateButtonId,
                           int(width*5-self.shareButton.winfo_width()), int(height*2))
        self.canvas.moveto(self.shareButtonId,
                           int(width*5-self.shareButton.winfo_width()), int(height*3))

        self.canvas.moveto(self.friendsListButtonId,
                           int(width*11), int(height*2))
        self.canvas.moveto(self.mailBoxButtonId,
                           int(width*11), int(height*3))

        self.canvas.moveto(self.logoutButtonId, int(
            width*13.5), int(self.canvas.height/25))

        self.canvas.moveto(self.userNameText, int(
            self.canvas.width/25), int(self.canvas.height/18))

        self.canvas.itemconfigure(self.userNameText, font=(
            "Adobe Caslon Pro", int(15*scale)))