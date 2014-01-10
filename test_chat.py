import unittest
import json
import chat
import os
from datetime import datetime, timedelta
from collections import namedtuple
from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
import transaction

def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

def getMessagesAndUsersFromJson(json):
    response = json2obj(json)
    return response.data.messages, response.data.users

class ChatUnitTests(unittest.TestCase):

    def setUp(self):
        chat.open_db()

    def tearDown(self):
        chat.close_db()
        os.remove('db/webChat.fs')
        os.remove('db/webChat.fs.index')
        os.remove('db/webChat.fs.lock')
        os.remove('db/webChat.fs.tmp')

    def test_MessageObject_DoesNotReturnHTMLInMessagePropertyWhenConstructedWithHTML(self):
        msg = chat.Message(message = "<html>")
        self.assertEqual("&lt;html&gt;", msg.message)

    def test_MessageObject_DoesNotReturnHTMLInMessagePropertyWhenAssigned(self):
        msg = chat.Message()
        msg.message = "<html>"
        self.assertEqual("&lt;html&gt;", msg.message)

    def test_UserStatusIsTrue_WhenTrueActivityLogged(self):
        u = chat.UserActivity(name = "TestUser", active = "true") 
        chat.logUserActivity(u)
        msg, users = getMessagesAndUsersFromJson(chat.getMessages())
        self.assertEqual(users[0].active, True)

    def test_UserStatusIsFalse_WhenFalseActivityLogged(self):
        u = chat.UserActivity(name = "TestUser", active = "false") 
        chat.logUserActivity(u)
        msg, users = getMessagesAndUsersFromJson(chat.getMessages())
        self.assertEqual(users[0].active, False)

    def test_UserStatusIsFalse_WhenTrueThenFalseActivityLogged(self):
        u = chat.UserActivity(name = "TestUser", active = "true") 
        chat.logUserActivity(u)
        u = chat.UserActivity(name = "TestUser", active = "false") 
        chat.logUserActivity(u)
        msg, users = getMessagesAndUsersFromJson(chat.getMessages())
        self.assertEqual(users[0].active, False)

    def test_UserStatusIsTrue_WhenFalseThenTruePythonBooleanActivityRead(self):
        u = chat.UserActivity(name = "TestUser", active = False) 
        chat.logUserActivity(u)
        u = chat.UserActivity(name = "TestUser", active = True) 
        chat.logUserActivity(u)
        msg, users = getMessagesAndUsersFromJson(chat.getMessages())
        self.assertEqual(users[0].active, True)

    def test_UserIsLoggedOut_AfterTwoMinutesWithoutPolling(self):
        today = datetime.utcnow()
        threeMinuteAgoDelta = timedelta(minutes = -3)
        u = chat.UserActivity(name = "TestUser", active = False, date = today + threeMinuteAgoDelta)
        chat.logUserActivity(u)

        twoMinuteAgoDelta = timedelta(minutes = -2)
        u = chat.UserActivity(name = "TestUser", active = False, date = today + twoMinuteAgoDelta)
        chat.logUserActivity(u)
        msg, users = getMessagesAndUsersFromJson(chat.getMessages())
        self.assertEqual(0, len(users))

    def test_MessageObject_CanBeSerializedAndDeSerialized(self):
        m = chat.Message(user = "TestUser", date = datetime.utcnow(), message = "unit test message")
        chat.storeMessage(m)
        msg, users = getMessagesAndUsersFromJson(chat.getMessages())
        self.assertEqual(1, len(msg))

    def test_UserIsLoggedIn_WhileTheyAreStillActiveOrPolling(self):
        today = datetime.utcnow()
        threeMinuteAgoDelta = timedelta(minutes = -3)
        u = chat.UserActivity(name = "TestUser", active = False, date = today + threeMinuteAgoDelta)
        chat.logUserActivity(u)

        msg, users = getMessagesAndUsersFromJson(chat.getMessages())
        self.assertEqual(0, len(users))

        u.date = today
        chat.logUserActivity(u)

        msg, users = getMessagesAndUsersFromJson(chat.getMessages())
        self.assertEqual(1, len(users))

    def test_UserIsLoggedIn_WhileTheyAreTyping(self):
        today = datetime.utcnow()
        threeMinuteAgoDelta = timedelta(minutes = -3)
        u = chat.UserActivity(name = "TestUser", active = False, date = today + threeMinuteAgoDelta)
        chat.logUserActivity(u)

        m = chat.Message(user = "TestUser", date = datetime.utcnow(), message = "test message")
        chat.storeMessage(m)

        msg, users = getMessagesAndUsersFromJson(chat.getMessages())
        self.assertEqual(1, len(users))

    def test_LinkInMessage_IsConvertedToHtmlLink(self):
        m = chat.Message(user = "TestUser", message = "http://www.google.com")
        chat.storeMessage(m)

        msg, users = getMessagesAndUsersFromJson(chat.getMessages())
        self.assertEqual(1, len(msg))
        self.assertEqual("<a href=\"http://www.google.com\" target=\"_blank\" tabindex=\"-1\">http://www.google.com</a>",
            msg[0].message)
        
def main():
    unittest.main()

if __name__ == '__main__':
    main()
