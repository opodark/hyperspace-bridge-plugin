"""
HyperSpace Bridge Directive

Inietta il contesto del nodo HyperSpace nel system prompt ad ogni turno.
Per usarla su un agente:

    from cat import Agent

    class MyAgent(Agent):
        slug = "my_agent"
        directives = ["hyperspace"]
        system_prompt = "..."

Oppure aggiungila a un agente esistente tramite l'admin panel.
"""

import time
import logging
from cat import Directive, Agent

log = logging.getLogger("hyperspace_bridge")


class HyperSpaceDirective(Directive):
    slug = "hyperspace"
    name = "HyperSpace Bridge"
    description = "Inietta il contesto del nodo HyperSpace-AGI nel prompt e traccia ogni turno."

    # Configurazione di default — sovrascrivibile dall'admin panel del plugin
    node_id: str = "node-01"
    orchestrator_url: str = "http://hyperspace-orchestrator:8000"
    trace_enabled: bool = True

    async def start(self, agent: Agent) -> None:
        """Setup iniziale: log dell'avvio sessione."""
        if self.trace_enabled:
            ts = int(time.time())
            log.info(
                "[HS-BRIDGE] session start | trace=HS-TRACE-%s node=%s agent=%s",
                ts, self.node_id, agent.slug
            )

    async def step(self, agent: Agent) -> None:
        """
        Ad ogni turno: inietta il contesto HyperSpace nel system prompt.
        Il loop resetta il prompt prima di step(), quindi è sempre fresco.
        """
        injection = (
            f"\n\n[HYPERSPACE NODE: {self.node_id}]\n"
            f"Sei un agente del cluster HyperSpace-AGI, nodo {self.node_id}. "
            f"Puoi cooperare con altri nodi tramite l'orchestratore ({self.orchestrator_url}). "
            "Rispondi in modo conciso e strutturato per facilitare il parsing automatico."
        )
        agent.system_prompt += injection

        if self.trace_enabled:
            ts = int(time.time())
            log.info(
                "[HS-BRIDGE] step | trace=HS-TRACE-%s node=%s agent=%s",
                ts, self.node_id, agent.slug
            )

    async def finish(self, agent: Agent) -> None:
        """Fine sessione: log del completamento."""
        if self.trace_enabled:
            log.info(
                "[HS-BRIDGE] session finish | node=%s agent=%s",
                self.node_id, agent.slug
            )
