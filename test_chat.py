import unittest
import chat
from datetime import datetime, timedelta

class ChatUnitTests(unittest.TestCase):

    def setUp(self):
        today = datetime.utcnow()
        chat.fileName = "unitTestFile_{0}-{1:02d}-{2:02d}.txt".format(today.year, today.month, today.day)

    def tearDown(self):
        import os
        if os.path.isfile(chat.fileName):
            os.remove(chat.fileName)

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
        msg, users = chat.readActivityFile()
        self.assertEqual(users[0].active, True)

    def test_UserStatusIsFalse_WhenFalseActivityLogged(self):
        u = chat.UserActivity(name = "TestUser", active = "false") 
        chat.logUserActivity(u)
        msg, users = chat.readActivityFile()
        self.assertEqual(users[0].active, False)

    def test_UserStatusIsFalse_WhenTrueThenFalseActivityLogged(self):
        u = chat.UserActivity(name = "TestUser", active = "true") 
        chat.logUserActivity(u)
        u = chat.UserActivity(name = "TestUser", active = "false") 
        chat.logUserActivity(u)
        msg, users = chat.readActivityFile()
        self.assertEqual(users[0].active, False)

    def test_UserStatusIsTrue_WhenFalseThenTruePythonBooleanActivityRead(self):
        u = chat.UserActivity(name = "TestUser", active = False) 
        chat.logUserActivity(u)
        u = chat.UserActivity(name = "TestUser", active = True) 
        chat.logUserActivity(u)
        msg, users = chat.readActivityFile()
        self.assertEqual(users[0].active, True)

    def test_UserIsLoggedOut_AfterTwoMinutesWithoutPolling(self):
        today = datetime.utcnow()
        threeMinuteAgoDelta = timedelta(minutes = -2)
        u = chat.UserActivity(name = "TestUser", active = False, date = today + threeMinuteAgoDelta)
        chat.logUserActivity(u)

        twoMinuteAgoDelta = timedelta(minutes = -2)
        u = chat.UserActivity(name = "TestUser", active = False, date = today + twoMinuteAgoDelta)
        chat.logUserActivity(u)
        msg, users = chat.readActivityFile()
        self.assertEqual(0, len(users))

    def test_MessageObject_CanBeSerializedAndDeSerialized(self):
        m = chat.Message(user = "TestUser", date = datetime.utcnow(), message = "unit test message")
        chat.storeMessage(m)
        msgs, users = chat.readActivityFile()
        self.assertEqual(1, len(msgs))


def main():
    unittest.main()

if __name__ == '__main__':
    main()
