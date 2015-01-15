#!/usr/bin/env python
# encoding: utf-8

import chat
from time import sleep
from chatModels import Message
from datetime import datetime

def main():
    for i in range(10000):
        m = Message(user = "loadUser{0}".format(i),
                date = datetime.utcnow(),
                message = "load test message: {0}".format(i))

        print("{0} - Store New Message".format(i))
        chat.storeMessage(m)
        print("{0} - Sleeping".format(i))

        sleep(3)



if __name__ == '__main__':
    main()
    
    
