from cat.mad_hatter.decorators import tool
from hyperspace_bridge.client import hs_post, hs_get


@tool(return_direct=False)
def hs_ping_orchestrator(tool_input: str, cat):
    """
    Verifica la connettività con l'orchestratore HyperSpace.
    Utile per debug: rispondi 'ping orchestratore' per usarlo.
    Input: stringa vuota o qualsiasi testo.
    """
    settings = cat.mad_hatter.get_plugin().load_settings()
    url = settings.get("orchestrator_url", "")
    if not url:
        return "Orchestrator URL non configurato nelle impostazioni del plugin."

    result = hs_get(url, "/health")
    if result is None:
        return f"Orchestratore non raggiungibile all'indirizzo {url}."
    return f"Orchestratore risponde: {result}"


@tool(return_direct=False)
def hs_list_nodes(tool_input: str, cat):
    """
    Elenca i nodi HyperSpace attivi secondo l'orchestratore.
    Rispondi 'lista nodi hyperspace' per usarlo.
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
