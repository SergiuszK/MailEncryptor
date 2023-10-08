from Canvas import *
import os
from math import *
from Functions import *
from SendFileWindow import SendFileWindow
from Database import *
from Account import *
from TopWindow import *

class Friend:
    def __init__(self, nameFriend, canvas, counter, root, account):
        database = Database()
        self.width = screensize[0]
        self.height = screensize[1]
        self.nameFriend = nameFriend
        self.root = root
        self.canvas = canvas
        self.counter = counter
        self.account = account
        scale = 1 / max(self.width/self.canvas.width,
                        self.height/self.canvas.height)
        if(scale < (1/2)):
            scale = 1/2
        self.idText = canvas.create_text(
            self.canvas.width/8, self.canvas.height/7 + 60*self.counter, anchor='center', fill='#FCFBF4', font=("Adobe Caslon Pro", int(20*scale)), text=nameFriend, justify=LEFT)
        self.idDateText = canvas.create_text(
            self.canvas.width/3, self.canvas.height/7 + 60*self.counter, anchor='center', fill='#FCFBF4', font=("Adobe Caslon Pro", int(20*scale)), text=str(datetime.datetime.strptime(
                database.getValidityDate(account.username, nameFriend), '%Y-%m-%d %H:%M:%S')) +" (UTC)", justify=LEFT)
        self.sendButton = Button(root, text='Wyślij wiadomość', font=("Adobe Caslon Pro", int(
            20*scale)), command=self.sendFile, bg='#FCFBF4', fg='#18191A', borderwidth=5)
        self.idButton = canvas.create_window(canvas.width/1.7, self.canvas.height/7 + 60*self.counter,
                                             anchor='center',
                                             window=self.sendButton)
        self.sendButton.bind("<Configure>", self.onResize)
        self.setSize()

    def sendFile(self):
        self.sendFile = SendFileWindow(self.account, self.nameFriend)

    def setSize(self):
        scale = 1 / max(self.width/self.canvas.width,
                        self.height/self.canvas.height)
        if(scale < (1/2)):
            scale = 1/2

        width = self.canvas.width/16

        self.canvas.itemconfigure(self.idText, font=(
            "Adobe Caslon Pro", int(20*scale)), justify=LEFT, anchor='center')
        self.canvas.moveto(self.idText, int(width),
                           int(self.canvas.height/5 + 50*self.counter))

        self.canvas.itemconfigure(self.idDateText, font=(
            "Adobe Caslon Pro", int(20*scale)), justify=LEFT, anchor='center')
        self.canvas.moveto(self.idDateText, int(width * 5.5),
                           int(self.canvas.height/5 + 50*self.counter))

        self.sendButton.config(font=("Adobe Caslon Pro", int(20*scale)))
        self.canvas.moveto(self.idButton, int(width*11), int(self.canvas.height/5 + 50 * self.counter - self.sendButton.winfo_height()/4))

    def onResize(self, event):
        self.setSize()


class FriendsListWindow(TopWindow):

    def __init__(self, account):
        TopWindow.__init__(self,True)
        self.counter = 2
        self.account = account
        self.refreshButton = None
        self.noneFriendsText = None
        self.root.title("Friends list")
        self.create()

    def createTextNoneFriends(self):
        self.noneFriendsText = self.canvas.create_text(
            self.canvas.width/6, int(self.canvas.height/25), anchor='center', fill='#FCFBF4', font=("Adobe Caslon Pro", 15), text='Nie masz żadnych znajomych')

    def createRefreshButton(self):
        self.refreshButton = Button(self.root, text='Odśwież', font=("Adobe Caslon Pro", int(
            self.canvas.width/100)), command=self.refresh, bg='#FCFBF4', fg='#18191A', borderwidth=5)
        self.refreshButtonId = self.canvas.create_window(int(self.canvas.width/1.05), int(self.canvas.height/23),
                                                         anchor='nw',
                                                         window=self.refreshButton)

    def createText(self):
        self.mailText = self.canvas.create_text(self.canvas.width/8, self.canvas.height/7,
                                                anchor='center', fill='#FCFBF4', font=("Adobe Caslon Pro", 15), text="Mail odbiorcy", justify=LEFT)
        self.dataText = self.canvas.create_text(self.canvas.width/3, self.canvas.height/7,
                                                anchor='center', fill='#FCFBF4', font=("Adobe Caslon Pro", 15), text="Data ważności", justify=LEFT)

    def clear(self):
        if(self.noneFriendsText != None):
            self.canvas.delete(self.noneFriendsText)
            self.canvas.delete(self.refreshButtonId)
        else:
            self.canvas.delete(self.refreshButtonId)
            self.canvas.delete(self.mailText)
            for friend in self.listOfFriends:
                self.canvas.delete(friend.idText)
                self.canvas.delete(friend.idDateText)
                self.canvas.delete(friend.idButton)
        self.counter = 2

    def create(self):
        if(self.refreshButton != None):
            self.clear()
        self.root.title("Mail Enryption")
        self.writeFriends()
        self.canvas.addtag_all("all")
        self.refreshButton.bind("<Configure>", self.onResize)
        self.setSize()
        for friend in self.listOfFriends:
            friend.setSize()

    def writeFriends(self):
        database = Database()
        path = "./"+self.account.userFolder+"/friends"
        friends = os.listdir(path)
        self.listOfFriends = []
        minimumOne = False
        self.counter = 2
        for friend in friends:
            if(database.checkIfKeySenderIsAvailable(self.account.username, friend)):
                self.listOfFriends.append(
                    Friend(friend, self.canvas, self.counter, self.root, self.account))
                self.counter += 1.5
                minimumOne = True
        if(minimumOne == False):
            self.empty = True
            self.createTextNoneFriends()
            self.createRefreshButton()
        else:
            self.empty = False
            self.createText()
            self.createRefreshButton()

    def reCreate(self):
        while(self.account.isDownloaded == False):
            continue
        self.create()

    def refresh(self):
        if(self.account.isDownloaded):
            self.refreshButton["state"] = DISABLED
            downloadFilesAndKeys = threading.Thread(
                target=self.account.receiveKeys)
            downloadFilesAndKeys.setDaemon(True)
            downloadFilesAndKeys.start()
            reCreateThreadAfterDownload = threading.Thread(
                target=self.reCreate)
            reCreateThreadAfterDownload.setDaemon(True)
            reCreateThreadAfterDownload.start()

    def setSize(self):
        scale = 1 / max(self.width/self.canvas.width,
                        self.height/self.canvas.height)
        if(scale < (1/2)):
            scale = 1/2

        width = self.canvas.width/16

        if(self.empty == True):
            self.canvas.itemconfigure(self.noneFriendsText, font=(
                "Adobe Caslon Pro", int(30*scale)))
            self.canvas.moveto(
                self.noneFriendsText, int(width*2), int(self.canvas.height/7))
        else:
            self.canvas.itemconfigure(self.mailText, font=(
                "Adobe Caslon Pro", int(30*scale)), justify=LEFT, anchor='center')
            self.canvas.moveto(
                self.mailText, int(width), int(self.canvas.height/7))
            self.canvas.itemconfigure(self.dataText, font=(
                "Adobe Caslon Pro", int(30*scale)), justify=LEFT, anchor='center')
            self.canvas.moveto(
                self.dataText, int(width*5.5), int(self.canvas.height/7))

        self.refreshButton.config(
            font=("Adobe Caslon Pro", int(20*scale)), justify=LEFT)
        self.canvas.moveto(self.refreshButtonId,
                           int(width*14), int(self.canvas.height/15))

    def onResize(self, event):
        self.setSize()
