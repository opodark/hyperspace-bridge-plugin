from cat.mad_hatter.decorators import plugin
from pydantic import BaseModel, Field


class HyperSpaceBridgeSettings(BaseModel):
    """
    Configurazione del plugin HyperSpace Bridge.
    Accessibile dall'admin panel di Cheshire Cat (Plugin Settings).
    """

    orchestrator_url: str = Field(
        default="http://hyperspace-orchestrator:8000",
        title="Orchestrator URL",
        description="URL HTTP base dell'orchestratore HyperSpace (es. http://host:8000).",
    )

    node_id: str = Field(
        default="node-01",
        title="Node ID",
        description="Identificatore univoco di questo nodo nel cluster HyperSpace.",
    )

    trace_enabled: bool = Field(
        default=True,
        title="Enable Tracing",
        description="Abilita il logging dei trace HS-TRACE nel flusso SSE.",
    )

    forward_tools: bool = Field(
        default=False,
        title="Forward Tools to Orchestrator",
        description="Se True, tutte le tool_call vengono inoltrate all'orchestratore prima dell'esecuzione locale.",
    )


@plugin
def settings_model():
    return HyperSpaceBridgeSettings
