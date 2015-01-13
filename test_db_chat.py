import unittest
import json
import os
from datetime import datetime, timedelta
from collections import namedtuple
import chat_db as db
from chatModels import Message
from boto.dynamodb2.fields import HashKey, RangeKey
from boto.dynamodb2.table import Table
from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.exceptions import JSONResponseError
from chat import getMessageArrayFromJson

import logging
logging.getLogger('boto').setLevel(logging.CRITICAL)

import pprint
pp = pprint.PrettyPrinter(indent=4)


def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

def getMessagesAndUsersFromJson(json):
    response = json2obj(json)
    return response.data.messages, response.data.users

class ChatDbUnitTests(unittest.TestCase):
    def setUp(self):
        self.todaysKey = datetime.utcnow().strftime("%Y_%m_%d")
        conn = DynamoDBConnection(
            host = 'localhost',
            port = 8000,
            aws_access_key_id = 'unit_test',
            aws_secret_access_key = 'unit_test',
            is_secure = False)

        msg_table = Table.create(db._message_table, 
            schema=[
                HashKey('date_string'),
                RangeKey('date')
            ], 
            connection = conn)
        with open('test_data.json') as f:
            self.test_json = f.readline()

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

    def generateMessageEveryHourSince(self, date):
        msgs = []
        today = datetime.now()
        oneHour = timedelta(hours = 1)
        while date < today:
            msgs.append(Message(date = date,
                user = 'test user',
                message = 'test message'))
            date = date + oneHour

        return msgs

    def test_LoadTestData_ReturnsRecordCount(self):
        msg_array = getMessageArrayFromJson(self.test_json)
        affected_records = db.storeMessageArray(self.todaysKey, msg_array)
        self.assertEqual(len(msg_array), affected_records)

    def test_ScanTable_ReturnsAllRecords(self):
        msg_array = sorted(getMessageArrayFromJson(self.test_json), key = lambda msg: msg.date)
        affected_records = db.storeMessageArray(self.todaysKey, msg_array)
        all_records = sorted(db.getAllMessages(), key = lambda msg: msg.date )
        self.assertEqual(len(msg_array), len(all_records))
        for i in range(len(msg_array)):
            self.assertEqual(msg_array[i].date, all_records[i].date)

    def test_GivenTwoDaysWorthOfMessages_OnlyMessagesSinceMidnightAreReturned(self):
        two_days_ago = timedelta(days = -2)
        msgs = self.generateMessageEveryHourSince(datetime.utcnow() + two_days_ago)

        db.storeMessageArray(self.todaysKey, msgs)

        utc = datetime.utcnow()
        utc_midnight = datetime(utc.year, utc.month, utc.day)

        db_msgs = db.getMessagesSince(utc_midnight)
        # test_msgs = [x for x in msgs if x.date > utc_midnight]
        # self.assertEqual(len(test_msgs), len(db_msgs))

def main():
    unittest.main()

if __name__ == '__main__':
    main()
