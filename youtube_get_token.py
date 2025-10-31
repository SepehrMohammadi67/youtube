from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from urllib.parse import urlencode
import httpx
import os
import secrets
import json

app = FastAPI()

# === Google OAuth2 config ===
CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID", "551965573557-9mi64ln3680gfkcvtftse5cuq59eoeac.apps.googleusercontent.com")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET",
                          "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")
REDIRECT_URI = "http://localhost:8000/callback"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]

state_store = {}


@app.get("/", response_class=HTMLResponse)
async def index():
    state = secrets.token_urlsafe(16)
    state_store[state] = True

    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",  # برای گرفتن refresh_token
        "include_granted_scopes": "true",
        "state": state,
        "prompt": "consent"  # اجبار به نمایش صفحه‌ی تأیید
    }

    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + \
        urlencode(params)

    return f"""
    <html>
      <head><title>Login with YouTube</title></head>
      <body style='font-family:sans-serif; text-align:center; margin-top:50px'>
        <h2>Login with YouTube</h2>
        <a href="{auth_url}" 
           style="padding:10px 20px; background:#db4437; color:white; border-radius:8px; text-decoration:none;">
           Sign in with YouTube
        </a>
      </body>
    </html>
    """


@app.get("/callback", response_class=HTMLResponse)
async def callback(request: Request):
    params = dict(request.query_params)
    if "error" in params:
        return f"<h3>Login failed:</h3><pre>{params}</pre>"

    code = params.get("code")
    state = params.get("state")

    if not code or not state or state not in state_store:
        return "<h3>Invalid or missing state/code.</h3>"

    del state_store[state]

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(token_url, data=data)
    token_data = token_resp.json()

    if "access_token" not in token_data:
        return f"<h3>Token request failed:</h3><pre>{token_data}</pre>"

    with open("youtube_tokens.json", "w", encoding="utf-8") as f:
        json.dump(token_data, f, ensure_ascii=False, indent=4)

    html = f"""
    <h2>✅ YouTube OAuth success!</h2>
    <p>✅ Tokens saved in <b>youtube_tokens.json</b></p>
    <h3>Access Token Data</h3>
    <pre>{token_data}</pre>
    """

    return HTMLResponse(html)
