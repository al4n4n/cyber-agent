# Cyber Agent

This repository contains a minimal, extensible LLM agent workflow for vulnerability discovery, knowledge retention, and reporting. The implementation is intentionally small and modular so you can wire in your own LLM provider, vector database, and data sources.

## What it does

1. **Discover new vulnerability reports** from a large source (HackerOne public disclosures via RSS by default).
2. **Read and summarize reports** to extract techniques, root causes, and remediation patterns.
3. **Store knowledge with RAG** (chunking + embeddings + vector search).
4. **Proactively search for issues** by applying learned heuristics against target program assets.
5. **Draft reports** for each new finding.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m agent.main --config agent/config.yaml
```

## Configuration

Edit `agent/config.yaml` to plug in your data sources, LLM, and vector store settings.

## Notes

- This is a framework starter. Wire in your preferred LLM/embedding providers (OpenAI, Anthropic, Azure, local, etc.) and storage (pgvector, Qdrant, Pinecone, etc.).
- The default implementation uses simple, offline placeholders to keep this repo runnable without secrets.
