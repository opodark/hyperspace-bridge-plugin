# hyperspace-bridge-plugin

> Plugin per [Cheshire Cat AI v2](https://cheshirecat.ai/) che collega ogni nodo al cluster **HyperSpace-AGI**.

## Installazione

```bash
# Entra nella cartella plugins di Cheshire Cat
cd /path/to/cheshire-cat/plugins

# Clona con il nome corretto del package (underscore, non trattino)
git clone https://github.com/opodark/hyperspace-bridge-plugin.git hyperspace_bridge

# Il Cat rileva e carica il plugin automaticamente
```

## Struttura (Cheshire Cat v2)

```
hyperspace_bridge/
├── plugin.json
├── __init__.py
├── requirements.txt
├── agents/
│   └── hyperspace_agent.py    # Agent con tool: ping, list_nodes, node_status, send_task
└── directives/
    └── hyperspace_directive.py # Directive: inietta contesto HyperSpace nel prompt
```

## Componenti

### HyperSpaceAgent (`slug: "hyperspace"`)

Agente dedicato al nodo HyperSpace. Indirizzabile direttamente:

```bash
curl -N -X POST "http://localhost:1865/agents/hyperspace/message" \
  -H "Authorization: Bearer meow" \
  -H "Content-Type: application/json" \
  -d '{"text": "ping orchestratore"}'
```

Tool disponibili:

| Tool | Trigger | Descrizione |
|---|---|---|
| `ping_orchestrator` | "ping orchestratore" | Testa connettività /health |
| `list_nodes` | "lista nodi" | GET /nodes sull'orchestratore |
| `node_status` | "stato nodo" | Info nodo corrente + timestamp |
| `send_task_to_orchestrator` | "invia task: ..." | POST /task all'orchestratore |

### HyperSpaceDirective (`slug: "hyperspace"`)

Inietta il contesto del nodo HyperSpace nel system prompt di **qualsiasi agente** ad ogni turno.

Per aggiungere la directive a un agente esistente:

```python
from cat import Agent

class MyAgent(Agent):
    slug = "my_agent"
    directives = ["hyperspace"]  # <- aggiunge contesto HyperSpace
    system_prompt = "..."
```

## Configurazione

Edita `node_id` e `orchestrator_url` direttamente nei file:
- `agents/hyperspace_agent.py` → `_node_id`, `_orchestrator_url`
- `directives/hyperspace_directive.py` → `node_id`, `orchestrator_url`

O tramite admin panel se il Cat v2 supporta plugin settings.

## Architettura nel cluster

```
HyperSpace Node N
├── Cheshire Cat v2 :1865
│   └── hyperspace_bridge (plugin)
│       ├── HyperSpaceAgent    → tool: ping, list_nodes, node_status, send_task
│       └── HyperSpaceDirective → prompt injection + tracing per ogni agente
└── Ollama :11434
    └── SLM locale (Phi-3, Qwen, Mistral...)

HyperSpace Orchestrator :8000
├── GET  /health
├── GET  /nodes
├── POST /task
└── POST /tool_call  (futuro)
```

## Aggiornamento

```bash
cd /path/to/cheshire-cat/plugins/hyperspace_bridge
git pull
# Il Cat rileva le modifiche e ricarica automaticamente
```

## Roadmap

- [ ] Plugin settings via admin panel (quando supportato da Cat v2)
- [ ] Autenticazione HMAC verso l'orchestratore
- [ ] Directive `hyperspace_memory` per sync memoria episodica tra nodi
- [ ] Tool `delegate_task` per routing intelligente verso nodo specializzato
- [ ] WebSocket keep-alive verso l'orchestratore

## Licenza

MIT
