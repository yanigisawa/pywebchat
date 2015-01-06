from datetime import datetime
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from threading import Thread
import os

_conn = S3Connection()

_bucketName = os.environ.get('AWS_BUCKET_NAME')
if not _bucketName:
    print("###### AWS_BUCKET_NAME NOT SET #####")

_testEnvKey = 'UNIT_TEST'

def postToS3Async(jsonMessages, s3_key):

    if os.environ.get(_testEnvKey):
        return

    bucket = _conn.get_bucket(_bucketName)
    key = bucket.get_key(s3_key)
    if key is None:
        key = Key(bucket)
        key.key = s3_key

    key.set_contents_from_string(jsonMessages)
    

def getWebMessagesForKey(s3_key):
    if os.environ.get(_testEnvKey):
        return ""

    bucket = _conn.get_bucket(_bucketName)
    key = bucket.get_key(s3_key)
    messages = ""
    if not key is None:
        messages = key.get_contents_as_string()

    return messages

def storeMessages(jsonMessages, s3_key):
    thread = Thread(target=postToS3Async, args=(jsonMessages,s3_key))
    thread.start()

def deleteMessagesForKey(s3_key):
    bucket = _conn.get_bucket(_bucketName)
    key = bucket.get_key(s3_key)
    messages = ""
    if not key is None:
        key.delete()

def getDayKeyListFromS3():
    if os.environ.get(_testEnvKey):
        return

    bucket = _conn.get_bucket(_bucketName)
    keyList = bucket.list()
    return [k.key for k in keyList]

def getMessagesForKey(s3KeyStr):
    if os.environ.get(_testEnvKey):
        return ""

    bucket = _conn.get_bucket(_bucketName)
    key = bucket.get_key(s3KeyStr)
    messages = ""
    if not key is None:
        messages = key.get_contents_as_string()

    return messages

