from app import app, socketio

# The port number should be the same as the front end
try:
    socketio.run(app, debug=True)
    # app.run(use_reloader=False, debug=True)
except:
    print("Some thing wrong!")