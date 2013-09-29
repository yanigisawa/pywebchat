#!/usr/bin/python

# Long Polling Example:
# http://techoctave.com/c7/posts/60-simple-long-polling-example-with-javascript-and-jquery
## Actor 1 in module1.py
##

import cgi, cgitb; cgitb.enable();

import os, json
from datetime import datetime, timedelta
from collections import namedtuple
from chatModels import ChatApiResponse, ApiResult, MessageEncoder, Message, FileChangeHandler
from chatModels import UserActivity, ChatLineType, ChatLogLine, _newMsg, _observer, fileName

today = datetime.utcnow()

def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

def storeMessage(msg):
    line = ChatLogLine(obj = msg)
    with open(fileName, 'a') as f:
        s = "{0}\n".format(json.dumps(line, cls=MessageEncoder))
        f.write(s)

def logUserActivity(userActivity):
    line = ChatLogLine(logType = ChatLineType.UserActivity, obj = userActivity)
    with open(fileName, 'a') as f:
        s = "{0}\n".format(json.dumps(line, cls=MessageEncoder))
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
                lineObj = json2obj(line)
                if lineObj.logType == ChatLineType.Message:
                    m = lineObj.obj
                    msg = Message(user = m.user, date = m.date, filterHTML = False, message = m.message)
                    messages.append(msg)
                    users = setUserActivityDate(users, msg.user, msg.date)
                elif lineObj.logType == ChatLineType.UserActivity:
                    users = getModifiedUsersArray(users, lineObj.obj)

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
    

