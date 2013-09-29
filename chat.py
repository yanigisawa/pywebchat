#!/usr/bin/python

# Long Polling Example:
# http://techoctave.com/c7/posts/60-simple-long-polling-example-with-javascript-and-jquery
## Actor 1 in module1.py
##

import cgi, cgitb; cgitb.enable();

import time, os, json, dateutil.parser, re
from datetime import datetime, timedelta

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from threading import Event

from collections import namedtuple

today = datetime.utcnow()
fileName = "chat/{0}-{1:02d}-{2:02d}.txt".format(today.year, today.month, today.day)

_newMsg = Event()
_observer = Observer()

class FileChangeHandler(LoggingEventHandler):
    def on_created(self, event):
        pass
    def on_deleted(self,event):
        pass

    def on_any_event(self, event):
        currentDirectory = os.getcwd()
        f = os.path.join(currentDirectory, fileName)
        if os.path.realpath(event.src_path) == f:
            _newMsg.set()
            _observer.stop()

    def on_modified(self, event):
        pass

class Message(object):
    def __init__(self, user = None, message = None, date = None, filterHTML = True):
        self.filterHTML = filterHTML
        self.user = user
        self.message = message
        self.date = date

    @staticmethod
    def replaceUrlsWithLinks(msg):
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', msg)
        newMsg = ""
        print("msg: {0} - count of urls: {1}".format(msg, len(urls)))
        if len(urls) > 0:
            for u in urls:
                newMsg = msg.replace(u, "<a href=\"{0}\" target=\"_blank\">{0}</a>".format(u))
        else:
            newMsg = msg

        return newMsg

    @property
    def message(self): 
        return self.m_message

    @message.setter
    def message(self, value):
        if value != None: 
            if self.filterHTML:
                self.m_message = value.replace("<", "&lt;").replace(">", "&gt;")
                self.m_message = Message.replaceUrlsWithLinks(self.m_message)
            else: 
                self.m_message = value

    def __str__(self):
        return "{0} - {1}: {2}".format(self.date, self.user, self.message)


class UserActivity(object):
    def __init__(self, name = None, active = False, date = None):
        self.name = name

        if isinstance(active, str):
            self.active = (active == "true")
        else:
            self.active = active

        self.date = date

    @property
    def date(self):
        return self.m_date

    @date.setter
    def date(self, value):
        if isinstance(value, datetime):
            self.m_date = value 
        elif value != None:
            self.m_date = dateutil.parser.parse(value)
        else:
            self.m_date = None

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return "{0} - {1} - {2}".format(self.name, self.active, self.date)

class ChatApiResponse(object):
    def __init__(self, messages = [], users = []):
        self.messages = messages
        self.users = users

class ApiResult(object):
    def __init__(self, success = True, message = None, data = None):
        self.success = success
        self.message = message
        self.data = data

def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

class MessageEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, Message):
            return obj.__dict__

        if isinstance(obj, ApiResult):
            return obj.__dict__

        if isinstance(obj, UserActivity):
            x = {}
            x["name"], x["date"], x["active"] = obj.name, obj.date, obj.active
            return x

        if isinstance(obj, ChatApiResponse):
            return obj.__dict__

        return super(MessageEncoder, self).default(obj)

def storeMessage(msg):
    with open(fileName, 'a') as f:
        f.write("Message: {0}\n".format(json.dumps(msg, cls=MessageEncoder)))

def logUserActivity(userActivity):
    with open(fileName, 'a') as f:
        s = "UserActivity: {0}\n".format(json.dumps(userActivity, cls=MessageEncoder))
        f.write(s)

def getModifiedUsersArray(users, u):
    userObjectToReturn = UserActivity(name = u.name, active = u.active, date = u.date)

    if u in users:
        for user in users:
            if u == user:
                user.active = u.active
                user.date = u.date
                break
    else:
        users.append(userObjectToReturn)

    return users

def removeInactiveUsers(users):
    today = datetime.utcnow()
    twoMinutesAgo = today + timedelta(minutes = -2)

    for user in users:
        if (user.date != None and user.date <= twoMinutesAgo):
            users.remove(user)

    return users

def setUserActivityDate(userArray, userName, date):
    for user in userArray:
        if user.name == userName: 
            user.date = date
            break

    return userArray

def readActivityFile():
    messages = []
    users = []

    if os.path.isfile(fileName): 
        with open(fileName, 'r') as f:
            for line in f:
                if line.startswith("Message: "):
                    m = json2obj(line.lstrip("Message: ").strip())
                    msg = Message(user = m.user, date = m.date, filterHTML = False, message = m.m_message)
                    messages.append(msg)
                    users = setUserActivityDate(users, msg.user, msg.date)
                elif line.startswith("UserActivity: "):
                    u = json2obj(line.lstrip("UserActivity: ").strip())
                    users = getModifiedUsersArray(users, u)

    users = removeInactiveUsers(users)

    return (messages, users)

def printMessages():
    print("Content-type: application/json")
    print(os.linesep)

    result = ApiResult()
    result.success = True
    messages, users = readActivityFile()
    chatResponse = ChatApiResponse(messages = messages, users = users)
    result.data = chatResponse

    print(json.dumps(result, cls=MessageEncoder))


def waitForNewMessages():
    event_handler = FileChangeHandler()
    path = os.getcwd()
    path = os.path.join(path, "chat")
    _observer.schedule(event_handler, path, recursive=False)
    _observer.start()
    _newMsg.wait(55)

def main():
    form = cgi.FieldStorage()
    messageSubmitted = form.getvalue("message", "")
    poll = form.getvalue("poll", "")
    name = form.getvalue("name", "")
    active = form.getvalue("active", "")
    activity = form.getvalue("activity", "")

    if messageSubmitted:
        msg = Message()
        msg.user = name
        msg.message = form.getvalue("message", "")
        msg.date = today
        storeMessage(msg)

    if activity and len(name.strip()) > 0:
        u = UserActivity(name = name, active = active, date = datetime.utcnow())
        logUserActivity(u)

    if poll:
        waitForNewMessages()

    printMessages()

if __name__ == "__main__":
    main()
    

