# chat.py
import json

from flask import request

from app.models import db, Message, User

sockets = {}  # user_id -> websocket


def register_chat_routes(sock):

    @sock.route("/ws/chat")
    def chat(ws):
        try:
            user_id = int(request.args.get("user_id"))
        except (TypeError, ValueError):
            ws.close()
            return

        sockets[user_id] = ws
        print(f"[WebSocket] User {user_id} connected.")

        # 💬 向当前用户发送历史消息（包含收发）
        all_messages = (
            Message.query.filter(
                (Message.sender_id == user_id) | (Message.receiver_id == user_id)
            )
            .order_by(Message.timestamp.asc())
            .all()
        )

        user_cache = {user_id: User.query.get(user_id).username}
        for msg in all_messages:
            if msg.sender_id not in user_cache:
                user_cache[msg.sender_id] = User.query.get(msg.sender_id).username
            direction = "outgoing" if msg.sender_id == user_id else "incoming"
            ws.send(
                json.dumps(
                    {
                        "from": user_cache[msg.sender_id],
                        "from_id": msg.sender_id,
                        "to_id": msg.receiver_id,
                        "message": msg.content,
                        "timestamp": msg.timestamp.strftime("%H:%M"),
                        "direction": direction,
                    }
                )
            )

        while True:
            try:
                data = ws.receive()
                if data is None:
                    break
                print("[Received]", data)

                payload = json.loads(data)
                to = int(payload["to"])
                content = payload["message"]

                msg = Message(sender_id=user_id, receiver_id=to, content=content)
                db.session.add(msg)
                db.session.commit()

                sender_user = User.query.get(user_id)
                outgoing_msg = json.dumps(
                    {
                        "from": sender_user.username,
                        "from_id": user_id,
                        "to_id": to,
                        "message": content,
                        "timestamp": msg.timestamp.strftime("%H:%M"),
                        "direction": "outgoing",
                    }
                )

                ws.send(outgoing_msg)

                if to in sockets:
                    sockets[to].send(
                        json.dumps(
                            {
                                "from": sender_user.username,
                                "from_id": user_id,
                                "to_id": to,
                                "message": content,
                                "timestamp": msg.timestamp.strftime("%H:%M"),
                                "direction": "incoming",
                            }
                        )
                    )
            except Exception as e:
                print("[WebSocket Error]", e)
                break

        print(f"[WebSocket] User {user_id} disconnected.")
        sockets.pop(user_id, None)
