from MainWindow import *

class LoginWindow(MainWindow):
    emailInput = None
    passwordInput = None
    root = None
    frame = None
    canvas = None
    login = None
    tryLogged = False
    welcomeText = None
    
    def __init__(self):
        MainWindow.__init__(self)
        self.tryLogged = False
        self.createWindow()
        
    def createWindow(self):
        self.root.title("Mail Encryption")
        self.createEmailInput()
        self.createPasswordInput()
        self.createLoginButton()
        self.canvas.addtag_all("all")
        
    def tryLogin(self):
        self.email = self.emailInput.get()
        self.password = self.passwordInput.get()
        if(self.email=='' or self.password==''):
            return
        self.tryLogged = True
        self.root.quit()

    def createLoginButton(self):
        self.loginButton = Button(self.root, text='Zaloguj się', font=("Adobe Caslon Pro", 10), command=self.tryLogin,
                                  bg='#FCFBF4', fg='#18191A', borderwidth=5, width=int(self.canvas.width/45), height=int(self.canvas.height/1000))

        self.loginButtonId = self.canvas.create_window(int(self.canvas.width/2), int(self.canvas.height/1.5),
                                                       anchor='center',
                                                       window=self.loginButton)

        self.loginButton.bind("<Configure>", self.onResize)

    def createEmailInput(self):
        self.emailText = self.canvas.create_text(int(self.canvas.width/2), int(
            self.canvas.height/3), text='Adres email:', font=("Adobe Caslon Pro", 15), fill='#FCFBF4', justify='left')
        self.emailInput = Entry(self.root, width=int(
            self.canvas.width/45), bg='#FCFBF4', fg='#18191A', borderwidth=5)
        self.emailInputId = self.canvas.create_window(int(self.canvas.width/2), int(self.canvas.height/2.7),
                                                      anchor='center',
                                                      window=self.emailInput)

    def createPasswordInput(self):
        self.passwordText = self.canvas.create_text(int(self.canvas.width/2), int(
            self.canvas.height/2.3), font=("Adobe Caslon Pro", 15), fill='#FCFBF4', text='Hasło:', justify='left')
        self.passwordInput = Entry(self.root, width=int(
            self.canvas.width/45), bg='#FCFBF4', fg='#18191A', borderwidth=5, show="*")
        self.passwordInputId = self.canvas.create_window(int(self.canvas.width/2)-self.passwordInput.winfo_width(), int(self.canvas.height/2),
                                                         anchor='center',
                                                         window=self.passwordInput)

    def getLoginButton(self):
        return self.loginButton

    def getLoginInput(self):
        return self.emailInput

    def getPasswordInput(self):
        return self.passwordInput

    def onResize(self, event):
        scale = 1 / max(self.width/self.canvas.width,
                        self.height/self.canvas.height)

        if(scale < (1/2)):
            scale = 1/2

        height = self.canvas.height/10

        xOffset = findXCenter(self.canvas, self.emailText)
        self.canvas.itemconfigure(self.emailText, font=(
            "Adobe Caslon Pro", int(20*scale)), anchor='n')
        self.canvas.moveto(self.emailText, xOffset,
                           int(height*3.25))

        self.emailInput.config(font=("Adobe Caslon Pro", int(
            20*scale)), justify=CENTER, width=int(50*scale))
        self.canvas.moveto(self.emailInputId, int(
            self.canvas.width/2)-(self.emailInput.winfo_width()/2), int(height*3.75))

        xOffset = findXCenter(self.canvas, self.passwordText)
        self.canvas.itemconfigure(self.passwordText, font=(
            "Adobe Caslon Pro", int(20*scale)), anchor='n')
        self.canvas.moveto(self.passwordText, xOffset,
                           int(height*4.75))

        self.passwordInput.config(font=("Adobe Caslon Pro", int(
            20*scale)), justify=CENTER, width=int(50*scale))
        self.canvas.moveto(self.passwordInputId, int(
            self.canvas.width/2)-(self.passwordInput.winfo_width()/2), int(height*5.25))

        self.loginButton.config(font=("Adobe Caslon Pro", int(
            20*scale)), justify=CENTER, width=int(20*scale))

        self.canvas.moveto(self.loginButtonId, int(
            self.canvas.width/2)-(self.loginButton.winfo_width()/2), int(height*6.25))
