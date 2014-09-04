#!/usr/bin/env python

import paste
from bottle import run, template, static_file, request, post, get, put, hook, response

import os, json
from datetime import datetime, timedelta
from collections import namedtuple
from chatModels import (ChatApiResponse, ApiResult, MessageEncoder, Message,
    UserActivity, ChatLineType, ChatLogLine)
from sched import scheduler
from time import time, sleep
from chat_s3 import getTodaysWebChatMessages, storeMessages, deleteTodaysMessages, getDayKeyListFromS3, getMessagesForKey
from threading import Event

_secondsToWait = 29 #seconds to pause the thread waiting for updates
_todaysKey = datetime.utcnow().strftime("%Y_%m_%d")
_messages, _users = [], []
_newMsg = Event()

def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

def storeMessage(msg):
    _messages.append(msg)
    ua = UserActivity(name = msg.user, active = True, date = msg.date)
    logUserActivity(ua)
    storeMessages(json.dumps(_messages, cls = MessageEncoder))
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

def getMessageArrayFromJson(jsonString):
    dictArray = json2obj(jsonString)
    arr = []
    for item in dictArray:
        m = Message(
            user = item.user
            , date = item.date
            , message = item.message
            , filterHTML = False)
        arr.append(m)

    return arr

def getMessages():
    result = ApiResult()
    result.success = True

    oneDay = timedelta(days = -1)
    oneDayAgo = datetime.utcnow() + oneDay

    global _messages
    if len(_messages) == 0:
        messageString = getTodaysWebChatMessages()
        if messageString.strip() != "":
            _messages = getMessageArrayFromJson(messageString)
    elif _messages[0].date.strftime("%Y_%m_%d") == oneDayAgo.strftime("%Y_%m_%d"):
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

    _newMsg.clear()
    _newMsg.wait(_secondsToWait)

    return getMessages()

@post('/readmessages')
def readMessages():
    return getMessages()

@get('/clear')
def clear():
    deleteTodaysMessages()
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

