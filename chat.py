#!/usr/bin/env python

import paste
from bottle import run, jinja2_template as template, static_file, request, post, get, put, hook, response, route

import os, json
from datetime import datetime, timedelta
from chatModels import (ChatApiResponse, ApiResult, MessageEncoder, Message,
    UserActivity, getMessageArrayFromJson)
from time import time, sleep
from chat_db import storeSingleMessage, getMessagesForHashKey, getDayKeyList
from threading import Event

_secondsToWait = 29 #seconds to pause the thread waiting for updates
_todaysKey = datetime.utcnow().strftime("%Y_%m_%d")
_users, _messages = [], []
_newMsg = Event()

def storeMessage(msg):
    _messages.append(msg)
    ua = UserActivity(name = msg.user, active = True, date = msg.date, room = msg.room)
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
                user.room = userActivity.room
                break
    else:
        _users.append(userActivity)
    _newMsg.set()

def getModifiedUsersArray(users, u):
    userObjectToReturn = UserActivity(name = u.name, active = u.active, date = u.date, room = u.room)

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

def getMessages(room = None):
    result = ApiResult()
    result.success = True

    today = datetime.utcnow().strftime("%Y_%m_%d")

    global _todaysKey
    global _messages
    if _todaysKey != today:
        _todaysKey = today
        _messages = []

    _messages = getMessagesForHashKey(_todaysKey)
    users = removeInactiveUsers(_users)
    room_users = []
    if room != None:
        room_messages = [x for x in _messages if x.room == room]
        room_users = [u for u in _users if u.room == room]

    chatResponse = ChatApiResponse(messages = room_messages, users = room_users)
    result.data = chatResponse

    jsonStr = json.dumps(result, cls=MessageEncoder)

    return jsonStr

def getJsonSuccessResponse():
    result = ApiResult(success = True)
    return json.dumps(result, cls = MessageEncoder)

@get('/')
def index():
    return static_file("index.html", 'static')

@get('/:room')
def room(room):
    return template("templates/room.tpl", { 'room' : room})

@route('/static/:path#.+#', name='static')
def static(path):
    response.set_header('Cache-Control', 'no-cache')
    return static_file(path, root='static')

@put('/:room/newmessage')
def newMessage(room):
    messageSubmitted = request.POST.get("message", "").strip()
    name = request.POST.get("name", "").strip()

    if messageSubmitted:
        msg = Message()
        msg.user = name
        msg.message = messageSubmitted
        msg.date = datetime.utcnow()
        msg.room = room
        storeMessage(msg)

    return getJsonSuccessResponse()

@put('/:room/useractivity')
def userActivity(room):
    active = request.POST.get("active", "").strip()
    activity = request.POST.get("activity", "").strip()
    name = request.POST.get("name", "").strip()
    if activity and len(name) > 0:
        u = UserActivity(name = name, active = active, date = datetime.utcnow(), room = room)
        logUserActivity(u)

    return getJsonSuccessResponse()

@post('/:room/poll')
def poll(room):
    _newMsg.clear()
    _newMsg.wait(_secondsToWait)

    return getMessages(room)

@post('/:room/readmessages')
def readMessages(room):
    return getMessages(room)

@get('/clear')
def clear():
    deleteMessagesForKey(_todaysKey)
    _messages = []
    return "Todays messages deleted"

@get('/history')
def history():
    keyList = getDayKeyList()
    return template("templates/history.tpl", { 'keyList' : keyList})

@get('/history/:key')
def historyForKey(key):
    messageList = getMessagesForHashKey(key)
    response.set_header('Content-Type', 'application/json')
    return json.dumps(messageList, cls=MessageEncoder)

@get('/test')
def generateLoremIpsum():
    with open('loremipsum.txt', 'r') as f:
        lineCount = 0
        for line in f:
            lineCount += 1
            msg = Message()
            if lineCount %3 != 0:
                msg.user = "test" 
                msg.room = "test1"
            else:
                msg.user = "test2"
                msg.room = "test2"
            msg.message = line
            msg.date = datetime.utcnow()
            storeMessage(msg)
    return "Test data generated"

if __name__ == "__main__":
    run(server='paste', reloader=True, port=5000)

