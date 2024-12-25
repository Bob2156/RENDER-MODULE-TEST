import os
import requests
import logging
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import yfinance as yf
from bs4 import BeautifulSoup

def verify_signature(req):
    signature = req.headers.get("X-Signature-Ed25519")
    timestamp = req.headers.get("X-Signature-Timestamp")
    body = req.data

    if not signature or not timestamp:
        raise ValueError("Missing signature or timestamp")

    public_key = VerifyKey(bytes.fromhex(os.getenv("DISCORD_PUBLIC_KEY")))
    try:
        public_key.verify(f"{timestamp}{body.decode()}".encode(), bytes.fromhex(signature))
    except BadSignatureError:
        raise ValueError("Invalid request signature")

def send_followup_response(interaction_token, payload):
    url = f"https://discord.com/api/v10/webhooks/{os.getenv('DISCORD_APP_ID')}/{interaction_token}"
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        logging.info("Successfully sent follow-up response.")
    else:
        logging.error(f"Failed to send follow-up response: {response.status_code} {response.text}")

def fetch_sma_and_volatility():
    try:
        ticker = yf.Ticker("^GSPC")
        data = ticker.history(period="1y")
        if data.empty or len(data) < 220:
            raise ValueError("Insufficient data to calculate SMA or volatility.")

        sma_220 = round(data['Close'].rolling(window=220).mean().iloc[-1], 2)
        last_close = round(data['Close'].iloc[-1], 2)

        recent_data = data[-30:]
        daily_returns = recent_data['Close'].pct_change().dropna()
        volatility = round(daily_returns.std() * (252**0.5) * 100, 2)
        return last_close, sma_220, volatility
    except Exception as e:
        raise ValueError(f"Error fetching SMA and volatility: {e}")

def fetch_treasury_rate():
    try:
        URL = "https://www.cnbc.com/quotes/US3M"
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, "html.parser")
        rate_element = soup.find("span", {"class": "QuoteStrip-lastPrice"})
        if rate_element:
            rate_text = rate_element.text.strip()
            if rate_text.endswith('%'):
                return round(float(rate_text[:-1]), 2)
        raise ValueError("Failed to fetch treasury rate.")
    except Exception as e:
        raise ValueError(f"Error fetching treasury rate: {e}")
