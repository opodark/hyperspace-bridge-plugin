# hyperspace-bridge-plugin

> Plugin per [Cheshire Cat AI](https://cheshirecat.ai/) che collega ogni nodo al cluster **HyperSpace-AGI**.

## Funzionalità

| Feature | Dettaglio |
|---|---|
| **Tracing SSE** | Ogni messaggio in ingresso viene marcato con `HS-TRACE-<timestamp>` e `node_id` |
| **System prompt injection** | Il prefix del prompt include il `node_id` e l'URL dell'orchestratore |
| **Tool forwarding** | Le tool_call possono essere inoltrate all'orchestratore (opzionale) |
| **Tool `hs_ping_orchestrator`** | Testa la connettività con l'orchestratore da chat |
| **Tool `hs_list_nodes`** | Lista i nodi attivi secondo l'orchestratore da chat |
| **Admin panel settings** | Tutto configurabile da UI senza toccare codice |

## Installazione

### Via Admin Panel (raccomandato)

1. Apri `http://localhost:1865/admin` → **Plugins**
2. Clicca **Upload Plugin** e carica lo zip del repo
3. Abilita il plugin
4. Vai in **Plugin Settings → HyperSpace Bridge** e configura:
   - `orchestrator_url` (es. `http://hyperspace-orchestrator:8000`)
   - `node_id` (es. `node-01`)
   - `trace_enabled` (default `true`)
   - `forward_tools` (default `false`)

### Via Docker Volume

```yaml
# docker-compose.yml (frammento)
volumes:
  - ./hyperspace_bridge:/app/cat/plugins/hyperspace_bridge
```

### Via git clone nella cartella plugins

```bash
cd /path/to/cheshire-cat/cat/plugins
git clone https://github.com/opodark/hyperspace-bridge-plugin.git
# Cheshire Cat rileva e carica il plugin automaticamente
```

## Struttura

```
hyperspace_bridge/
├── plugin.json        # Metadati plugin (nome, versione, autore)
├── __init__.py        # Entry point
├── settings.py        # Schema Pydantic dei settings (admin panel)
├── hooks.py           # Hook: before_cat_reads_message, before_cat_sends_message,
│                      #        after_agent_action, agent_prompt_prefix
├── tools.py           # Tool: hs_ping_orchestrator, hs_list_nodes
├── client.py          # HTTP client verso l'orchestratore (httpx / requests)
└── requirements.txt   # Dipendenze (httpx)
```

## Hook disponibili

```
before_cat_reads_message  → aggiunge trace_id e node_id al messaggio
before_cat_sends_message  → aggiunge metadata HyperSpace alla risposta
after_agent_action        → forwarding opzionale tool_call all'orchestratore
agent_prompt_prefix       → inietta contesto nodo nel system prompt
```

## Architettura nel cluster

```
HyperSpace Node N
├── Cheshire Cat :1865
│   └── hyperspace_bridge plugin
│       ├── hooks.py  →  tracing + prompt injection
│       ├── tools.py  →  hs_ping / hs_list_nodes
│       └── client.py →  POST/GET verso orchestratore
└── Ollama :11434
    └── SLM locale (Phi-3, Qwen, Mistral...)

HyperSpace Orchestrator :8000
├── GET  /health
├── GET  /nodes
└── POST /tool_call
```

## Roadmap

- [ ] Autenticazione HMAC verso l'orchestratore
- [ ] Hook `before_cat_stores_episodic_memory` per sincronizzare la memoria tra nodi
- [ ] Tool `hs_delegate_task` per delegare task ad altri nodi
- [ ] WebSocket keep-alive verso l'orchestratore
- [ ] Test suite con mock orchestratore

## Licenza

MIT
