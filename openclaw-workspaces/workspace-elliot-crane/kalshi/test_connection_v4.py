#!/usr/bin/env python3
"""
Kalshi API Connection Test v4 - Check multiple API environments
"""

import base64
import datetime
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

API_KEY_ID = "adcd595f-ac7a-4d70-b6df-a859a2f3ac63"

PRIVATE_KEY_PEM = """-----BEGIN RSA PRIVATE KEY-----
MIIEoQIBAAKCAQEAtTsPAY837dUOdT4JWFH8KMsomqooJe1fWgWWaFxRZCsFIqeC
IjknFX4JplBI4NcRhs6RNCI+NzCaTLtHEJ58XNEDEJszoG9PNCyTKaJ+nxUhOOdf
M1oGE8fRcTrTlcBcnqpDsvYTBS/OFdZfencAeR8SMkCSY9LxMVLZIU1TqunPBOVP
GuZyOHL29nXukbWPUNtWrZav7Rz/LRVSgJWWp7o78TE2t2t9UJ3zvGuNBsh7f4/0
/0cb1T8Nk8vQiug/c2zmnkB5ldEuW4VUT/IOYMGKXxdszbRAtv8DCZuQMh+3dkeR
l2VbfH/F8Cvmhd3qONzZuWc7Iti1dJX+dndkSQIDAQABAoH/G+U+V8g/5egEAnWc
XCaLl3K6KLLXh2CCOoO6CquYz2qrNQXEXYxiWTvKNEMnVh8Z7vVWrYT5V8JaRu83
XIItKGVlMdnuySq6ehaTIp6dZPeYmVRZKFd8KkYjs9ZH6++p8HkT/scq3S21bI6x
O/3MGvEI1eQai/nZ3SVXRp5RMEyWXSHngkTuxmaL3sT2E7xyvY1P+5+GG2fHmNGc
OS7COo76ll8rRmkurJqCKNOH9CBKJwkyCfVfVqKIw2vCGYZd97GVXdoiyn+j0b4Z
ybuWVXhO0m2xoWsbDaIZDCnbrzhxPrLcLZGBTumfTMmqITk/dg+wdUxwxH9CGiru
Mo6BAoGBAMEu+3RInfcIF1fw97ZMujarjEKm/e9y3BBWHajqbIaDx5/7hMBiRLoN
UxOG/hhXSOZJh+nDOA4/JongojEVdzrUP/nwF64/Te4IwxcgAqPjSxIXJyDT9Ob9
6d7hA1fK942oGEGgzY+mEU70TYJrYqb4Jjby8axvIZuab5GTxaJhAoGBAPApGNaA
Gf3q59dsURCV1g7cELT6fGaof9nxPhbT/KF/x38DozeBfYHl3PJ0OD6VkrrYWBMZ
9N59dCP+UgJ58cZ9D1upAmqo27bpGbCw8IkmATo2eHgkBR/mtX5m73SiWooWlpO9
+tdP7Zn0GbXZAO4PN5eC8QigUjwqSwcNUNrpAoGBAK9CMF4Og0DZ1lOyCQkaEtYG
S/ksBrR1P7CSb9YO1uYyJ6i8RnNCs5cW/4d3sI3kof5KN0OcF/7Uy+HKKVreXozA
gkn9x34NcGXDDTqtj7efPTvsRVNC96uYL9RDzwSW3n9lQJxJhjQMNSer+6WWRqmz
9vdi8F2/dH32XcF0jpgBAoGAQ4h6+I6LQJDW4wgNf6lyyTju5cVuR/vn/+RLvmWc
K9nfwoLGWexq26VEzVULH+Y1nZ8KnUx2RD5o81onu5SI/XTbZb4P9OhI6JWB6OLI
sPhj7fe1RqtyWXcp4EKX4WdqKFyTuTX6HKPYP6uZsz4zeb4DtvJWT0Ot/Ec0U+ZV
r0kCgYAPIRVuO/UjE8/BNH2UtLUL/wqOQG9ue0N3ozjvbgjSVl6SqSCSerSnivgd
CxYnXR6t9SpBBGOMqNtYH20uhaZ/17jBuA2ARQkxmc/SlWjAdlHuc3aZPzLWK32q
Fjg1duDrPKul1ANybep9ttsHpqdlKmqbVUijA7gIXBWLGnvUag==
-----END RSA PRIVATE KEY-----"""


def load_private_key():
    return serialization.load_pem_private_key(
        PRIVATE_KEY_PEM.encode(),
        password=None,
        backend=default_backend()
    )


# All known Kalshi API base URLs
API_BASES = [
    "https://api.elections.kalshi.com/trade-api/v2",
    "https://demo-api.kalshi.com/trade-api/v2",
    "https://trading-api.kalshi.com/trade-api/v2", 
    "https://api.kalshi.com/trade-api/v2",
    "https://api.elections.kalshi.com/v2",
    "https://api.kalshi.com/v2",
]


def check_api_bases():
    """Check which API bases are reachable"""
    print("=" * 60)
    print("CHECKING API BASE URLS")
    print("=" * 60)
    
    for base in API_BASES:
        try:
            # Try exchange status (public endpoint)
            resp = requests.get(f"{base}/exchange/status", timeout=10)
            print(f"\n✅ {base}")
            print(f"   Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"   Response: {resp.json()}")
        except requests.exceptions.ConnectionError:
            print(f"\n❌ {base} - Connection failed")
        except Exception as e:
            print(f"\n❌ {base} - Error: {e}")


def test_with_working_base():
    """Test auth with the elections API"""
    print("\n" + "=" * 60)
    print("DETAILED AUTH TEST")
    print("=" * 60)
    
    base = "https://api.elections.kalshi.com/trade-api/v2"
    private_key = load_private_key()
    
    # Get fresh timestamp
    timestamp = str(int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000))
    
    # According to various sources, the message should be: timestamp + method + path
    # where path includes everything after the host
    method = "GET"
    path = "/trade-api/v2/portfolio/balance"
    
    message = f"{timestamp}{method}{path}"
    print(f"\nSigning message: {message}")
    
    signature = private_key.sign(
        message.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    sig_b64 = base64.b64encode(signature).decode()
    
    headers = {
        "KALSHI-ACCESS-KEY": API_KEY_ID,
        "KALSHI-ACCESS-SIGNATURE": sig_b64,
        "KALSHI-ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    print(f"\nHeaders:")
    for k, v in headers.items():
        if k == "KALSHI-ACCESS-SIGNATURE":
            print(f"   {k}: {v[:40]}...")
        else:
            print(f"   {k}: {v}")
    
    url = f"{base}/portfolio/balance"
    print(f"\nURL: {url}")
    
    resp = requests.get(url, headers=headers)
    print(f"\nResponse Status: {resp.status_code}")
    print(f"Response Headers: {dict(resp.headers)}")
    print(f"Response Body: {resp.text}")
    
    # Try to get more error details
    if resp.status_code == 401:
        print("\n--- Analyzing 401 Error ---")
        try:
            err = resp.json()
            print(f"Error code: {err.get('error', {}).get('code')}")
            print(f"Error message: {err.get('error', {}).get('message')}")
            print(f"Error details: {err.get('error', {}).get('details')}")
        except:
            pass


if __name__ == "__main__":
    check_api_bases()
    test_with_working_base()
