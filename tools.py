import logging
from cat.mad_hatter.decorators import tool

log = logging.getLogger("hyperspace_bridge")


def _get_settings(cat):
    try:
        return cat.mad_hatter.get_plugin().load_settings()
    except Exception:
        return {}


def _hs_get(base_url: str, path: str):
    url = base_url.rstrip("/") + path
    try:
        import httpx
        r = httpx.get(url, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        log.warning("[HS-BRIDGE] GET %s failed: %s", url, exc)
        return None


@tool(return_direct=False)
def hs_ping_orchestrator(tool_input: str, cat):
    """
    Verifica la connettivita' con l'orchestratore HyperSpace e ritorna lo stato.
    Input: stringa vuota o qualsiasi testo.
    """
    settings = _get_settings(cat)
    url = settings.get("orchestrator_url", "")
    if not url:
        return "Orchestrator URL non configurato nelle impostazioni del plugin."
    result = _hs_get(url, "/health")
    if result is None:
        return f"Orchestratore non raggiungibile a {url}/health"
    return f"Orchestratore OK: {result}"


@tool(return_direct=False)
def hs_list_nodes(tool_input: str, cat):
    """
    Elenca i nodi HyperSpace attivi secondo l'orchestratore.
    Input: stringa vuota o qualsiasi testo.
    """
    settings = _get_settings(cat)
    url = settings.get("orchestrator_url", "")
    if not url:
        return "Orchestrator URL non configurato."
    result = _hs_get(url, "/nodes")
    if result is None:
        return "Impossibile recuperare la lista dei nodi."
    return f"Nodi attivi: {result}"
