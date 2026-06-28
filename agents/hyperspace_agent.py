"""
HyperSpace Agent

Agente dedicato alla gestione del nodo HyperSpace-AGI.
Espone tool per interagire con l'orchestratore direttamente da chat.

Indirizzo: invia messaggi con {"agent": "hyperspace"} per usarlo direttamente.
Oppure usa i singoli tool da qualsiasi altro agente tramite la directive.

Esempi:
    "ping orchestratore"
    "lista nodi hyperspace"
    "stato nodo"
"""

import logging
from cat import Agent, tool, user

log = logging.getLogger("hyperspace_bridge")


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


def _hs_post(base_url: str, path: str, payload: dict):
    url = base_url.rstrip("/") + path
    try:
        import httpx
        r = httpx.post(url, json=payload, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        log.warning("[HS-BRIDGE] POST %s failed: %s", url, exc)
        return None


class HyperSpaceAgent(Agent):
    slug = "hyperspace"
    name = "HyperSpace Agent"
    description = "Agente del cluster HyperSpace-AGI: gestisce il nodo e comunica con l'orchestratore."

    # Directive integrata: inietta contesto HyperSpace ad ogni turno
    directives = ["hyperspace"]

    system_prompt = (
        "Sei l'agente HyperSpace-AGI di questo nodo. "
        "Hai accesso a tool per verificare la connettivit\u00e0 con l'orchestratore, "
        "elencare i nodi attivi e ottenere lo stato del cluster. "
        "Rispondi sempre in modo conciso e strutturato."
    )

    # Configurazione nodo — sincronizzata con HyperSpaceDirective
    _node_id: str = "node-01"
    _orchestrator_url: str = "http://hyperspace-orchestrator:8000"

    @tool
    async def ping_orchestrator(self) -> str:
        """
        Verifica la connettivita' con l'orchestratore HyperSpace.
        Usa questo tool quando l'utente chiede di testare la connessione
        o verificare se l'orchestratore e' raggiungibile.
        """
        result = _hs_get(self._orchestrator_url, "/health")
        if result is None:
            return f"Orchestratore non raggiungibile a {self._orchestrator_url}/health"
        return f"Orchestratore OK: {result}"

    @tool
    async def list_nodes(self) -> str:
        """
        Elenca i nodi HyperSpace attivi nel cluster secondo l'orchestratore.
        Usa questo tool quando l'utente chiede quali nodi sono online
        o vuole vedere lo stato del cluster.
        """
        result = _hs_get(self._orchestrator_url, "/nodes")
        if result is None:
            return "Impossibile recuperare la lista dei nodi dall'orchestratore."
        return f"Nodi attivi nel cluster: {result}"

    @tool
    async def node_status(self) -> str:
        """
        Restituisce lo stato corrente di questo nodo: node_id, orchestrator_url
        e timestamp. Usa questo tool per diagnostica o quando l'utente
        chiede informazioni su questo nodo specifico.
        """
        import time
        return (
            f"Node ID: {self._node_id}\n"
            f"Orchestrator: {self._orchestrator_url}\n"
            f"Timestamp: {int(time.time())}\n"
            f"Status: online"
        )

    @tool
    async def send_task_to_orchestrator(self, task: str) -> str:
        """
        Invia un task testuale all'orchestratore HyperSpace per distribuzione
        agli altri nodi del cluster. Usa quando l'utente vuole delegare
        un'operazione al cluster.
        Input: descrizione del task da distribuire.
        """
        payload = {
            "node_id": self._node_id,
            "task": task,
        }
        result = _hs_post(self._orchestrator_url, "/task", payload)
        if result is None:
            return f"Impossibile inviare il task all'orchestratore ({self._orchestrator_url})."
        return f"Task inviato al cluster: {result}"
