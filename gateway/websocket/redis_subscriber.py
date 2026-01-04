import json
import threading
import redis
from websocket.socket import socketio

# from gateway.log_logic.log_util import

REDIS_CLIENT = redis.Redis.from_url(
    "redis://localhost:6379/1",
    decode_responses=True
)

def listen_for_results():
    try:
        pubsub = REDIS_CLIENT.pubsub()
        pubsub.subscribe("playlist:completed")

        for message in pubsub.listen():
            if message["type"] != "message":
                continue

            payload = json.loads(message["data"])
            request_id = payload["request_id"]
            result = payload["result"]

            socketio.emit(
                "playlist_done",
                result,
                room=request_id
            )
    except Exception as e:
        # log something
        raise e


def start_listener():  # thread for gateway to listen for playlist generation completes
    thread = threading.Thread(target=listen_for_results, daemon=True)
    thread.start()