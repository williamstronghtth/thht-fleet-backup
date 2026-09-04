#!/usr/bin/env python3
"""
Kalshi API Connection Test v5 - RSA-PSS signing
Based on Kalshi's official documentation
"""

import base64
import datetime
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

API_BASE = "https://api.elections.kalshi.com/trade-api/v2"
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


def sign_pss(private_key, message: bytes) -> str:
    """Sign with RSA-PSS (SHA256, max salt length)"""
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()


def test_pss_signing():
    """Test with RSA-PSS"""
    print("=" * 60)
    print("TESTING RSA-PSS SIGNING")
    print("=" * 60)
    
    private_key = load_private_key()
    method = "GET"
    path = "/trade-api/v2/portfolio/balance"
    
    # Try different message formats with PSS
    message_formats = [
        ("timestamp+method+path", lambda ts: f"{ts}{method}{path}"),
        ("timestamp+method+endpoint", lambda ts: f"{ts}{method}/portfolio/balance"),
        ("method+path+timestamp", lambda ts: f"{method}{path}{ts}"),
        ("ts_space_method_space_path", lambda ts: f"{ts} {method} {path}"),
    ]
    
    for name, fmt_func in message_formats:
        timestamp = str(int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000))
        message = fmt_func(timestamp)
        
        try:
            sig_b64 = sign_pss(private_key, message.encode())
            
            headers = {
                "KALSHI-ACCESS-KEY": API_KEY_ID,
                "KALSHI-ACCESS-SIGNATURE": sig_b64,
                "KALSHI-ACCESS-TIMESTAMP": timestamp,
            }
            
            resp = requests.get(f"{API_BASE}/portfolio/balance", headers=headers, timeout=10)
            status = "✅" if resp.status_code == 200 else "❌"
            print(f"\n{status} {name}: {resp.status_code}")
            if resp.status_code == 200:
                print(f"   SUCCESS! {resp.json()}")
                return True
        except Exception as e:
            print(f"\n❌ {name}: Error - {e}")
    
    return False


def test_different_salt_lengths():
    """Try different PSS salt lengths"""
    print("\n" + "=" * 60)
    print("TESTING DIFFERENT PSS SALT LENGTHS")
    print("=" * 60)
    
    private_key = load_private_key()
    timestamp = str(int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000))
    method = "GET"
    path = "/trade-api/v2/portfolio/balance"
    message = f"{timestamp}{method}{path}".encode()
    
    salt_lengths = [
        ("MAX_LENGTH", padding.PSS.MAX_LENGTH),
        ("DIGEST_LENGTH (32)", 32),
        ("20", 20),
        ("0", 0),
    ]
    
    for name, salt_len in salt_lengths:
        try:
            signature = private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=salt_len
                ),
                hashes.SHA256()
            )
            sig_b64 = base64.b64encode(signature).decode()
            
            headers = {
                "KALSHI-ACCESS-KEY": API_KEY_ID,
                "KALSHI-ACCESS-SIGNATURE": sig_b64,
                "KALSHI-ACCESS-TIMESTAMP": timestamp,
            }
            
            resp = requests.get(f"{API_BASE}/portfolio/balance", headers=headers, timeout=10)
            status = "✅" if resp.status_code == 200 else "❌"
            print(f"   {status} Salt={name}: {resp.status_code}")
            if resp.status_code == 200:
                print(f"      SUCCESS! {resp.json()}")
                return True
        except Exception as e:
            print(f"   ❌ Salt={name}: Error - {e}")
    
    return False


if __name__ == "__main__":
    test_pss_signing()
    test_different_salt_lengths()
