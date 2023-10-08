import sqlite3 as sl
import datetime


class Database:
    def __init__(self):
        self.con = sl.connect('database.db', isolation_level=None)
        self.createTables()

    def close(self):
        self.con.close()

    def checkIfExistsOneCondition(self, table, id, value):
        with self.con:
            cursor = self.con.cursor()
            cursor.execute(
                "SELECT COUNT(id) FROM %s WHERE %s = '%s';" % (table, id, value))
            (number_of_rows,) = cursor.fetchone()

            if(number_of_rows > 0):
                return True
            else:
                return False

    def checkIfExistsTwoConditions(self, table, id, value, id_2, value_2):
        with self.con:
            cursor = self.con.cursor()
            cursor.execute("SELECT COUNT(id) FROM %s WHERE %s = '%s' and %s = %s;" % (
                table, id, value, id_2, value_2))
            (number_of_rows,) = cursor.fetchone()
            if(number_of_rows > 0):
                return True
            else:
                return False

    def createNewUser(self, mail):
        if(self.checkIfExistsOneCondition("USER", "mail", mail) == False):
            with self.con:
                self.con.execute(
                    "INSERT INTO USER (mail,validity_time) VALUES ('%s',%d);" % (mail, 60))

    def getUserIdByMail(self, mail):
        with self.con:
            cursor = self.con.cursor()
            cursor.execute("SELECT id FROM USER WHERE mail = '%s';" % (mail))
            (id,) = cursor.fetchone()
        return id

    def createNewReceiver(self, mailReceiver, mailOwner):
        ownerId = self.getUserIdByMail(mailOwner)

        if(self.checkIfExistsTwoConditions("RECEIVER", "mail", mailReceiver, "owner_id", ownerId) == False):
            with self.con:
                self.con.execute("INSERT INTO RECEIVER (mail,owner_id) VALUES ('%s',%d);" % (
                    mailReceiver, ownerId))

    def createNewSender(self, mailSender, mailOwner, date):
        ownerId = self.getUserIdByMail(mailOwner)

        if(self.checkIfExistsTwoConditions("SENDER", "mail", mailSender, "owner_id", ownerId) == False):
            with self.con:
                self.con.execute("INSERT INTO SENDER (mail,owner_id,date_of_validity_key) VALUES ('%s',%d,'%s');" % (
                    mailSender, ownerId, date))
        else:
            with self.con:
                self.con.execute(
                    "UPDATE SENDER SET date_of_validity_key = '%s' WHERE mail = '%s';" % (date, mailSender))

    def deleteReceiver(self, mailReceiver, mailOwner):
        ownerId = self.getUserIdByMail(mailOwner)

        if(self.checkIfExistsTwoConditions("RECEIVER", "mail", mailReceiver, "owner_id", ownerId)):
            with self.con:
                self.con.execute("DELETE FROM RECEIVER WHERE mail = '%s' AND owner_id = %d;" % (
                    mailReceiver, ownerId))
            return True
        else:
            return False

    def getReceivers(self, mail):
        id = self.getUserIdByMail(mail)

        with self.con:
            cursor = self.con.cursor()
            cursor.execute(
                "SELECT mail FROM RECEIVER WHERE owner_id = '%s';" % (id))
            results = cursor.fetchall()

        return results

    def updateColumn(self, mail, table, column, value):
        id = self.getUserIdByMail(mail)

        with self.con:
            cursor = self.con.cursor()
            cursor.execute("UPDATE %s SET %s = '%s' WHERE id = '%s';" %
                           (table, column, value, id))

    def getValue(self, mail, table, column):
        id = self.getUserIdByMail(mail)

        with self.con:
            cursor = self.con.cursor()
            cursor.execute("SELECT %s FROM %s WHERE id = '%s';" %
                           (column, table, id))
            (result,) = cursor.fetchone()

        return result

    def getValidityDate(self, username, sender):
        ownerId = self.getUserIdByMail(username)
        if(self.checkIfExistsTwoConditions("SENDER", "mail", sender, "owner_id", ownerId)):
            with self.con:
                cursor = self.con.cursor()
                cursor.execute(
                    "SELECT date_of_validity_key FROM SENDER WHERE mail = '%s' and owner_id = %d;" % (sender, ownerId))
                (date,) = cursor.fetchone()
            return date
        else:
            return False

    def checkIfKeySenderIsAvailable(self, username, sender):
        date = self.getValidityDate(username, sender)
        if(date == False):
            return False
        now = datetime.datetime.utcnow()
        dateOfReceiveKey = datetime.datetime.strptime(
            date, '%Y-%m-%d %H:%M:%S')
        difference = now - dateOfReceiveKey
        seconds_in_day = 24 * 60 * 60
        difference = divmod(
            difference.days * seconds_in_day + difference.seconds, 60)
        if(difference[0] < 0):
            return True
        else:
            return False

    def createTables(self):
        with self.con:

            self.con.execute("""
                CREATE TABLE if not exists USER (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    mail TEXT,
                    date_of_last_generate_key DATE,
                    validity_time INTEGER
                    );
                """)

            self.con.execute("""
                CREATE TABLE if not exists RECEIVER (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    mail TEXT,
                    owner_id INTEGER,
                    FOREIGN KEY (owner_id) REFERENCES USER(id)
                    );
                """)

            self.con.execute("""
                CREATE TABLE if not exists SENDER (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    mail TEXT,
                    owner_id INTEGER,
                    date_of_validity_key DATE,
                    FOREIGN KEY (owner_id) REFERENCES USER(id)
                    );
                """)
