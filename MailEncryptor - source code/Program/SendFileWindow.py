from Canvas import *
import os
from math import *
from tkinter.filedialog import askopenfilename
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from Crypto.Cipher import AES
from base64 import b64encode
from Functions import *
from Crypto.Util.Padding import pad
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from tkinter.messagebox import _show
import threading
from os.path import exists
import subprocess
from tkinter import ttk
from TopWindow import *

filesToSend = []

class File(TopWindow):
    def __init__(self, name, canvas, counter, root):
        self.width = screensize[0]
        self.height = screensize[1]
        self.name = name
        self.root = root
        self.canvas = canvas
        self.counter = counter
        self.idName = None
        self.create()

    def create(self):
        scale = 1 / max(self.width/self.canvas.width,
                        self.height/self.canvas.height)
        if(scale < (1/2)):
            scale = 1/2
        self.height = self.canvas.height/10
        self.idName = self.canvas.create_text(
            self.canvas.width/1.1, self.height * 7 + 30*self.counter, anchor='center', fill='#FCFBF4', font=("Adobe Caslon Pro", int(10*scale)), text=os.path.basename(self.name)[0:30], justify=LEFT)
        self.deleteButton = Button(self.root, text='Usuń z listy', font=("Adobe Caslon Pro", int(
            10*scale)), command=self.deleteFileFromList, bg='#FCFBF4', fg='#18191A', borderwidth=5)
        self.idButton = self.canvas.create_window(self.canvas.width/1.11, self.height * 7 + 60 * self.counter,
                                                  anchor='center',
                                                  window=self.deleteButton)
        self.deleteButton.bind("<Configure>", self.onResize)
        self.setSize()

    def deleteFileFromList(self):
        self.canvas.delete(self.idName)
        self.canvas.delete(self.idButton)
        filesToSend.remove(self)
        temp = 1
        for file in filesToSend:
            file.counter = temp
            temp += 1
            file.canvas.delete(file.idName)
            file.canvas.delete(file.idButton)
            file.create()

    def setSize(self):
        scale = 1 / max(self.width/self.canvas.width,
                        self.height/self.canvas.height)
        if(scale < (1/2)):
            scale = 1/2

        height = self.canvas.height/10
        self.canvas.itemconfigure(self.idName, font=(
            "Adobe Caslon Pro", int(10*scale)), justify=LEFT, anchor='center')
        self.canvas.moveto(self.idName, int(self.canvas.width /
                           1.3), int(height * 7.5 + 35 * self.counter))
        self.deleteButton.config(font=("Adobe Caslon Pro", int(8*scale)))
        self.canvas.moveto(self.idButton, int(self.canvas.width /
                           1.15), int(height * 7.5 + 35 * self.counter - 5))

    def onResize(self, event):
        self.setSize()


class SendFileWindow(TopWindow):
    fileToGenerate = randomFile()

    def __init__(self, account, nameFriend):
        TopWindow.__init__(self,False)
        self.counter = 1
        self.account = account
        self.nameFriend = nameFriend
        self.root.title("Send File")
        self.createTextArea()
        self.createSendButton()
        self.createAddFileButton()
        self.canvas.addtag_all("all")

    def startThread(self):
        self.progressBar = ttk.Progressbar(
            self.root, orient=HORIZONTAL, length=self.width/3, mode="indeterminate")
        self.progressBarId = self.canvas.create_window(self.canvas.width/2, 50,
                                                       anchor='center',
                                                       window=self.progressBar)
        self.progressBar.start(10)

        self.sendFileThread = threading.Thread(target=self.sendFile)
        self.sendFileThread.setDaemon(True)
        self.sendFileThread.start()

    def createAddFileButton(self):
        self.addFileButton = Button(self.root, text='Dodaj Plik', font=("Adobe Caslon Pro", 10), command=self.addFile,
                                    bg='#FCFBF4', fg='#18191A', borderwidth=5, width=int(self.canvas.width/45), height=int(self.canvas.height/1000))
        self.addFileButtonId = self.canvas.create_window(self.canvas.width/2, int(self.canvas.height/1.1),
                                                         anchor='center',
                                                         window=self.addFileButton)

    def createTextArea(self):
        self.text = self.canvas.create_text(int(self.canvas.width/2), int(self.canvas.height/10),
                                            text='Treść maila:', font=("Adobe Caslon Pro", 15), fill='#FCFBF4', justify='left')
        self.messages = Text(self.root, width=int(
            self.canvas.width/15), height=int(self.canvas.height/25))
        self.messagesId = self.canvas.create_window(self.canvas.width/2, int(self.canvas.height/2),
                                                    anchor='center',
                                                    window=self.messages)

    def createSendButton(self):
        self.sendButton = Button(self.root, text='Wyślij', font=("Adobe Caslon Pro", 10), command=self.startThread,
                                 bg='#FCFBF4', fg='#18191A', borderwidth=5, width=int(self.canvas.width/45), height=int(self.canvas.height/1000))
        self.sendButtonId = self.canvas.create_window(self.canvas.width/2, int(self.canvas.height/1.05),
                                                      anchor='center',
                                                      window=self.sendButton)
        self.sendButton.bind("<Configure>", self.onResize)


    def loadRsaPublicKey(self):
        file_public_key = open(str(self.account.userFolder) +
                               "/friends/"+self.nameFriend+"/keys/public_key.pem", 'rb')
        return RSA.importKey(file_public_key.read())

    def getAesKey(self):
        if(exists("resultFromGenerator.png")):
            os.remove("resultFromGenerator.png")
        fileGenerator = randomFile()
        subprocess.run(['Generator', fileGenerator])
        while(exists("resultFromGenerator.png") == False):
            continue
        fileGenerator = open("resultFromGenerator.png", "rb")
        return fileGenerator.read(AES.key_size[2])

    def encrypt(self, pathFile, key):
        with open(pathFile, "rb") as entry:
            data = entry.read()
            cipher = AES.new(key, AES.MODE_CBC)
            cipherText = cipher.encrypt(pad(data, AES.key_size[2]))
            iv = b64encode(cipher.iv)
            toWrite = iv + cipherText
        entry.close()

        if not os.path.exists("Encrypted to send/"):
            os.makedirs("Encrypted to send")

        with open("Encrypted to send/"+os.path.basename(pathFile), 'wb') as data:
            data.write(toWrite)
        data.close()
        return os.path.basename(pathFile)

    def addFile(self):
        Tk().withdraw()
        file = askopenfilename()
        self.root.lift()
        filesToSend.append(
            File(file, self.canvas, len(filesToSend)+1, self.root))

    def sendFile(self):
        try:
            self.sendButton["state"] = DISABLED
            nameFiles = []
            nameKeyFiles = []
            msg = MIMEMultipart()
            msg['From'] = self.account.username
            msg['To'] = self.nameFriend
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = "EncryptedFile"
            RsaPublicKey = self.loadRsaPublicKey()
            cipher = Cipher_PKCS1_v1_5.new(RsaPublicKey)
            keyToAes = self.getAesKey()
            if(exists("resultFromGenerator.png")):
                os.remove("resultFromGenerator.png")
            encryptedKeyToAes = cipher.encrypt(keyToAes)
            msg.attach(MIMEText(self.messages.get("1.0", 'end-1c')))

            for file in filesToSend:
                pathFileToSend = file.name
                nameFiles.append(self.encrypt(pathFileToSend, keyToAes))

            for nameFile in nameFiles:
                nameKeyFiles.append(nameFile.split(".")[0]+"_Key.txt")
                with open("./encrypted to send/"+nameFile, "rb") as file:
                    part = MIMEApplication(
                        file.read(),
                        Name=nameFile
                    )

                    part['Content-Disposition'] = 'attachment; filename="%s"' % nameFile
                    msg.attach(part)
                temp = os.path.abspath("./encrypted to send/"+nameFile)
                os.remove(temp)

            for nameKeyFile in nameKeyFiles:
                with open("./encrypted to send/"+nameKeyFile, "wb") as file:
                    file.write(encryptedKeyToAes)
                    file.close()
                with open("./encrypted to send/"+nameKeyFile, "rb") as file:
                    part = MIMEApplication(
                        file.read(),
                        Name=nameKeyFile
                    )

                    part['Content-Disposition'] = 'attachment; filename="%s"' % nameKeyFile
                    msg.attach(part)
                temp = os.path.abspath("./encrypted to send/"+nameKeyFile)
                os.remove(temp)

            self.account.serverToSend.sendmail(
                self.account.username, self.nameFriend, msg.as_string())
            self.root.after(10, lambda: _show(
                'Powiadomienie', 'Wysłano wiadomość'))
            self.canvas.delete(self.progressBarId)
            self.closeWindow()
        except:
            self.root.after(10, lambda: _show(
                'Powiadomienie', 'Nie udało się wysłać wiadomości'))
        

    def onResize(self, event):
        scale = 1 / max(self.width/self.canvas.width,
                        self.height/self.canvas.height)

        if(scale < (1/2)):
            scale = 1/2

        height = self.canvas.height/10

        self.messages.config(width=int(
            self.canvas.width/15), height=int(self.canvas.height/55), font=("Adobe Caslon Pro", int(20*scale)))

        xOffset = findXCenter(self.canvas, self.text)
        self.canvas.moveto(self.text, xOffset, int(height*1.5))
        self.canvas.itemconfigure(self.text, font=(
            "Adobe Caslon Pro", int(25*scale)))

        self.sendButton.config(font=("Adobe Caslon Pro", int(
            20*scale)))
        self.canvas.moveto(self.sendButtonId,
                           int(self.canvas.width/2)-(self.sendButton.winfo_width()/2), int(height*8))

        self.addFileButton.config(font=("Adobe Caslon Pro", int(
            20*scale)))
        self.canvas.moveto(self.addFileButtonId,
                           int(self.canvas.width/2)-(self.addFileButton.winfo_width()/2), int(height*9))
