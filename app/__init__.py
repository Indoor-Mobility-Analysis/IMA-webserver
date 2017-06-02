# -*- coding: UTF-8 -*-
from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo

from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
mongo = PyMongo(app)
# flask_cors: Cross Origin Resource Sharing (CORS), making cross-origin AJAX possible.
CORS(app)
async_mode = None
socketio = SocketIO(app, async_mode=async_mode)
thread = None




from app.routes import index
