from flask_socketio import SocketIO, emit, join_room

socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode="eventlet",
)

@socketio.on("subscribe")
def handle_subscribe(data):
    """
    Client sends:
    { request_id: "abc123" }
    """
    request_id = data.get("request_id")
    if not request_id:
        return

    join_room(request_id)
    emit("subscribed", {"request_id": request_id})