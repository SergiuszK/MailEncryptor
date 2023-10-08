import os
from os.path import basename
from Crypto.Hash import SHA256
import smtplib
import imaplib
import email
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from email.mime.text import MIMEText
import threading
from tkinter.messagebox import _show
import datetime
from Database import *

class Account():
    username = None
    password = None
    smtp_ssl_host = 'smtp.gmail.com'
    imap_ssl_host = 'imap.gmail.com'
    smtp_ssl_port = 465
    imap_ssl_port = 993
    userFolder = None

    def __init__(self, email, password, root):
        self.serverToSend = smtplib.SMTP_SSL(
            self.smtp_ssl_host, self.smtp_ssl_port)
        self.serverToReceive = imaplib.IMAP4_SSL(
            self.imap_ssl_host, self.imap_ssl_port)
        self.isDownloaded = False
        self.root = root
        self.username = email
        self.password = password
        self.downloadFilesAndKeys = threading.Thread(target=self.receiveKeys)
        self.downloadFilesAndKeys.setDaemon(True)

    def logout(self):
        self.login(False)
        self.serverToSend.quit()
        self.serverToSend.close()
        self.serverToReceive.logout()

    def afterLogin(self):
        database = Database()
        self.makeFolders()
        database.createNewUser(self.username)

    def makeFolders(self):
        temp = str.encode(self.username)
        self.userFolder = str(SHA256.new(temp).hexdigest())
        if not os.path.exists(self.userFolder):
            os.makedirs(self.userFolder)
            os.makedirs(self.userFolder+"/keys")
            os.makedirs(self.userFolder+"/friends/")
            os.makedirs(self.userFolder+"/received files/")

    def checkIfKeysExists(self):
        if not os.path.exists(str(self.userFolder)+"/public_key.pem") or not os.path.exists(str(self.userFolder)+"/private_key.pem"):
            self.hasKeys = False
        else:
            self.hasKeys = True

    def sendPublicKey(self, email):
        try:
            self.login(False)
            database = Database()

            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = email
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = "PublicKey"

            file = "./"+self.userFolder+"/keys"+"/"+"public_key.pem"

            with open(file, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(file),
                )
                part['Content-Disposition'] = 'attachment; filename="%s"' % basename(
                    file)

                msg.attach(part)

            date = database.getValue(
                self.username, "USER", "date_of_last_generate_key")
            valdityTime = database.getValue(self.username, "USER", 'validity_time')
            valdityDate = datetime.datetime.strptime(
                date, '%Y-%m-%d %H:%M:%S')
            valdityDate = valdityDate + datetime.timedelta(minutes=valdityTime)

            msg.attach(MIMEText(valdityDate.strftime('%Y-%m-%d %H:%M:%S')))
            self.serverToSend.sendmail(self.username, email, msg.as_string())
            return True
        except:
            return False

    def deleteMails(self, keys):
        self.serverToReceive.select()
        if(keys):
            type, data = self.serverToReceive.search(
                None, '(SUBJECT "PublicKey")')
        else:
            type, data = self.serverToReceive.search(
                None, '(SUBJECT "EncryptedFile")')
        mail_ids = data[0]
        id_list = mail_ids.split()
        for id in id_list:
            self.serverToReceive.store(id, "+FLAGS", "\\Deleted")
        self.serverToReceive.expunge()

    def receiveKeys(self):
        self.login(False)
        self.isDownloaded = False
        self.serverToReceive.select()
        type, data = self.serverToReceive.search(None, '(SUBJECT "PublicKey")')
        if(data == [b'']):
            self.receiveFiles()
        mail_ids = data[0]
        id_list = mail_ids.split()
        for id in id_list:
            typ, data = self.serverToReceive.fetch(id, '(RFC822)')
            raw_email = data[0][1]
            raw_email_string = raw_email.decode('utf-8')
            email_message = email.message_from_string(raw_email_string)
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if(content_type == "text/plain"):
                    database = Database()
                    datestring = part.get_payload()
                    database.createNewSender(email_message['From'], self.username, datetime.datetime.strptime(
                        datestring, '%Y-%m-%d %H:%M:%S'))
                elif "attachment" in content_disposition:
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    fileName = part.get_filename()
                    filePath = os.path.join(
                        "./"+self.userFolder+"/friends/"+email_message['From']+"/keys/", fileName)

                    if bool(fileName):
                        if not os.path.exists(self.userFolder+"/friends/"+email_message['From']):
                            os.makedirs(self.userFolder+"/friends/" +
                                        email_message['From'])
                        if not os.path.exists(self.userFolder+"/friends/"+email_message['From']+"/keys"):
                            os.makedirs(self.userFolder+"/friends/" +
                                        email_message['From']+"/keys")

                        fp = open(filePath, 'wb')
                        fp.write(part.get_payload(decode=True))
                        fp.close()


        self.deleteMails(True)
        self.checkIfKeysExists()
        self.receiveFiles()

    def receiveFiles(self):
        type, data = self.serverToReceive.search(
            None, '(SUBJECT "EncryptedFile")')
        if(data == [b'']):
            self.isDownloaded = True
            return False
        mail_ids = data[0]
        id_list = mail_ids.split()
        for id in id_list:
            typ, data = self.serverToReceive.fetch(id, '(RFC822)')
            raw_email = data[0][1]
            raw_email_string = raw_email.decode('utf-8')
            email_message = email.message_from_string(raw_email_string)

            for part in email_message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                fileName = part.get_filename()
                filePath = os.path.join(
                    "./"+self.userFolder + "/received files/"+email_message['From'], fileName)

                if bool(fileName):
                    if not os.path.exists("./"+self.userFolder+"/received files"):
                        os.makedirs("./"+self.userFolder+"/received files")
                    if not os.path.exists("./"+self.userFolder+"/received files/"+email_message['From']):
                        os.makedirs("./"+self.userFolder +
                                    "/received files/"+email_message['From'])

                    fp = open(filePath, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()

        self.deleteMails(False)
        self.isDownloaded = True
        return

    def validateKey(self):
        database = Database()
        date = database.getValue(
            self.username, "USER", "date_of_last_generate_key")
        validityTime = database.getValue(
            self.username, "USER", "validity_time")
        if(date != None and validityTime != None):
            validityDate = datetime.datetime.strptime(
                date, '%Y-%m-%d %H:%M:%S')
            validityDate = validityDate + \
                datetime.timedelta(minutes=validityTime)
            now = datetime.datetime.utcnow()
            difference = validityDate - now
            seconds_in_day = 24 * 60 * 60
            difference = divmod(
                difference.days * seconds_in_day + difference.seconds, 60)
            if(difference[0] >= 0):
                return False, validityDate, difference[0]
            else:
                return True, validityDate, difference[0]
        else:
            return True, False, False

    def login(self, firstLogin):
        try:
            self.serverToSend = smtplib.SMTP_SSL(
                self.smtp_ssl_host, self.smtp_ssl_port)
            self.serverToReceive = imaplib.IMAP4_SSL(
                self.imap_ssl_host, self.imap_ssl_port)
            self.serverToSend.login(self.username, self.password)
            self.serverToReceive.login(self.username, self.password)
            if(firstLogin):
                self.afterLogin()
            return True
        except:
            return False
