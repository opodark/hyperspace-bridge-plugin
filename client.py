# client.py mantenuto per compatibilita' futura e test diretti.
# hooks.py e tools.py usano import inline di httpx per evitare dipendenze circolari.

import logging
from typing import Any, Optional

log = logging.getLogger("hyperspace_bridge")
DEFAULT_TIMEOUT = 5


def hs_post(base_url: str, path: str, payload: dict) -> Optional[Any]:
    url = base_url.rstrip("/") + path
    try:
        import httpx
        r = httpx.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        log.warning("[HS-BRIDGE] POST %s failed: %s", url, exc)
        return None


def hs_get(base_url: str, path: str) -> Optional[Any]:
    url = base_url.rstrip("/") + path
    try:
        import httpx
        r = httpx.get(url, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        log.warning("[HS-BRIDGE] GET %s failed: %s", url, exc)
        return None
