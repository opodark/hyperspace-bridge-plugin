# hyperspace-bridge-plugin

> Plugin per [Cheshire Cat AI](https://cheshirecat.ai/) che collega ogni nodo al cluster **HyperSpace-AGI**.

## Installazione

### Via git clone nella cartella plugins (raccomandato)

```bash
# Entra nella cartella plugins di Cheshire Cat
cd /path/to/cheshire-cat/cat/plugins

# Clona direttamente con il nome corretto del package
git clone https://github.com/opodark/hyperspace-bridge-plugin.git hyperspace_bridge

# Cheshire Cat rileva e carica il plugin automaticamente (no restart)
```

> **Importante:** clona con il nome `hyperspace_bridge` (underscore), non il nome default del repo.
> Il nome della cartella deve corrispondere al package Python.

### Via Docker volume

```yaml
# docker-compose.yml (frammento)
volumes:
  - ./hyperspace_bridge:/app/cat/plugins/hyperspace_bridge
```

## Configurazione

Dopo l'installazione, vai in `http://localhost:1865/admin` → **Plugins** → **HyperSpace Bridge Settings**:

| Setting | Default | Descrizione |
|---|---|---|
| `orchestrator_url` | `http://hyperspace-orchestrator:8000` | URL base dell'orchestratore |
| `node_id` | `node-01` | ID univoco del nodo nel cluster |
| `trace_enabled` | `true` | Abilita logging HS-TRACE |
| `forward_tools` | `false` | Inoltra tool_call all'orchestratore |

## Funzionalità

| Feature | Hook/Tool | Dettaglio |
|---|---|---|
| **Tracing SSE** | `before_cat_reads_message` | Marca ogni messaggio con `HS-TRACE-<ts>` e `node_id` |
| **System prompt injection** | `agent_prompt_prefix` | Inietta `[HYPERSPACE NODE: id]` nel system prompt |
| **Metadata risposta** | `before_cat_sends_message` | Aggiunge `hyperspace_node` nel campo `why` |
| **Tool forwarding** | `after_agent_action` | POST tool_call all'orchestratore (se abilitato) |
| **Ping orchestratore** | tool `hs_ping_orchestrator` | Testa connettività da chat |
| **Lista nodi** | tool `hs_list_nodes` | Elenca nodi attivi da chat |

## Struttura

```
hyperspace_bridge/   (= root del repo)
├── plugin.json
├── __init__.py
├── settings.py
├── hooks.py
├── tools.py
├── client.py
└── requirements.txt
```

## Architettura

```
HyperSpace Node N
├── Cheshire Cat :1865
│   └── hyperspace_bridge (plugin)
│       ├── hooks   → tracing + prompt injection + tool forwarding
│       ├── tools   → hs_ping / hs_list_nodes
│       └── client  → HTTP verso orchestratore
└── Ollama :11434
    └── SLM locale (Phi-3, Qwen, Mistral...)

HyperSpace Orchestrator :8000
├── GET  /health
├── GET  /nodes
└── POST /tool_call
```

## Aggiornamento

```bash
cd /path/to/cheshire-cat/cat/plugins/hyperspace_bridge
git pull
# Il Cat rileva le modifiche e ricarica il plugin automaticamente
```

## Roadmap

- [ ] Autenticazione HMAC verso l'orchestratore
- [ ] Hook `before_cat_stores_episodic_memory` per sync memoria tra nodi
- [ ] Tool `hs_delegate_task` per delegare task ad altri nodi
- [ ] WebSocket keep-alive verso l'orchestratore
- [ ] Test suite con mock orchestratore

## Licenza

MIT
