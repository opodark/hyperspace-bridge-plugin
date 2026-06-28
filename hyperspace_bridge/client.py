import logging
from typing import Any, Optional

try:
    import httpx
    _HTTP_LIB = "httpx"
except ImportError:
    import requests as httpx  # type: ignore
    _HTTP_LIB = "requests"

log = logging.getLogger("hyperspace_bridge")
DEFAULT_TIMEOUT = 5  # secondi


def hs_post(base_url: str, path: str, payload: dict) -> Optional[Any]:
    """Esegue POST verso l'orchestratore HyperSpace. Ritorna None in caso di errore."""
    url = base_url.rstrip("/") + path
    try:
        if _HTTP_LIB == "httpx":
            r = httpx.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
        else:
            r = httpx.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        log.warning("[HS-BRIDGE] POST %s failed: %s", url, exc)
        return None


def hs_get(base_url: str, path: str) -> Optional[Any]:
    """Esegue GET verso l'orchestratore HyperSpace. Ritorna None in caso di errore."""
    url = base_url.rstrip("/") + path
    try:
        if _HTTP_LIB == "httpx":
            r = httpx.get(url, timeout=DEFAULT_TIMEOUT)
        else:
            r = httpx.get(url, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        log.warning("[HS-BRIDGE] GET %s failed: %s", url, exc)
        return None
