import time
import logging
from cat.mad_hatter.decorators import hook
from hyperspace_bridge.client import hs_post

log = logging.getLogger("hyperspace_bridge")


# ---------------------------------------------------------------------------
# 1. BEFORE_CAT_READS_MESSAGE
#    Intercetta il messaggio in ingresso, aggiunge metadata HyperSpace.
# ---------------------------------------------------------------------------
@hook(priority=10)
def before_cat_reads_message(user_message_json: dict, cat) -> dict:
    settings = cat.mad_hatter.get_plugin().load_settings()
    if not settings.get("trace_enabled", True):
        return user_message_json

    ts = int(time.time())
    trace_id = f"HS-TRACE-{ts}"
    user_message_json["hyperspace_trace_id"] = trace_id
    user_message_json["hyperspace_node_id"] = settings.get("node_id", "node-01")

    log.info("[HS-BRIDGE] incoming message | trace=%s node=%s text='%s'",
             trace_id, settings.get("node_id"), user_message_json.get("text", "")[:80])

    return user_message_json


# ---------------------------------------------------------------------------
# 2. BEFORE_CAT_SENDS_MESSAGE
#    Aggiunge metadata HyperSpace alla risposta in uscita.
# ---------------------------------------------------------------------------
@hook(priority=10)
def before_cat_sends_message(message: dict, cat) -> dict:
    settings = cat.mad_hatter.get_plugin().load_settings()
    if not settings.get("trace_enabled", True):
        return message

    message.setdefault("why", {}).update({
        "hyperspace_node": settings.get("node_id", "node-01"),
        "hyperspace_plugin_version": "0.1.0",
    })

    log.info("[HS-BRIDGE] outgoing message | node=%s", settings.get("node_id"))
    return message


# ---------------------------------------------------------------------------
# 3. AFTER_AGENT_ACTION
#    Se forward_tools=True, inoltra ogni tool_call all'orchestratore.
# ---------------------------------------------------------------------------
@hook(priority=10)
def after_agent_action(agent_output, cat):
    settings = cat.mad_hatter.get_plugin().load_settings()
    if not settings.get("forward_tools", False):
        return agent_output

    if agent_output and getattr(agent_output, "tool", None):
        tool_name = agent_output.tool
        tool_input = getattr(agent_output, "tool_input", {})
        log.info("[HS-BRIDGE] forwarding tool call | tool=%s input=%s", tool_name, tool_input)

        payload = {
            "node_id": settings.get("node_id", "node-01"),
            "tool": tool_name,
            "input": tool_input,
        }
        hs_post(settings.get("orchestrator_url", ""), "/tool_call", payload)

    return agent_output


# ---------------------------------------------------------------------------
# 4. AGENT_PROMPT_PREFIX
#    Inietta nel system prompt le info sul nodo HyperSpace corrente.
# ---------------------------------------------------------------------------
@hook(priority=5)
def agent_prompt_prefix(prefix: str, cat) -> str:
    settings = cat.mad_hatter.get_plugin().load_settings()
    node_id = settings.get("node_id", "node-01")
    orch_url = settings.get("orchestrator_url", "")
    injection = (
        f"\n\n[HYPERSPACE NODE: {node_id}]\n"
        f"Sei un agente del cluster HyperSpace-AGI, nodo {node_id}. "
        f"Puoi cooperare con altri nodi tramite l'orchestratore ({orch_url}). "
        "Rispondi in modo conciso e strutturato per facilitare il parsing automatico.\n"
    )
    return prefix + injection
