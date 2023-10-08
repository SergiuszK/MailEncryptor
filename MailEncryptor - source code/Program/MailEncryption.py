from LoggedWindow import *
from LoginWindow import *
from Account import *

def main():
    loginPage = LoginWindow()
    
    loggedWindow = None
    mail = None
    password = None
    account = None

    loginPage.startLoop()
    while(True):
        
        if(loginPage != None and loginPage.tryLogged == True):
            mail = loginPage.email
            password = loginPage.password
            account = Account(mail, password, loginPage.root)

            if(account.login(True)):
                loginPage.tryLogged = False
                loginPage.destroy()
                loginPage = None
                loggedWindow = LoggedWindow(account)
                loggedWindow.startLoop()
            else:
                loginPage.tryLogged = False
                account = None
                loginPage.root.after(10, lambda: messagebox.showerror('Powiadomienie', 'Logowanie nie powiodło się'))
                loginPage.startLoop()
                
                
        if(loggedWindow != None and loggedWindow.logouted == True):
            loggedWindow.destroy()
            loggedWindow = None
            account = None
            loginPage = LoginWindow()
            loginPage.startLoop()

if __name__ == "__main__":
    main()
