#!/Users/yanigisawa/.virtualenvs/pywebchat/bin/python

# Long Polling Example:
# http://techoctave.com/c7/posts/60-simple-long-polling-example-with-javascript-and-jquery
## Actor 1 in module1.py
##

import cgi;
import cgitb; cgitb.enable();

javascriptFile = "chatClient.js"


import os.path, time
print("Content-type: application/text")
print(os.linesep)

with open (javascriptFile, 'r') as f:
    print(f.read())

