import eventlet
eventlet.monkey_patch()  # Without it: requests, redis, sockets can block; breaking concurrency

from __init__ import create_app, socketio

app = create_app()

if __name__ == "__main__":  # so that it's only ran as a script not a module (dunder needs to match).
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)  # websocket capabilities added to normal gateway server