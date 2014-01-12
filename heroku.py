from bottle import run, template, static_file, request, post, get, put, hook
import chat
import paste
import os

if __name__ == "__main__":
    run(server='paste', host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

