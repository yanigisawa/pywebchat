
devBucket = 'jra_dev_webchat'
prodBucket = 'jra_prod_webchat'
_bucketName = prodBucket

from datetime import datetime
_todaysKey = datetime.utcnow().strftime("%Y_%m_%d")

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from threading import Thread


_conn = S3Connection()

def postToS3Async(jsonMessages):
    bucket = _conn.get_bucket(_bucketName)
    key = bucket.get_key(_todaysKey)
    if key is None:
        key = Key(bucket)
        key.key = _todaysKey

    key.set_contents_from_string(jsonMessages)
    

def getTodaysWebChatMessages():
    bucket = _conn.get_bucket(_bucketName)
    key = bucket.get_key(_todaysKey)
    messages = ""
    if not key is None:
        messages = key.get_contents_as_string()

    return messages

def storeMessages(jsonMessages):
    thread = Thread(target=postToS3Async, args=(jsonMessages,))
    thread.start()

def deleteTodaysMessages():
    bucket = _conn.get_bucket(_bucketName)
    key = bucket.get_key(_todaysKey)
    messages = ""
    if not key is None:
        key.delete()

def getDayKeyListFromS3():
    bucket = _conn.get_bucket(_bucketName)
    keyList = bucket.list()
    return [k.key for k in keyList]

def getMessagesForKey(s3KeyStr):
    bucket = _conn.get_bucket(_bucketName)
    key = bucket.get_key(s3KeyStr)
    messages = ""
    if not key is None:
        messages = key.get_contents_as_string()

    return messages

