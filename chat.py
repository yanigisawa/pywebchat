#!/usr/bin/env python

import paste
from bottle import run, template, static_file, request, post, get, put, hook

import os, json
from datetime import datetime, timedelta
from collections import namedtuple
from chatModels import (ChatApiResponse, ApiResult, MessageEncoder, Message,
    UserActivity, ChatLineType, ChatLogLine, _newMsg)
from sched import scheduler
from time import time, sleep
from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
import transaction

_secondsToWait = 55 #seconds to pause the thread waiting for updates
_observerIsStarted = False
_zdb = {}
_todaysKey = datetime.utcnow().strftime("%Y_%m_%d")
_usersKey = "users"

def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

def storeMessage(msg):
    db = _zdb['root']
    if not db.has_key(_todaysKey):
        db[_todaysKey] = []
    db[_todaysKey].append(msg)
    ua = UserActivity(name = msg.user, active = True, date = msg.date)
    logUserActivity(ua)
    transaction.commit()
    _newMsg.set()

def logUserActivity(userActivity):
    db = _zdb['root']
    if not db.has_key(_usersKey):
        db[_usersKey] = []
    users = db[_usersKey]
    if userActivity in users:
        for user in users:
            if userActivity == user:
                user.active = userActivity.active
                user.date = userActivity.date
                break
    else:
        users.append(userActivity)
    db[_usersKey] = users
    transaction.commit()
    _newMsg.set()

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
    db = _zdb['root']
    if not db.has_key(_todaysKey):
        db[_todaysKey] = []

    messages = db[_todaysKey]

    if not db.has_key(_usersKey):
        db[_usersKey] = []

    users = removeInactiveUsers(db[_usersKey])
    chatResponse = ChatApiResponse(messages = messages, users = users)
    result.data = chatResponse

    return json.dumps(result, cls=MessageEncoder)

def getJsonSuccessResponse():
    result = ApiResult(success = True)
    return json.dumps(result, cls = MessageEncoder)

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
    open_db()
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
    open_db()
    active = request.POST.get("active", "").strip()
    activity = request.POST.get("activity", "").strip()
    name = request.POST.get("name", "").strip()
    if activity and len(name) > 0:
        u = UserActivity(name = name, active = active, date = datetime.utcnow())
        logUserActivity(u)

    return getJsonSuccessResponse()

@post('/poll')
def poll():

    _newMsg.clear()
    _newMsg.wait(_secondsToWait)

    #open_db()

    return getMessages()

@post('/readmessages')
def readMessages():
    open_db()
    return getMessages()

def open_db():
    global _zdb
    _zdb['storage'] = FileStorage("db/webChat.fs")
    _zdb['db'] = DB(_zdb['storage'])
    _zdb['connection'] = _zdb['db'].open()
    _zdb['root'] = _zdb['connection'].root()

@hook('after_request')
def close_db():

    print("after request")
    global _zdb
    if not _zdb.has_key('connection'):
        return
    transaction.commit()
    _zdb['connection'].close()
    _zdb['db'].close()
    _zdb['storage'].close()

if __name__ == "__main__":
    run(server='paste', reloader=True)

