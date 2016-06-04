from chatModels import Message, MessageEncoder, getMessageArrayFromJson
import json
from datetime import datetime
import os
import boto.dynamodb2
from boto.dynamodb2.fields import HashKey, RangeKey
from boto.dynamodb2.table import Table
from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.exceptions import JSONResponseError
import dateutil.parser

env = "test"
if os.environ.get("ENVIRONMENT"):
    env = os.environ.get("ENVIRONMENT")

_message_table = "{0}.webchat_messages".format(env)
_foundDynamoDbLocal = False

def confirmDynamoDbLocalIsRunning(host, port):
    global _foundDynamoDbLocal
    if _foundDynamoDbLocal: 
        return

    print('_foundDynamoDbLocal is {0}, contining'.format(_foundDynamoDbLocal))

    try:
        import telnetlib
        telnetlib.Telnet(host, port, 1)
        _foundDynamoDbLocal = True
    except Exception as e:
        print("###################")
        print("Could not conect to dynamodb at {0}:{1}".format(host, port))
        print("###################")

        raise e

def getMessageTable():
    conn = None
    if os.environ.get('DEVELOPER_MODE'):
        host, port = 'localhost', 8000
        confirmDynamoDbLocalIsRunning(host, port)
        conn = DynamoDBConnection(
            host = host,
            port = port,
            aws_access_key_id = 'unit_test',
            aws_secret_access_key = 'unit_test',
            is_secure = False)
    else:
        conn = DynamoDBConnection()

    try:
        msg_table_desc = conn.describe_table(_message_table)
        msg_table = Table(_message_table, connection = conn)
    except JSONResponseError as e:
        # Only handle the ResourceNotFoundException here
        if e.error_code != 'ResourceNotFoundException':
            raise e

        msg_table = Table.create(_message_table, 
            schema=[
                HashKey('date_string'),
                RangeKey('date')
            ], throughput = {
                'read' : 5,
                'write' : 5
            },
            connection = conn)

    while not msg_table.describe()['Table']['TableStatus'] == "ACTIVE":
        from time import sleep
        sleep(1)

    return msg_table

def getDynamoDBMessage(message):
    dyn_msg = {}
    dyn_msg['date'] = message.date.isoformat()
    dyn_msg['message'] = message.message
    dyn_msg['user'] = message.user
    dyn_msg['room'] = message.room

    return dyn_msg

def getMessageFromDynObject(dyn_dict):
    """Converts a DynoDB object back into a Message python object

    :dyn_dict: DynamoDB stored object
    :returns: Message python object

    """
    return Message(
            user = dyn_dict['user']
            , date = dateutil.parser.parse(dyn_dict['date'])
            , message = dyn_dict['message']
            , filterHTML = False
            , room = dyn_dict['room'])

def storeSingleMessage(date_string, message):
    msg_table = getMessageTable()
    dyn_dict = getDynamoDBMessage(message)
    dyn_dict['date_string'] = date_string
    msg_table.put_item(data = dyn_dict)

def storeMessageArray(date_string, messages):
    msg_table = getMessageTable()
    dyn_dict = {}
    write_count = 0
    for msg in messages:
        dyn_dict = getDynamoDBMessage(msg)
        dyn_dict['date_string'] = date_string
        msg_table.put_item(data = dyn_dict)
        write_count += 1

    return write_count

def getMessagesSince(key, date):
    msg_table = getMessageTable()
    filtered_msgs = msg_table.query(date_string__eq = key, date__gte = date.isoformat())
    
    return [getMessageFromDynObject(x) for x in filtered_msgs]

def getMessagesForHashKey(key):
    msg_table = getMessageTable()

    filtered_msgs = sorted([getMessageFromDynObject(x) for x in msg_table.query(date_string__eq = key)])

    return filtered_msgs
    
def getDayKeyList():
    msg_table = getMessageTable()
    all_msgs = list(msg_table.scan())
    keys = []
    for m in all_msgs:
        if m['date_string'] not in keys:
            keys.append(m['date_string'])

    return sorted(keys)


