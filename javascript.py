#!/usr/bin/python

import cgi;
import cgitb; cgitb.enable();

javascriptFile = "chatClient.js"

import os.path, time
print("Content-type: text/javascript")
print(os.linesep)

with open (javascriptFile, 'r') as f:
    print(f.read())

