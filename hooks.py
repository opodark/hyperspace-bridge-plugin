import time
import logging
from cat.mad_hatter.decorators import hook

log = logging.getLogger("hyperspace_bridge")


def _get_settings(cat):
    try:
        return cat.mad_hatter.get_plugin().load_settings()
    except Exception:
        return {}


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


@hook(priority=10)
def before_cat_reads_message(user_message_json: dict, cat) -> dict:
    """Timbra ogni messaggio in ingresso con trace_id e node_id HyperSpace."""
    settings = _get_settings(cat)
    if not settings.get("trace_enabled", True):
        return user_message_json

    ts = int(time.time())
    trace_id = f"HS-TRACE-{ts}"
    user_message_json["hyperspace_trace_id"] = trace_id
    user_message_json["hyperspace_node_id"] = settings.get("node_id", "node-01")

    log.info(
        "[HS-BRIDGE] incoming | trace=%s node=%s text='%s'",
        trace_id,
        settings.get("node_id", "node-01"),
        user_message_json.get("text", "")[:80],
    )
    return user_message_json


@hook(priority=10)
def before_cat_sends_message(message: dict, cat) -> dict:
    """Aggiunge metadata HyperSpace alla risposta in uscita."""
    settings = _get_settings(cat)
    if not settings.get("trace_enabled", True):
        return message

    message.setdefault("why", {}).update({
        "hyperspace_node": settings.get("node_id", "node-01"),
        "hyperspace_plugin_version": "0.1.0",
    })
    log.info("[HS-BRIDGE] outgoing | node=%s", settings.get("node_id", "node-01"))
    return message


@hook(priority=10)
def after_agent_action(agent_output, cat):
    """Se forward_tools=True, inoltra ogni tool_call all'orchestratore."""
    settings = _get_settings(cat)
    if not settings.get("forward_tools", False):
        return agent_output

    if agent_output and getattr(agent_output, "tool", None):
        payload = {
            "node_id": settings.get("node_id", "node-01"),
            "tool": agent_output.tool,
            "input": getattr(agent_output, "tool_input", {}),
        }
        log.info("[HS-BRIDGE] forwarding tool | tool=%s", agent_output.tool)
        _hs_post(settings.get("orchestrator_url", ""), "/tool_call", payload)

    return agent_output


@hook(priority=5)
def agent_prompt_prefix(prefix: str, cat) -> str:
    """Inietta contesto nodo HyperSpace nel system prompt."""
    settings = _get_settings(cat)
    node_id = settings.get("node_id", "node-01")
    orch_url = settings.get("orchestrator_url", "http://hyperspace-orchestrator:8000")
    injection = (
        f"\n\n[HYPERSPACE NODE: {node_id}]\n"
        f"Sei un agente del cluster HyperSpace-AGI, nodo {node_id}. "
        f"Puoi cooperare con altri nodi tramite l'orchestratore ({orch_url}). "
        "Rispondi in modo conciso e strutturato per facilitare il parsing automatico.\n"
    )
    return prefix + injection
