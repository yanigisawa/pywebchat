#!/usr/bin/python

# Long Polling Example:
# http://techoctave.com/c7/posts/60-simple-long-polling-example-with-javascript-and-jquery
## Actor 1 in module1.py
##

#import cgi, cgitb; cgitb.enable();

import paste
from bottle import run, template, static_file, request, post, get, put

import os, json
from datetime import datetime, timedelta
from collections import namedtuple
from chatModels import (ChatApiResponse, ApiResult, MessageEncoder, Message, FileChangeHandler,
    UserActivity, ChatLineType, ChatLogLine, _newMsg, _observer, fileName)
from sched import scheduler
from time import time, sleep


_secondsToWait = 55 #seconds to pause the thread waiting for updates
_messages, _users = [], []
_observerIsStarted = False

def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

def storeMessage(msg):
    global _messages
    _messages.append(msg)
    ua = UserActivity(name = msg.user, active = True, date = msg.date)
    logUserActivity(ua)
    _newMsg.set()

def logUserActivity(userActivity):
    global _users
    if userActivity in _users:
        for user in _users:
            if userActivity == user:
                user.active = userActivity.active
                user.date = userActivity.date
                break
    else:
        _users.append(userActivity)
    _newMsg.set()

    #line = ChatLogLine(logType = ChatLineType.UserActivity, obj = userActivity)
    #with open(fileName, 'a') as f:
    #    s = "{0}\n".format(json.dumps(line, cls=MessageEncoder))
    #    f.write(s)

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

def getMessages():
    result = ApiResult()
    result.success = True
    global _users
    _users = removeInactiveUsers(_users)
    chatResponse = ChatApiResponse(messages = _messages, users = _users)
    result.data = chatResponse

    return json.dumps(result, cls=MessageEncoder)

def getJsonSuccessResponse():
    result = ApiResult(success = True)
    return json.dumps(result, cls = MessageEncoder)

def waitForNewMessages():
    event_handler = FileChangeHandler()
    path = os.getcwd()
    path = os.path.join(path, "chat")
    _observer.schedule(event_handler, path, recursive=False)
    global _observerIsStarted
    if not _observerIsStarted: 
        _observer.start()
        _observerIsStarted = True

@get('/')
def index():
    return static_file("index.html", ".")

@get('/js')
def javaScript():
    return static_file("chatClient.js", ".")

@get('/hotkeyjs')
def hotKeys():
    return static_file("jquery.hotkeys.js", ".")

@get('/img/:imageName')
def serveImages(imageName):
    return static_file(imageName, "./img")

@put('/newmessage')
def newMessage():
    messageSubmitted = request.POST.get("message", "").strip()
    name = request.POST.get("name", "").strip()

    if messageSubmitted:
        msg = Message()
        msg.user = name
        msg.message = messageSubmitted
        msg.date = datetime.utcnow()
        storeMessage(msg)

    return getJsonSuccessResponse()

@put('/useractivity')
def userActivity():
    active = request.POST.get("active", "").strip()
    activity = request.POST.get("activity", "").strip()
    name = request.POST.get("name", "").strip()
    if activity and len(name) > 0:
        u = UserActivity(name = name, active = active, date = datetime.utcnow())
        logUserActivity(u)

    return getJsonSuccessResponse()

@post('/poll')
def poll():
    #if not _observerIsStarted:
    #    waitForNewMessages()

    _newMsg.clear()
    _newMsg.wait(_secondsToWait)

    return getMessages()

@post('/readmessages')
def readMessages():
    return getMessages()

if __name__ == "__main__":
    #run(server='paste', reloader=True)
    run(server='paste', host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

