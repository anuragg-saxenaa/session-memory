#!/usr/bin/env python3
"""
Persistent Agent Memory Layer (PAML) — Cross-platform memory for AI agents.

Usage:
    paml store <key> <value>         Store a value
    paml get <key>                   Retrieve a value
    paml search <query>              Semantic search
    paml delete <key>                Delete a key
    paml list                        List all keys
    paml stats                       Show storage stats
    paml compress                    Compress memory
"""

import argparse
import json
import os
import sys
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = Path.home() / ".paml" / "data"
INDEX_FILE = Path.home() / ".paml" / "index.jsonl"
CONFIG_FILE = Path.home() / ".paml" / "config.json"

def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps({
            "created": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "retention_days": 90
        }))

def _hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()[:16]

def store(key: str, value: str, ttl: int = 0) -> bool:
    ensure_dirs()
    h = _hash_key(key)
    path = DATA_DIR / h
    meta = {
        "key": key,
        "hash": h,
        "stored": datetime.utcnow().isoformat(),
        "expires": (datetime.utcnow() + timedelta(seconds=ttl)).isoformat() if ttl else None,
        "size": len(value)
    }
    path.write_text(value)
    with open(INDEX_FILE, "a") as f:
        f.write(json.dumps(meta) + "\n")
    print(f"Stored: {key}")
    return True

def get(key: str) -> str | None:
    ensure_dirs()
    h = _hash_key(key)
    path = DATA_DIR / h
    if not path.exists():
        return None
    return path.read_text()

def search(query: str) -> list[dict]:
    ensure_dirs()
    results = []
    if not INDEX_FILE.exists():
        return results
    with open(INDEX_FILE) as f:
        for line in f:
            meta = json.loads(line)
            if query.lower() in meta.get("key", "").lower():
                results.append(meta)
    return results

def delete(key: str) -> bool:
    ensure_dirs()
    h = _hash_key(key)
    path = DATA_DIR / h
    if path.exists():
        path.unlink()
        print(f"Deleted: {key}")
        return True
    print(f"Not found: {key}")
    return False

def list_keys() -> list[str]:
    ensure_dirs()
    keys = []
    if not INDEX_FILE.exists():
        return keys
    with open(INDEX_FILE) as f:
        seen = set()
        for line in f:
            meta = json.loads(line)
            k = meta["key"]
            if k not in seen:
                keys.append(k)
                seen.add(k)
    return keys

def stats() -> dict:
    ensure_dirs()
    total = 0
    count = 0
    keys = set()
    if INDEX_FILE.exists():
        with open(INDEX_FILE) as f:
            for line in f:
                meta = json.loads(line)
                keys.add(meta["key"])
                total += meta.get("size", 0)
                count += 1
    return {
        "total_bytes": total,
        "total_entries": count,
        "unique_keys": len(keys),
        "storage_path": str(DATA_DIR)
    }

def compress():
    """Remove duplicate entries, keep latest."""
    if not INDEX_FILE.exists():
        print("Nothing to compress.")
        return
    seen = {}
    temp = DATA_DIR.parent / "index.temp.jsonl"
    with open(INDEX_FILE) as f:
        for line in f:
            meta = json.loads(line)
            key = meta["key"]
            seen[key] = line.strip()
    with open(temp, "w") as f:
        for line in seen.values():
            f.write(line + "\n")
    temp.rename(INDEX_FILE)
    removed = sum(1 for _ in (DATA_DIR.parent / "index.bak").glob("*",) if True) if (DATA_DIR.parent / "index.bak").exists() else 0
    print(f"Compressed: {len(seen)} unique keys retained.")

def main():
    parser = argparse.ArgumentParser(description="PAML — Persistent Agent Memory Layer")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("init", help="Initialize PAML storage")

    p = sub.add_parser("store", help="Store a value")
    p.add_argument("key")
    p.add_argument("value")
    p.add_argument("--ttl", type=int, default=0, help="TTL in seconds")

    p = sub.add_parser("get", help="Get a value")
    p.add_argument("key")

    p = sub.add_parser("search", help="Search keys")
    p.add_argument("query")

    p = sub.add_parser("delete", help="Delete a key")
    p.add_argument("key")

    p = sub.add_parser("list", help="List all keys")

    p = sub.add_parser("stats", help="Show stats")

    sub.add_parser("compress", help="Remove duplicate entries")

    args = parser.parse_args()

    if args.cmd == "init":
        ensure_dirs()
        print("PAML initialized at ~/.paml/")
        print(f"Data: {DATA_DIR}")
        print(f"Index: {INDEX_FILE}")
        return

    if not DATA_DIR.exists():
        print("Not initialized. Run: paml init")
        sys.exit(1)

    if args.cmd == "store":
        ok = store(args.key, args.value, args.ttl)
        sys.exit(0 if ok else 1)
    elif args.cmd == "get":
        val = get(args.key)
        if val is None:
            print(f"Not found: {args.key}")
            sys.exit(1)
        print(val)
    elif args.cmd == "search":
        results = search(args.query)
        if not results:
            print("No results.")
        for r in results:
            print(f"  {r['key']} ({r['stored']})")
    elif args.cmd == "delete":
        ok = delete(args.key)
        sys.exit(0 if ok else 1)
    elif args.cmd == "list":
        keys = list_keys()
        if not keys:
            print("(empty)")
        for k in keys:
            print(f"  {k}")
    elif args.cmd == "stats":
        s = stats()
        print(f"Total bytes:  {s['total_bytes']}")
        print(f"Total entries: {s['total_entries']}")
        print(f"Unique keys:  {s['unique_keys']}")
        print(f"Storage path: {s['storage_path']}")
    elif args.cmd == "compress":
        compress()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()