#!/usr/bin/env python

import paste
from bottle import run, template, static_file, request, post, get, put, hook, response, route

import os, json
from datetime import datetime, timedelta
from chatModels import (ChatApiResponse, ApiResult, MessageEncoder, Message,
    UserActivity, getMessageArrayFromJson)
from time import time, sleep
#from chat_s3 import getWebMessagesForKey, storeMessages, deleteMessagesForKey, getDayKeyListFromS3, getMessagesForKey
from chat_db import storeSingleMessage, getMessagesForHashKey
from threading import Event

_secondsToWait = 29 #seconds to pause the thread waiting for updates
_todaysKey = datetime.utcnow().strftime("%Y_%m_%d")
_users, _messages = [], []
_newMsg = Event()

def storeMessage(msg):
    _messages.append(msg)
    ua = UserActivity(name = msg.user, active = True, date = msg.date)
    logUserActivity(ua)
    storeSingleMessage(_todaysKey, msg)

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

    today = datetime.utcnow().strftime("%Y_%m_%d")

    global _todaysKey
    global _messages
    if len(_messages) == 0:
        _messages = getMessagesForHashKey(_todaysKey)
    elif _todaysKey != today:
        _todaysKey = today
        _messages = []

    users = removeInactiveUsers(_users)
    chatResponse = ChatApiResponse(messages = _messages, users = _users)
    result.data = chatResponse

    jsonStr = json.dumps(result, cls=MessageEncoder)

    return jsonStr

def getJsonSuccessResponse():
    result = ApiResult(success = True)
    return json.dumps(result, cls = MessageEncoder)

@get('/')
def index():
    return static_file("index.html", 'static')

@route('/static/:path#.+#', name='static')
def static(path):
    response.set_header('Cache-Control', 'no-cache')
    return static_file(path, root='static')

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
    _newMsg.clear()
    _newMsg.wait(_secondsToWait)

    return getMessages()

@post('/readmessages')
def readMessages():
    return getMessages()

@get('/clear')
def clear():
    deleteMessagesForKey(_todaysKey)
    _messages = []
    return "Todays messages deleted"

@get('/history')
def history():
    keyList = getDayKeyListFromS3()
    listStr = ""
    for k in keyList:
        listStr += "<a href='/history/{0}'>{0}</a><br/>".format(k)

    return listStr

@get('/history/:s3Key')
def historyForKey(s3Key):
    messageList = getMessagesForKey(s3Key)
    response.set_header('Content-Type', 'application/json')
    return json.dumps(getMessageArrayFromJson(messageList), cls=MessageEncoder)


if __name__ == "__main__":
    run(server='paste', reloader=True, port=5000)

