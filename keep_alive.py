"""
Render Keep-Alive Script
Pings the backend every 14 minutes to prevent cold starts (free tier limitation).
Run this script 24/7 on your local machine or deploy it to a free service like Replit.
"""

import requests
import time
from datetime import datetime

# Your Render backend URL
BACKEND_URL = "https://oracledota2.onrender.com/health"

# Ping interval (14 minutes in seconds)
PING_INTERVAL = 14 * 60  # 840 seconds

def ping_server():
    """Ping the server to keep it awake"""
    try:
        response = requests.get(BACKEND_URL, timeout=30)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if response.status_code == 200:
            print(f"[{timestamp}] ✅ Server is alive - Status: {response.json().get('status')}")
        else:
            print(f"[{timestamp}] ⚠️  Unexpected status code: {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"[{timestamp}] ⏱️  Timeout - Server might be waking up")
    except Exception as e:
        print(f"[{timestamp}] ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Render Keep-Alive Script Started")
    print(f"📡 Pinging {BACKEND_URL} every {PING_INTERVAL//60} minutes")
    print("⚠️  Keep this window open to prevent server sleep\n")
    
    while True:
        ping_server()
        time.sleep(PING_INTERVAL)
