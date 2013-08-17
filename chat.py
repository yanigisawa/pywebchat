#!/usr/bin/python

# Long Polling Example:
# http://techoctave.com/c7/posts/60-simple-long-polling-example-with-javascript-and-jquery
## Actor 1 in module1.py
##

import cgi;
import cgitb; cgitb.enable();

import time
from datetime import datetime
import os

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

from threading import Event

import json
from collections import namedtuple

today = datetime.utcnow()
fileName = "chat/{0}-{1:02d}-{2:02d}.txt".format(today.year, today.month, today.day)
userFileName = "chat/users_{0}-{1:02d}-{2:02d}.txt".format(today.year, today.month, today.day)

_newMsg = Event()
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

        u = os.path.join(currentDirectory, userFileName)
        if os.path.realpath(event.src_path) == u:
            _newMsg.set()

    def on_modified(self, event):
        pass

def log(msg):
    with open("chat/log.txt", 'a') as f:
        f.write(msg + "\n")

class Message(object):
    def __init__(self, user = None, message = None, date = None):
        self.user = user
        self.message = message
        self.date = date

    def __str__(self):
        return "{0} - {1}: {2}".format(self.date, self.user, self.message)


class User(object):
    def __init__(self, name = None, date = None):
        self.name = name
        self.date = date

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

        if isinstance(obj, User):
            return obj.__dict__

        if isinstance(obj, ChatApiResponse):
            return obj.__dict__

        return super(MessageEncoder, self).default(obj)

def storeMessage(msg):
    with open(fileName, 'a') as f:
        f.write("{0}\n".format(json.dumps(msg, cls=MessageEncoder)))

def getMessageArray():
    messages = []

    if os.path.isfile(fileName): 
        with open(fileName, 'r') as f:
            for line in f:
                m = json2obj(line.strip())
                msg = Message(user = m.user, date = m.date, message = m.message)
                messages.append(msg)

    return messages

def getUserArray():
    users = []

    if os.path.isfile(userFileName): 
        with open(userFileName, 'r') as f:
            for line in f:
                u = json2obj(line.strip())
                user = User(name = u.name, date = u.date)
                users.append(u)

    return users

def printMessages():
    print("Content-type: application/json")
    print(os.linesep)

    result = ApiResult()
    result.success = True
    chatResponse = ChatApiResponse(messages = getMessageArray(), users = getUserArray())
    result.data = chatResponse

    print(json.dumps(result, cls=MessageEncoder))

def logUserPoll(name):
    user = User(name = name, date = today)

    with open(userFileName, 'w') as f:
        f.write("{0}\n".format(json.dumps(user, cls=MessageEncoder)))

def waitForNewMessages():
    observer = Observer()
    event_handler = FileChangeHandler()
    path = os.getcwd()
    path = os.path.join(path, "chat")
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    _newMsg.wait(55)

def main():
    form = cgi.FieldStorage()
    messageSubmitted = form.getvalue("message", "")
    poll = form.getvalue("poll", "")
    name = form.getvalue("name", "")

    if messageSubmitted:
        msg = Message()
        msg.user = name
        msg.message = form.getvalue("message", "")
        msg.date = today
        storeMessage(msg)

    if poll:
        logUserPoll(name)
        waitForNewMessages()

    printMessages()

if __name__ == "__main__":
    main()
    

