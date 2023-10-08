from Canvas import *
from PIL import ImageTk
from math import *
from Account import *
from Crypto.PublicKey import RSA
from tkinter.filedialog import askopenfilename
from Functions import *
from tkinter.messagebox import _show
from tkinter import ttk
import threading
import datetime
from Database import *
from os.path import exists
import subprocess
from TopWindow import *

class GenerateKeyWindow(TopWindow):

    fileToGenerate = randomFile()

    def __init__(self, account, withWindow, loggedWindowRoot):
        self.loggedWindowRoot = loggedWindowRoot
        self.withWindow = withWindow
        self.account = account
        self.generateKeyThread = threading.Thread(target=self.generateKey)
        self.generateKeyThread.setDaemon(True)
        if(withWindow):
            TopWindow.__init__(self,False)
            self.root.title("Key generator")
            self.createButtonToGenerateKeys()
            self.createChooseText()
            self.createButtonToChooseKeys()
            self.createInputPath()
            self.createTimeSetter()
            self.canvas.addtag_all("all")

    def selectFile(self):
        Tk().withdraw()
        self.fileToGenerate = askopenfilename()
        self.pathToFile.delete(0, END)
        self.pathToFile.insert(0, self.fileToGenerate)
        self.root.lift()

    def generateKey(self):
        if(exists("resultFromGenerator.png")):
            os.remove("resultFromGenerator.png")
        database = Database()
        if(self.withWindow):
            self.generateKeyButton["state"] = DISABLED
            sourceGenerator = self.pathToFile.get()
        else:
            sourceGenerator = randomFile()

        if(self.withWindow):
            try:
                time = int(self.timeSetter.get())
            except:
                self.root.after(10, lambda: _show(
                    'Powiadomienie', 'Czas ważności musi być liczbą całkowitą'))
            if(time != None):
                database.updateColumn(self.account.username, "USER", "validity_time",
                                      int(time))
        

        subprocess.run(['Generator', sourceGenerator])
        while(exists("resultFromGenerator.png") == False):
            continue

        fileGenerator = open("resultFromGenerator.png", "rb")
        try:
            keys = RSA.generate(2048, fileGenerator.read)
            if(self.withWindow):
                self.root.after(10, lambda: _show(
                    'Powiadomienie', 'Wygenerowano klucze'))
        except:
            if(self.withWindow):
                self.root.after(10, lambda: _show(
                    'Powiadomienie', 'Nie wygenerowano kluczy, podaj inne źródło losowości'))
            return
        fileGenerator.close()

        if(exists("resultFromGenerator.png")):
            os.remove("resultFromGenerator.png")

        privateKey = keys.exportKey("PEM")
        publicKey = keys.publickey().exportKey("PEM")

        path = "./"+self.account.userFolder+"/keys"+"/"+"public_key.pem"
        fileForPublicKey = open(path, 'wb')
        fileForPublicKey.write(publicKey)
        fileForPublicKey.close()

        path = "./"+self.account.userFolder+"/keys"+"/"+"private_key.pem"
        fileForPrivateKey = open(path, 'wb')
        fileForPrivateKey.write(privateKey)
        fileForPrivateKey.close()

        database.updateColumn(self.account.username, "USER", "date_of_last_generate_key",
                              datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

        self.shareKey()
        if(self.withWindow):
            self.canvas.delete(self.progressBarId)

    def generate(self):
        if(self.withWindow):
            self.progressBar = ttk.Progressbar(
                self.root, orient=HORIZONTAL, length=self.width/3, mode="indeterminate")
            self.progressBarId = self.canvas.create_window(self.canvas.width/2, 50,
                                                           anchor='center',
                                                           window=self.progressBar)
            self.progressBar.start(10)
        self.generateKeyThread.start()

    def shareKey(self):
        database = Database()
        listOfReceivers = database.getReceivers(self.account.username)
        for receiver in listOfReceivers:
            self.account.sendPublicKey(receiver[0])
        return

    def createButtonToGenerateKeys(self):
        self.generateKeyButton = Button(self.root, text='Generuj klucze', font=("Adobe Caslon Pro", int(sqrt(
            self.canvas.width*self.canvas.height)/50)), command=self.generate, bg='#FCFBF4', fg='#18191A', borderwidth=5)
        self.generateKeyButtonId = self.canvas.create_window(self.canvas.width/6, int(self.canvas.height/4),
                                                             anchor='center',
                                                             window=self.generateKeyButton)

    def createInputPath(self):
        self.pathToFile = Entry(self.root, width=int(
            self.canvas.width/30), bg='#FCFBF4', fg='#18191A', borderwidth=5, font=("Adobe Caslon Pro", 15))
        self.pathToFileId = self.canvas.create_window(self.canvas.width/2, int(self.canvas.height*0.8),
                                                      anchor='center',
                                                      window=self.pathToFile)
        self.pathToFile.delete(0, END)
        self.pathToFile.insert(0, self.fileToGenerate)

    def createChooseText(self):
        self.chooseText = self.canvas.create_text(self.canvas.width/6, int(self.canvas.height*0.6), anchor='center', fill='#FCFBF4', font=(
            "Adobe Caslon Pro", int(sqrt(self.canvas.width*self.canvas.height)/50)), text='Aby wybrać własne źródło losowości, kliknij Wybierz plik\n')

    def createButtonToChooseKeys(self):
        self.chooseButton = Button(self.root, text='Wybierz plik', font=("Adobe Caslon Pro", int(sqrt(
            self.canvas.width*self.canvas.height)/50)), command=self.selectFile, bg='#FCFBF4', fg='#18191A', borderwidth=5)
        self.chooseButtonId = self.canvas.create_window(self.canvas.width/6, int(self.canvas.height*0.75),
                                                        anchor='center',
                                                        window=self.chooseButton)
        self.chooseButton.bind("<Configure>", self.onResize)

    def createTimeSetter(self):
        database = Database()
        self.timeSetterText = self.canvas.create_text(self.canvas.width/30, int(
            self.canvas.height/7), text='Czas ważności (minuty):', font=("Adobe Caslon Pro", 15), fill='#FCFBF4', anchor='center')
        self.timeSetter = Entry(self.root, width=int(
            self.canvas.width/45), bg='#FCFBF4', fg='#18191A', borderwidth=5, font=("Adobe Caslon Pro", 15))
        self.timeSetter.delete(0, END)
        self.timeSetter.insert(0,  database.getValue(
            self.account.username, "USER", 'validity_time'))
        self.timeSetter.pack()
        self.timeSetterId = self.canvas.create_window(int(self.canvas.width/30), int(self.canvas.height/8),
                                                      anchor='center',
                                                      window=self.timeSetter)

    def startLoop(self):
        self.root.mainloop()

    def onResize(self, event):
        scale = 1 / max(self.width/self.canvas.width,
                        self.height/self.canvas.height)

        if(scale < (1/2)):
            scale = 1/2
        height = self.canvas.height/16
        width = self.canvas.width/16

        self.pathToFile.config(font=("Adobe Caslon Pro", int(
            15*scale)), width=int(width/1.4))

        self.timeSetter.config(font=("Adobe Caslon Pro", int(
            15*scale)), width=int(width/8))

        self.generateKeyButton.config(font=("Adobe Caslon Pro", int(25*scale)))

        self.canvas.moveto(self.generateKeyButtonId,
                           int(width*3), int(height*5))

        self.chooseButton.config(font=("Adobe Caslon Pro", int(25*scale)))
        self.canvas.itemconfigure(self.chooseText, font=(
            "Adobe Caslon Pro", int(25*scale)))
        self.canvas.moveto(self.chooseText, int(width*3), int(height*11.5))
        self.canvas.moveto(self.chooseButtonId,
                           int(width*3), int(height*13))
        self.canvas.moveto(self.pathToFileId,
                           int(width*5), int(height*13 + self.pathToFile.winfo_height()/2))

        self.canvas.itemconfigure(self.timeSetterText, font=(
            "Adobe Caslon Pro", int(25*scale)))
        self.canvas.moveto(self.timeSetterText,
                           int(width * 11 - self.timeSetter.winfo_width()/4), int(height*3.5))
        self.canvas.moveto(self.timeSetterId,
                           int(width * 11), int(height*5 + self.timeSetter.winfo_height()/2))
