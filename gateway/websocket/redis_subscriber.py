import json
import threading
import redis
import time

from websocket.socket import socketio
from log_logic.log_util import redis_log

REDIS_CLIENT = redis.Redis.from_url(
    "redis://localhost:6379/1",
    decode_responses=True  # message sent as str not bytes
)

def listen_for_results():
    redis_log(
        20,
        "redis_listener_started",
        channel="playlist:completed",
    )

    while True:
        try:
            """
            opens a push-based pubsub redis connection purely for listening
            no key value pairs are stored in redis and instead they are pushed to listeners (fire-and-forget)
            """

            pubsub = REDIS_CLIENT.pubsub(ignore_subscribe_messages=True)
            pubsub.subscribe("playlist:completed", "playlist:progress")

            for message in pubsub.listen():  # blocks/sleeps until a message arrives
                try:
                    payload = json.loads(message["data"])
                    request_id = payload.get("request_id")

                    if not request_id or not result:
                        redis_log(
                            30,
                            "redis_message_invalid",
                            raw_message=message.get("data"),
                        )
                        continue

                    if message["channel"] == "playlist:progress":
                        step = payload.get("step")

                        socketio.emit(
                            "playlist_progress",
                            step,
                            room=request_id,
                        )
                    elif message["channel"] == "playlist:completed":
                        result = payload.get("result")

                        socketio.emit(
                            "playlist_done",
                            result,
                            room=request_id,
                        )

                except json.JSONDecodeError:
                    redis_log(
                        30,
                        "redis_message_decode_failed",
                        raw_message=message.get("data"),
                    )

                except Exception as e:
                    redis_log(
                        30,
                        "websocket_emit_failed",
                        request_id,
                        error=f"{e.__class__.__name__}: {str(e)}",
                    )

        except Exception as e:
            redis_log(
                50,
                "redis_listener_crash_retry",
                error=f"{e.__class__.__name__}: {str(e)}",
            )

            time.sleep(3)


def start_listener():  # thread for gateway to listen for playlist generation completes
    thread = threading.Thread(target=listen_for_results, daemon=True)
    thread.start()