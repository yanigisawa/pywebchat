import os, json, dateutil.parser, re
from datetime import datetime, timedelta
from collections import namedtuple

class Message(object):
    def __init__(self, user = None, message = None, date = datetime.utcnow(), filterHTML = True):
        self.filterHTML = filterHTML
        self.user = user
        self.message = message
        self.date = date

    @staticmethod
    def replaceUrlsWithLinks(msg):
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', msg)
        newMsg = ""
        if len(urls) > 0:
            for u in urls:
                newMsg = msg.replace(u, "<a href=\"{0}\" target=\"_blank\" tabindex=\"-1\">{0}</a>".format(u))
        else:
            newMsg = msg

        return newMsg

    @property
    def message(self): 
        return self.m_message

    @message.setter
    def message(self, value):
        if value != None: 
            if self.filterHTML:
                self.m_message = value.replace("<", "&lt;").replace(">", "&gt;")
                self.m_message = Message.replaceUrlsWithLinks(self.m_message)
            else: 
                self.m_message = value

    def __repr__(self):
        return "{0} - {1}: {2}".format(self.date, self.user, self.message)

class UserActivity(object):
    def __init__(self, name = None, active = False, date = None):
        self.name = name

        if isinstance(active, str):
            self.active = (active == "true")
        else:
            self.active = active

        self.date = date

    @property
    def date(self):
        return self.m_date

    @date.setter
    def date(self, value):
        if isinstance(value, datetime):
            self.m_date = value 
        elif value != None:
            self.m_date = dateutil.parser.parse(value)
        else:
            self.m_date = None

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return "{0} - {1} - {2}".format(self.name, self.active, self.date)

class ChatApiResponse(object):
    def __init__(self, messages = [], users = []):
        self.messages = messages
        self.users = users

class ApiResult(object):
    def __init__(self, success = True, message = None, data = None):
        self.success = success
        self.message = message
        self.data = data

class MessageEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, Message):
            x = {}
            x["filterHTML"], x["user"], x["message"] = obj.filterHTML, obj.user, obj.message
            x["date"] = obj.date
            return x

        if isinstance(obj, ApiResult):
            return obj.__dict__

        if isinstance(obj, UserActivity):
            x = {}
            x["name"], x["date"], x["active"] = obj.name, obj.date, obj.active
            return x

        if isinstance(obj, ChatApiResponse):
            return obj.__dict__

        if isinstance(obj, ChatLineType):
            return obj.__dict__

        if isinstance(obj, ChatLogLine):
            return obj.__dict__

        return super(MessageEncoder, self).default(obj)

def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

def getMessageArrayFromJson(jsonString):
    dictArray = json2obj(jsonString)
    arr = []
    for item in dictArray:
        m = Message(
            user = item.user
            , date = datetime.strptime(item.date, "%Y-%m-%dT%H:%M:%S.%f")
            , message = item.message
            , filterHTML = False)
        arr.append(m)

    return arr

class ChatLineType(object):
    UserActivity = 1
    Message = 2

class ChatLogLine(object):
    def __init__(self, logType = ChatLineType.Message, obj = None):
        self.logType = logType
        self.obj = obj
