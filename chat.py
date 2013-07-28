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
from threading import Event

import json
from collections import namedtuple

today = datetime.utcnow()
fileName = "chat/{0}-{1:02d}-{2:02d}.txt".format(today.year, today.month, today.day)

def log(msg):
    with open("chat/log.txt", 'a') as f:
        f.write(msg + "\n")

class Message(object):
    user = None
    message = None
    date = None

    def __str__(self):
        return "{0} - {1}: {2}".format(self.date, self.user, self.message)

class ApiResult(object):
    success = True
    message = None
    data = []

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

        return super(MessageEncoder, self).default(obj)

def storeMessage(msg):
    with open(fileName, 'a') as f:
        f.write("{0}\n".format(json.dumps(msg, cls=MessageEncoder)))

def printMessages():
    print("Content-type: application/json")
    print(os.linesep)

    messages = []
    
    if not os.path.isfile(fileName): return

    with open(fileName, 'r') as f:
        for line in f:
            m = json2obj(line.strip())
            msg = Message()
            msg.user = m.user
            msg.date = m.date
            msg.message = m.message
            messages.append(msg)

    result = ApiResult()
    result.success = True
    result.data = messages

    print(json.dumps(result, cls=MessageEncoder))
            
def waitForNewMessages():
    localTime = time.time()
    modifiedTime = os.path.getmtime(fileName)
    totalRequestTime = 0
    while modifiedTime < localTime and totalRequestTime < 25:
        time.sleep(1)
        totalRequestTime += 1
        modifiedTime = os.path.getmtime(fileName)

def main():
    form = cgi.FieldStorage()
    messageSubmitted = form.getvalue("message", "")
    poll = form.getvalue("poll", "")

    if messageSubmitted:
        msg = Message()
        msg.user = form.getvalue("name", "")
        msg.message = form.getvalue("message", "")
        msg.date = today
        storeMessage(msg)

    if poll:
        waitForNewMessages()

    printMessages()


if __name__ == "__main__":
    main()
    



#def newMessage():
#    with open(fileName, 'r') as f:
#        for line in f:
#            print(line)
#
#def pushMessage(msg):
#    with open(fileName, 'a') as f:
#        f.write(msg + os.linesep)
#
#    newMsg.set()
#
#class thread1(Thread):
#    def run(self):
#        newMsg.wait(10)
#        if newMsg.is_set():
#            newMessage()
#            newMsg.clear()
#        else:
#            print("Thread not set, exiting")
