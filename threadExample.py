
# Long Polling Example:
# http://techoctave.com/c7/posts/60-simple-long-polling-example-with-javascript-and-jquery
## Actor 1 in module1.py
##
from time import sleep
from datetime import datetime
import os
from threading import Event
from threading import Thread

today = datetime.now()
fileName = "chat/{0}-{1}-{2}.txt".format(today.year, today.month, today.day)

newMsg = Event()

def newMessage():
    with open(fileName, 'r') as f:
        for line in f:
            print(line)

def pushMessage(msg):
    with open(fileName, 'a') as f:
        f.write(msg + os.linesep)

    newMsg.set()

class thread1(Thread):
    def run(self):
        newMsg.wait(10)
        if newMsg.is_set():
            newMessage()
            newMsg.clear()
        else:
            print("Thread not set, exiting")

class thread2(Thread):
    def run(self):
        for x in xrange(10):
            #pushMessage("message from thread 2: {0}".format(x))
            sleep(2)

def main():
    thread1().start()
    thread2().start()

if __name__ == "__main__":
    main()
