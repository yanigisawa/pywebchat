#!/usr/bin/env sh
java -Djava.library.path=./dynamodb_local/DynamoDBLocal_lib -jar ./dynamodb_local/DynamoDBLocal.jar -port 8000 -dbPath /Users/jalexander/src/pywebchat/dynamodb_local/db 
