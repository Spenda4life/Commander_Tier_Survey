# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Flask web app for surveying Magic: The Gathering Commander deck compatibility. Users vote on which commander decks "play well together," and votes adjust edge weights in a NetworkX graph stored as a pickle file in Google Cloud Storage. The graph is used to detect communities of compatible decks via Louvain partitioning.

## Architecture

**Backend (`app.py`)** — Single Flask module. All routes, graph logic, and GCS I/O live here. No blueprints or separate modules.

- Graph state is a NetworkX undirected graph persisted as `decks_graph.pickle` in GCS bucket `ptero_cloud_storage`
- Each node represents a commander deck with attributes: `commander` (format: `"Card Name (Owner)"`), `image_url`
- Edge weights encode compatibility: voting increases weight between co-selected decks (+2) and decreases weight between split selections (-1)
- Deck selection for the survey uses a weighted random choice between community-based and edge-weight-based strategies (1:3 ratio)
- Community detection uses Louvain algorithm with a sigmoid transform on edge weights (`k=-0.125`, `resolution=1.1`, `seed=56`)

**Frontend (`templates/`)** — Three Jinja2 templates with inline JS, no build step:
- `index.html` — Survey voting page
- `network_graph.html` — vis-network force-directed graph visualization
- `communities.html` — Louvain community groupings display

**Deployment** — Google App Engine (Python 3.11 runtime) via `app.yaml`, served by gunicorn.

## Commands

```bash
# Run locally
python app.py                    # starts on 0.0.0.0:8080

# Deploy to App Engine
gcloud app deploy app.yaml

# Install dependencies
pip install -r requirements.txt
```

## Key Details

- GCS client and bucket are initialized at module level (runs on import) — the app requires valid GCP credentials
- The `/get_graph` endpoint returns `nx.node_link_data` JSON format; `/get_communities` returns nested arrays of node attribute dicts
- No tests, no linter configuration, no database — graph state is entirely in the GCS pickle file
