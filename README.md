# ShopSphere

Production-grade teaching platform for demonstrating OWASP ASI03 (Identity and Privilege Abuse)
in a multi-agent e-commerce system.

## Requirements

- Python 3.12
- uv
- Docker + Docker Compose

## Bootstrap

```bash
uv sync --all-groups
cp .env.example .env
```

## Task Runner (poethepoet)

```bash
uv run poe lint
uv run poe format
uv run poe typecheck
uv run poe test
uv run poe test-integration
uv run poe test-attack
uv run poe migrate
uv run poe seed
uv run poe up
uv run poe down
uv run poe check
```

`make` remains available as a thin compatibility wrapper around `uv run poe <task>`.
