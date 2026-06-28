from cat.mad_hatter.decorators import tool
from .client import hs_get


@tool(return_direct=False)
def hs_ping_orchestrator(tool_input: str, cat):
    """
    Verifica la connettivita' con l'orchestratore HyperSpace e ritorna lo stato.
    Input: stringa vuota o qualsiasi testo.
    """
    settings = cat.mad_hatter.get_plugin().load_settings()
    url = settings.get("orchestrator_url", "")
    if not url:
        return "Orchestrator URL non configurato nelle impostazioni del plugin."

    result = hs_get(url, "/health")
    if result is None:
        return f"Orchestratore non raggiungibile a {url}/health"
    return f"Orchestratore OK: {result}"


@tool(return_direct=False)
def hs_list_nodes(tool_input: str, cat):
    """
    Elenca i nodi HyperSpace attivi secondo l'orchestratore.
    Input: stringa vuota o qualsiasi testo.
    """
    settings = cat.mad_hatter.get_plugin().load_settings()
    url = settings.get("orchestrator_url", "")
    if not url:
        return "Orchestrator URL non configurato."

    result = hs_get(url, "/nodes")
    if result is None:
        return "Impossibile recuperare la lista dei nodi."
    return f"Nodi attivi: {result}"
