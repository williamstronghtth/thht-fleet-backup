#!/usr/bin/env python3
"""Shared WordPress credentials loader.

Reads from the environment first, falling back to a gitignored `.env` file in
the workspace root. Never hardcode the application password in a script.

    WP_SITE=https://thehooverhometeam.com
    WP_USER=chris@cbcoastrealty.com
    WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
"""
import os
import xmlrpc.client
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

DEFAULTS = {
    "WP_SITE": "https://thehooverhometeam.com",
    "WP_USER": "chris@cbcoastrealty.com",
}


def _load_env_file():
    if not ENV_FILE.exists():
        return {}
    values = {}
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def get_credentials():
    """Return (site, user, app_password). Raises if the password is missing."""
    file_values = _load_env_file()

    def resolve(key):
        return os.environ.get(key) or file_values.get(key) or DEFAULTS.get(key)

    password = resolve("WP_APP_PASSWORD")
    if not password:
        raise RuntimeError(
            "WP_APP_PASSWORD is not set. Add it to the environment or to "
            f"{ENV_FILE} (which is gitignored)."
        )
    return resolve("WP_SITE"), resolve("WP_USER"), password


# The host's WAF answers the first request with a JS cookie challenge and a 409.
# Sending the cookie up front skips the challenge. Changing the User-Agent trips
# Mod_Security, so leave the default one alone.
WAF_COOKIE = os.environ.get("WP_WAF_COOKIE", "humans_21909=1")


class _WafTransport(xmlrpc.client.SafeTransport):
    def send_headers(self, connection, headers):
        super().send_headers(connection, headers)
        connection.putheader("Cookie", WAF_COOKIE)


def get_server():
    """XML-RPC ServerProxy that passes the host's WAF cookie challenge."""
    site = get_credentials()[0]
    return xmlrpc.client.ServerProxy(f"{site}/xmlrpc.php", transport=_WafTransport())
