from TopWindow import *
from tkinter.messagebox import _show

class ShareKeyWindow(TopWindow):

    def __init__(self, account):
        TopWindow.__init__(self,False)
        self.account = account
        self.database = Database()
        self.root.title("Share Key")
        self.createEmailInput()
        self.createShareButton()
        self.createChecboxAddToTheList()
        self.createDeleteButton()
        self.canvas.addtag_all("all")

    def shareKey(self):
        email = self.emailInput.get()
        if(self.var.get() == 1):
            self.database.createNewReceiver(email, self.account.username)
        else:
            self.database.deleteReceiver(email, self.account.username)

        if(self.account.sendPublicKey(email)):
            self.root.after(10, lambda: _show('Powiadomienie','Udostępniono klucz: ' + email))
        else:
            self.root.after(10, lambda: _show('Powiadomienie', 'Nie udało się udostępnić klucza dla: ' + email))
            
    def deleteMail(self):
        email = self.emailInput.get()
        if(self.database.deleteReceiver(email, self.account.username)):
            self.root.after(10, lambda: _show('Powiadomienie','Usunięto: ' + email +" z listy automatycznego udostępniania"))
        else:
            self.root.after(10, lambda: _show('Powiadomienie', 'Nie udało się usunąć ' + email + " z listy automatycznego udostępniania"))
                
    def createChecboxAddToTheList(self):
        self.var = IntVar()
        self.checkbox = Checkbutton(
            self.root, text="Wysyłaj automatycznie nowe wersje klucza", variable=self.var,font=("Adobe Caslon Pro", 15))
        self.checkboxId = self.canvas.create_window(int(self.canvas.width/2)-self.shareButton.winfo_width(), int(self.canvas.height/1.25),
                                                       anchor='center',
                                                       window=self.checkbox)

    def createEmailInput(self):
        self.emailText = self.canvas.create_text(self.canvas.width/2-30, int(
            self.canvas.height/6), text='Adres email:', font=("Adobe Caslon Pro", 15), fill='#FCFBF4', anchor='center')
        self.emailInput = Entry(self.root, width=int(
            self.canvas.width/45), bg='#FCFBF4', fg='#18191A', borderwidth=5)
        self.emailInputId = self.canvas.create_window(int(self.canvas.width/2)-self.emailInput.winfo_width(), int(self.canvas.height/4),
                                                      anchor='center',
                                                      window=self.emailInput)

    def createShareButton(self):
        self.shareButton = Button(self.root, text='Udostępnij klucz', font=(
            "Adobe Caslon Pro", 10), command=self.shareKey, bg='#FCFBF4', fg='#18191A', borderwidth=5)
        self.shareButtonId = self.canvas.create_window(int(self.canvas.width/2)-self.shareButton.winfo_width(), int(self.canvas.height/2),
                                                       anchor='center',
                                                       window=self.shareButton)
        
    def createDeleteButton(self):
        self.deleteButton = Button(self.root, text='   Usuń z listy   ', font=(
            "Adobe Caslon Pro", 10), command=self.deleteMail, bg='#FCFBF4', fg='#18191A', borderwidth=5)
        self.deleteButtonId = self.canvas.create_window(int(self.canvas.width/2)-self.shareButton.winfo_width(), int(self.canvas.height/1.5),
                                                       anchor='center',
                                                       window=self.deleteButton)
        self.deleteButton.bind("<Configure>", self.onResize)

    def onResize(self, event):
        scale = 1 / max(self.width/self.canvas.width,
                        self.height/self.canvas.height)

        if(scale < (1/2)):
            scale = 1/2

        height = self.canvas.height/8

        xOffset = findXCenter(self.canvas, self.emailText)
        self.canvas.moveto(self.emailText, xOffset, int(height*2.5))
        self.canvas.itemconfigure(self.emailText, font=(
            "Adobe Caslon Pro", int(25*scale)))

        self.emailInput.config(font=("Adobe Caslon Pro", int(30*scale)))
        self.canvas.moveto(self.emailInputId, int(
            self.canvas.width/2)-(self.emailInput.winfo_width()/2), int(height*3.25))


        self.shareButton.config(font=("Adobe Caslon Pro", int(20*scale)))
        self.canvas.moveto(self.shareButtonId, int(
            self.canvas.width/2)-(self.shareButton.winfo_width()/2), int(height*4.25))
        
        self.deleteButton.config(font=("Adobe Caslon Pro", int(20*scale)))
        self.canvas.moveto(self.deleteButtonId, int(
            self.canvas.width/2)-(self.deleteButton.winfo_width()/2), int(height*5.25))

        self.checkbox.config(font=("Adobe Caslon Pro", int(20*scale)))
        self.canvas.moveto(self.checkboxId, int(
            self.canvas.width/2)-(self.checkbox.winfo_width()/2), int(height*7))