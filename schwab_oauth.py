"""
Exchange a Schwab OAuth authorization code for access/refresh tokens.

Setup:
  1. Copy .env.example to .env and fill in your Schwab app credentials.
  2. Run the script, follow the printed authorize URL, log in and approve.
  3. Paste the full URL you land on after approving when prompted.

Never commit real credentials or the resulting schwab_tokens.json — both
are already excluded via .gitignore.
"""

import base64
import json
import os
from urllib.parse import parse_qs, urlencode, urlparse, unquote

import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

CLIENT_ID = os.environ["SCHWAB_CLIENT_ID"]
CLIENT_SECRET = os.environ["SCHWAB_CLIENT_SECRET"]
REDIRECT_URI = os.environ.get("SCHWAB_REDIRECT_URI", "https://127.0.0.1")

AUTHORIZE_URL = "https://api.schwabapi.com/v1/oauth/authorize"
TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"
TOKEN_FILE = "schwab_tokens.json"


def build_authorize_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
    }
    return f"{AUTHORIZE_URL}?{urlencode(params)}"


def exchange_code_for_token(redirect_url):
    parsed = urlparse(redirect_url)
    code = unquote(parse_qs(parsed.query)["code"][0])

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    resp = requests.post(TOKEN_URL, headers=headers, data=data)

    if resp.status_code == 200:
        tokens = resp.json()
        print("SUCCESS")
        print(json.dumps(tokens, indent=2))
        with open(TOKEN_FILE, "w") as f:
            json.dump(tokens, f, indent=2)
        return tokens
    else:
        print(f"FAILED: {resp.status_code}")
        print(resp.text)
        return None


if __name__ == "__main__":
    print("Authorize URL:")
    print(build_authorize_url())
    redirect_response_url = input(
        "\nPaste the full redirect URL you landed on after approving: "
    ).strip()
    exchange_code_for_token(redirect_response_url)
