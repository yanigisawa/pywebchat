#!/usr/bin/env python
# encoding: utf-8

import chat
from time import sleep
from chatModels import Message, getMessageArrayFromJson
from datetime import datetime
from chat_s3 import getMessagesForKey, getDayKeyListFromS3
from chat_db import storeSingleMessage, getMessagesForHashKey

def main():
    keys = getDayKeyListFromS3()

    for key in keys:
        msgs = getMessageArrayFromJson(getMessagesForKey(key))

        db_msgs = getMessagesForHashKey(key)
        for msg in db_msgs:
            if msg in msgs:
                msgs.remove(msg)

        sleepCounter = 1
        for m in msgs:
            if sleepCounter % 10 == 0:
                print("sleep for 10 seconds")
                sleep(10) # Throttle back on the posts to not overload throughput

            storeSingleMessage(key, m)
            sleepCounter += 1


if __name__ == '__main__':
    main()
    
    
