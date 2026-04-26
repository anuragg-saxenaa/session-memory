# PAML — Persistent Agent Memory Layer

> Give your AI agents a memory that survives between sessions.

PAML is a zero-dependency CLI tool that provides persistent key-value storage for AI coding agents. Store context, learned facts, and session state — and retrieve them in future sessions without starting from scratch.

## Install

```bash
pip install paml
# or just download paml.py and chmod +x
```

## Quick Start

```bash
# Initialize
paml init

# Store something
paml store user_prefs "Uses TypeScript, prefers dark mode"
paml store project_context "Backend is Go, frontend is React, DB is Postgres"

# Retrieve
paml get user_prefs

# Search
paml search project

# List all keys
paml list

# Stats
paml stats
```

## Commands

| Command | Description |
|---------|-------------|
| `paml init` | Initialize storage at `~/.paml/` |
| `paml store <key> <value>` | Store a value (use `--ttl N` for expiry in seconds) |
| `paml get <key>` | Retrieve a value |
| `paml search <query>` | Fuzzy search over keys |
| `paml delete <key>` | Delete a key |
| `paml list` | List all keys |
| `paml stats` | Show storage stats (bytes, entries) |
| `paml compress` | Remove duplicate index entries |

## Use Cases

**Session continuity**: Store the context of what you worked on last session, so the next session starts with full context.

**Learned facts**: Store things the agent learns about the codebase that aren't in the code itself.

**Preference memory**: Remember developer preferences (language, tooling, conventions) across sessions.

**Context caching**: Cache expensive lookups (DB schemas, API docs) that are expensive to rebuild.

## How It Works

PAML stores key-value pairs in `~/.paml/data/` using a hash of the key as the filename. All keys are indexed in `~/.paml/index.jsonl` for search and list operations.

```
~/.paml/
  data/          # actual values (one file per key hash)
  index.jsonl   # key metadata for search/list
  config.json   # configuration
```

## Python API

```python
import subprocess

# Store
subprocess.run(["paml", "store", "my_key", "my_value"])

# Get
result = subprocess.run(["paml", "get", "my_key"], capture_output=True, text=True)
print(result.stdout.strip())

# Search
result = subprocess.run(["paml", "search", "context"], capture_output=True, text=True)
```

Or import as a module:

```python
import sys
sys.path.insert(0, "/path/to/paml.py")
from paml import store, get, search, list_keys, stats, compress
```

## License

MIT — do whatever you want with it.