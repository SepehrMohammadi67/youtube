import httpx
import json
import asyncio
import socketio  # type:ignore

# کلاینت Socket.IO
sio = socketio.AsyncClient()


async def get_live_chat_messages():
    # اتصال به سرور Socket.IO
    await sio.connect("http://localhost:8000")
    print("✅ Connected to Socket.IO server")

    with open("youtube_tokens.json", "r", encoding="utf-8") as f:
        tokens = json.load(f)
    access_token = tokens["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    timeout = httpx.Timeout(30.0)

    async def safe_get(url, params=None, retries=3):
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    resp = await client.get(url, params=params, headers=headers)
                    return resp
            except Exception as e:
                print(f"⚠️ تلاش {attempt + 1}/{retries} ناموفق: {e}")
                await asyncio.sleep(5)
        return None

    broadcast_resp = await safe_get(
        "https://www.googleapis.com/youtube/v3/liveBroadcasts",
        params={"part": "snippet", "broadcastStatus": "active"}
    )
    if not broadcast_resp:
        return

    data = broadcast_resp.json()
    if "items" not in data or len(data["items"]) == 0:
        print("❌ هیچ استریم فعالی پیدا نشد.")
        return

    live_chat_id = data["items"][0]["snippet"]["liveChatId"]
    print(f"✅ Live Chat ID: {live_chat_id}\n")

    page_token = None

    while True:
        params = {
            "liveChatId": live_chat_id,
            "part": "snippet,authorDetails",
            "maxResults": 200,
        }
        if page_token:
            params["pageToken"] = page_token

        chat_resp = await safe_get(
            "https://www.googleapis.com/youtube/v3/liveChat/messages",
            params=params
        )
        if not chat_resp:
            await asyncio.sleep(5)
            continue

        chat_data = chat_resp.json()

        for item in chat_data.get("items", []):
            author = item["authorDetails"]["displayName"]
            message = item["snippet"]["displayMessage"]
            print(f"{author}: {message}")

            # 🎯 ارسال مستقیم به Socket.IO سرور
            await sio.emit("new_message", {"author": f"{author}", "message": message})

        page_token = chat_data.get("nextPageToken")
        delay = chat_data.get("pollingIntervalMillis", 5000) / 1000
        await asyncio.sleep(delay)


if __name__ == "__main__":
    asyncio.run(get_live_chat_messages())
