import os, sys
INTERP = os.path.join(os.environ['HOME'], '.venvs', 'pywebchat', 'bin', 'python')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())

from bottle import PasteServer
import chat

application = PasteServer(host='0.0.0.0')
#def application(environ, start_response):
#    return bottle.default_app().wsgi(environ, start_response)



