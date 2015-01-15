import unittest
import json
import os
from datetime import datetime, timedelta
from collections import namedtuple
import chat_db as db
from chatModels import Message, MessageEncoder
from boto.dynamodb2.fields import HashKey, RangeKey
from boto.dynamodb2.table import Table
from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.exceptions import JSONResponseError
from chat_db import getMessageArrayFromJson

import logging
logging.getLogger('boto').setLevel(logging.CRITICAL)

import pprint
pp = pprint.PrettyPrinter(indent=4)


def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

def getMessagesAndUsersFromJson(json):
    response = json2obj(json)
    return response.data.messages, response.data.users

def generateMessageEveryHourSince(date):
    msgs = []
    oneHour = timedelta(hours = -1)
    keyDate = datetime.utcnow()
    while date < keyDate:
        msgs.append(Message(
            user = 'test user{0}'.format(keyDate.hour),
            date = keyDate,
            message = 'test message {0}'.format(keyDate.hour)))
        keyDate = keyDate + oneHour

    return msgs

class ChatDbUnitTests(unittest.TestCase):
    def setUp(self):
        self.todaysKey = datetime.utcnow().strftime("%Y_%m_%d")
        conn = DynamoDBConnection(
            host = 'localhost',
            port = 8000,
            aws_access_key_id = 'unit_test',
            aws_secret_access_key = 'unit_test',
            is_secure = False)

        try:
            msg_table = Table.create(db._message_table, 
                schema=[
                    HashKey('date_string'),
                    RangeKey('date')
                ], 
                connection = conn)
        except JSONResponseError as e:
            conn.delete_table(db._message_table)
            #print("Could not create test table: {0}".format(e))

        with open('test_data.json') as f:
            self.test_json = f.readline()

        with open('test2_data.json', 'w') as f:
            utc = datetime.utcnow()
            utc_midnight = datetime(utc.year, utc.month, utc.day)
            msgs = generateMessageEveryHourSince(utc_midnight)
            f.write(json.dumps(msgs, cls = MessageEncoder))

    def tearDown(self):
        """Any tear down steps post test run.

        :returns: TODO

        """
        conn = DynamoDBConnection(
            host = 'localhost',
            port = 8000,
            aws_access_key_id = 'unit_test',
            aws_secret_access_key = 'unit_test',
            is_secure = False)

        conn.delete_table(db._message_table)


    def test_LoadTestData_ReturnsRecordCount(self):
        msg_array = getMessageArrayFromJson(self.test_json)
        affected_records = db.storeMessageArray(self.todaysKey, msg_array)
        self.assertEqual(len(msg_array), affected_records)

    def test_GivenTwoDaysWorthOfMessages_OnlyMessagesSinceMidnightAreReturned(self):
        two_days_ago = timedelta(days = -2)
        msgs = generateMessageEveryHourSince(datetime.utcnow() + two_days_ago) 

        db.storeMessageArray(self.todaysKey, msgs)

        utc = datetime.utcnow()
        utc_midnight = datetime(utc.year, utc.month, utc.day)

        db_msgs = sorted(db.getMessagesSince(self.todaysKey, utc_midnight))
        test_msgs = sorted([x for x in msgs if x.date > utc_midnight])
        self.assertEqual(len(test_msgs), len(db_msgs))
        for i in range(len(db_msgs)):
            self.assertEqual(db_msgs[i].date, test_msgs[i].date) 
            self.assertEqual(db_msgs[i].user, test_msgs[i].user)
            self.assertEqual(db_msgs[i].message, test_msgs[i].message)

    def test_GivenIsoDateWithoutMicroseconds_DateCanStillBeParsed(self):
        utc = datetime.utcnow()
        utc_midnight = datetime(utc.year, utc.month, utc.day)
        m = generateMessageEveryHourSince(utc_midnight)
        getMessageArrayFromJson(json.dumps(m, cls = MessageEncoder))

    def test_GivenTwoDaysWorthOfMessages_ReturnAllOfCurrentDaysMessages(self):
        two_days_ago = timedelta(days = -2)
        msgs = sorted(generateMessageEveryHourSince(datetime.utcnow() + two_days_ago), key = lambda msg: msg.date)

        db.storeMessageArray(self.todaysKey, msgs)

        db_msgs = sorted(db.getMessagesForHashKey(self.todaysKey), key = lambda msg: msg.date)
        self.assertEqual(len(msgs), len(db_msgs))
        for i in range(len(db_msgs)):
            self.assertEqual(db_msgs[i].date, msgs[i].date)
            self.assertEqual(db_msgs[i].user, msgs[i].user)
            self.assertEqual(db_msgs[i].message, msgs[i].message)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
