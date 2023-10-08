from Canvas import *
from PIL import ImageTk
import os
from math import *
from Account import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from Crypto.Random import get_random_bytes
from base64 import b64decode
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES
from Functions import *
from tkinter.messagebox import _show
from TopWindow import *

class File:
    def __init__(self, nameFile, canvas, counter, root, sender, path, account, create):
        self.reCreateThread = threading.Thread(target=create)
        self.reCreateThread.setDaemon(True)
        self.nameFile = nameFile
        self.root = root
        self.canvas = canvas
        self.counter = counter
        self.sender = sender
        self.width = screensize[0]
        self.height = screensize[1]
        self.path = path
        self.account = account
        self.idSenderText = canvas.create_text(self.canvas.width/11, self.canvas.height/7 + 60*self.counter, anchor='center',
                                               fill='#FCFBF4', font=("Adobe Caslon Pro", int(self.canvas.width/150)), text=sender[0:60], justify=LEFT)
        self.idFileText = canvas.create_text(self.canvas.width/4, self.canvas.height/7 + 60*self.counter, anchor='center',
                                             fill='#FCFBF4', font=("Adobe Caslon Pro", int(self.canvas.width/150)), text=nameFile[0:60], justify=LEFT)
        self.openButton = Button(root, text='Otwórz', font=(
            "Adobe Caslon Pro", 10), command=self.openFile, bg='#FCFBF4', fg='#18191A', borderwidth=5)
        self.idOpenButton = canvas.create_window(canvas.width/1.4, canvas.height/7 + screensize[0]/16*self.counter,
                                                 anchor='center',
                                                 window=self.openButton)
        self.decodeButton = Button(root, text='Odzyfruj', font=(
            "Adobe Caslon Pro", 10), command=self.decodeFile, bg='#FCFBF4', fg='#18191A', borderwidth=5)
        self.idDecodeButton = canvas.create_window(canvas.width/1.25, canvas.height/7 + screensize[0]/16*self.counter,
                                                   anchor='center',
                                                   window=self.decodeButton)
        if "(odszyfrowane)" in nameFile:
            self.decodeButton["state"] = DISABLED
            self.decrypted = True
        else:
            self.decrypted = False
        self.deleteButton = Button(root, text='Usuń', font=(
            "Adobe Caslon Pro", 10), command=self.deleteFile, bg='#FCFBF4', fg='#18191A', borderwidth=5)
        self.idDeleteButton = canvas.create_window(canvas.width/1.1, canvas.height/7 + screensize[0]/16*self.counter,
                                                   anchor='center',
                                                   window=self.deleteButton)
        self.decodeButton.bind("<Configure>", self.onResize)

    def openFile(self):
        temp = os.path.abspath(self.path + "/" + self.nameFile)
        os.startfile(temp)

    def deleteFile(self):
        self.canvas.delete(self.idSenderText)
        self.canvas.delete(self.idFileText)
        temp = os.path.abspath(self.path + "/" + self.nameFile)
        os.remove(temp)
        split = self.nameFile.split(".")
        if(self.decrypted == False):
            temp = os.path.abspath(self.path + "/" + split[0]+"_Key.txt")
            os.remove(temp)
        self.reCreateThread.start()

    def loadRsaPrivateKey(self):
        file_private_key = open(
            str(self.account.userFolder)+"/keys/private_key.pem", 'rb')
        return RSA.importKey(file_private_key.read())

    def loadEncryptedKeyAes(self):
        files = os.listdir(self.path)
        key = None
        for file in files:
            if self.nameFile.split(".")[0] + "_Key" in file:
                key = file
        return open(self.path+"/"+key, "rb")

    def decodeFile(self):
        RsaPrivateKey = self.loadRsaPrivateKey()
        cipher = Cipher_PKCS1_v1_5.new(RsaPrivateKey)
        sentinel = get_random_bytes(32)
        decryptedKeyAes = cipher.decrypt(
            self.loadEncryptedKeyAes().read(), sentinel, expected_pt_len=32)

        with open(self.path + "/" + self.nameFile, "rb") as entry:
            try:
                data = entry.read()
                iv = data[:24]
                iv = b64decode(iv)
                ciphertext = data[24:]
                cipher = AES.new(decryptedKeyAes, AES.MODE_CBC, iv)
                decrypted = cipher.decrypt(ciphertext)
                decrypted = unpad(decrypted, AES.key_size[2])
                with open(self.path + "/(odszyfrowane)"+self.nameFile, 'wb') as data:
                    data.write(decrypted)
                data.close()
                self.decodeButton["state"] = DISABLED
            except(ValueError, KeyError):
                self.root.after(10, lambda: _show(
                    'Powiadomienie', 'Nieprawidłowy klucz, usunięto plik'))
        self.deleteFile()

    def onResize(self, event):
        self.setSize()

    def setSize(self):
        scale = 1 / max(self.width/self.canvas.width,
                        self.height/self.canvas.height)
        if(scale < (1/2)):
            scale = 1/2

        width = self.canvas.width/16

        self.canvas.itemconfigure(self.idSenderText, font=(
            "Adobe Caslon Pro", int(20*scale)), justify=LEFT, anchor='center')
        self.canvas.moveto(self.idSenderText, int(width), int(self.canvas.height/7 + 60*self.counter))
        self.canvas.itemconfigure(self.idFileText, font=(
            "Adobe Caslon Pro", int(20*scale)), justify=LEFT, anchor='center')
        self.canvas.moveto(self.idFileText, int(width*5.5),
                           int(self.canvas.height/7 + 60*self.counter))

        self.openButton.config(
            font=("Adobe Caslon Pro", int(20*scale)), justify=LEFT)
        self.canvas.moveto(self.idOpenButton, int(width*11), int(self.canvas.height/7.5 + 60 * self.counter  - self.openButton.winfo_height()/4))

        self.decodeButton.config(
            font=("Adobe Caslon Pro", int(20*scale)), justify=LEFT)
        self.canvas.moveto(self.idDecodeButton, int(width*12.5), int(self.canvas.height/7.5 + 60 * self.counter  - self.decodeButton.winfo_height()/4))

        self.deleteButton.config(
            font=("Adobe Caslon Pro", int(20*scale)), justify=LEFT)
        self.canvas.moveto(self.idDeleteButton, int(width*14), int(self.canvas.height/7.5 + 60 * self.counter  - self.deleteButton.winfo_height()/4))


class MailBoxWindow(TopWindow):
    def __init__(self, account):
        TopWindow.__init__(self,True)
        self.listOfFiles = []
        self.counter = 2
        self.account = account
        self.refreshButton = None
        self.noneMessagesText = None
        self.empty = False
        self.root.title("Mail Box")
        self.create()
        self.refreshButton.bind("<Configure>", self.onResize)

    def clear(self):
        if(self.noneMessagesText != None):
            self.canvas.delete(self.noneMessagesText)
            self.canvas.delete(self.refreshButtonId)
        else:
            self.canvas.delete(self.refreshButtonId)
            self.canvas.delete(self.senderText)
            self.canvas.delete(self.fileText)
            for file in self.listOfFiles:
                self.canvas.delete(file.idSenderText)
                self.canvas.delete(file.idFileText)
                self.canvas.delete(file.idOpenButton)
                self.canvas.delete(file.idDecodeButton)
                self.canvas.delete(file.idDeleteButton)
        self.counter = 2

    def create(self):
        if(self.refreshButton != None):
            self.clear()
        self.listOfFiles = []
        self.showFiles()
        self.canvas.addtag_all("all")
        self.setSize()
        for file in self.listOfFiles:
            file.setSize()

    def createRefreshButton(self):
        self.refreshButton = Button(self.root, text='Odśwież', font=("Adobe Caslon Pro", int(
            self.canvas.width/100)), command=self.refresh, bg='#FCFBF4', fg='#18191A', borderwidth=5)
        self.refreshButtonId = self.canvas.create_window(int(self.canvas.width/1.05), int(self.canvas.height/23),
                                                         anchor='nw',
                                                         window=self.refreshButton)

    def createTexts(self):
        self.senderText = self.canvas.create_text(self.canvas.width/11, self.canvas.height/7,
                                                  anchor='center', fill='#FCFBF4', font=("Adobe Caslon Pro", 15), text="Nadawca", justify=LEFT)
        self.fileText = self.canvas.create_text(self.canvas.width/2, self.canvas.height/7, anchor='center',
                                                fill='#FCFBF4', font=("Adobe Caslon Pro", 15), text="Nazwa pliku", justify=LEFT)

    def createTextNoneMessages(self):
        self.noneMessagesText = self.canvas.create_text(
            self.canvas.width/7, int(self.canvas.height/25), anchor='center', fill='#FCFBF4', font=("Adobe Caslon Pro", 15), text='Nie masz żadnych wiadomości')

    def writeMessages(self, sender):

        path = "./"+self.account.userFolder+"/received files/"+sender
        files = os.listdir(path)

        for file in files:
            if "_Key" in file:
                files.remove(file)

        for file in files:
            self.listOfFiles.append(File(
                file, self.canvas, self.counter, self.root, sender, path, self.account, self.create))
            self.counter += 1

    def showFiles(self):
        path = "./" + self.account.userFolder + "/received files"
        dir = os.listdir(path)
        self.createRefreshButton()
        if len(dir) == 0:
            self.empty = True
            self.createTextNoneMessages()
        else:
            self.empty = True
            for sender in dir:
                if(len(os.listdir(path + "/" + sender)) != 0):
                    self.empty = False
            if(self.empty == False):
                self.createTexts()
                for sender in dir:
                    self.writeMessages(sender)
            else:
                self.createTextNoneMessages()


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

    def onResize(self, event):
        self.setSize()

    def setSize(self):
        scale = 1 / max(self.width/self.canvas.width,
                        self.height/self.canvas.height)
        if(scale < (1/2)):
            scale = 1/2


        width = self.canvas.width/16
        
        if(self.empty == True):
            self.canvas.itemconfigure(self.noneMessagesText, font=(
                "Adobe Caslon Pro", int(30*scale)), justify=LEFT)
            self.canvas.moveto(self.noneMessagesText,
                               int(width*2), int(self.canvas.height/7))
        else:
            self.canvas.itemconfigure(self.senderText, font=(
                "Adobe Caslon Pro", int(30*scale)), justify=LEFT, anchor='center')
            self.canvas.moveto(
                self.senderText, int(width), int(self.canvas.height/7))
            self.canvas.itemconfigure(self.fileText, font=(
                "Adobe Caslon Pro", int(30*scale)), justify=LEFT, anchor='center')
            self.canvas.moveto(
                self.fileText, int(width*5.5), int(self.canvas.height/7))
        self.refreshButton.config(
            font=("Adobe Caslon Pro", int(20*scale)), justify=LEFT)
        self.canvas.moveto(self.refreshButtonId,
                           int(width*14), int(self.canvas.height/15))