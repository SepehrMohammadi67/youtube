import socketio  # type:ignore
import uvicorn

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = socketio.ASGIApp(sio)


@sio.event
async def connect(sid, environ):
    print(f"✅ Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"❌ Client disconnected: {sid}")


# این تابع فقط برای debug
@sio.event
async def new_message(sid, data):
    author = data.get("author")
    message = data.get("message")
    print(f"📩 {author}: {message}")
    # ارسال برای تمام مرورگرها
    await sio.emit("new_message", data)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
