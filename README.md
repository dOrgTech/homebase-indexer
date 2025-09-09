# Homebase Indexer (v3)

Minimal DipDup (v6.1) + Hasura + Postgres indexer for Homebase/RegistryDAO. It indexes on-chain events into Postgres and exposes them via Hasura GraphQL.

## Quick Start (Docker)
- Start services: `docker-compose up -d`
- Hasura Console: open `http://localhost:9088`
- Track tables: Hasura → Data → public → Track All tables (Optional) 
- Logs (indexer): `docker-compose logs -f indexer`

## Local Run (no Docker)
- Install: `pip install -r requirements.txt`
- Set env vars: `PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DB, PG_SCHEMA`
- Run: `python -m dipdup run -c dipdup.yml`

## Project Structure
- `registrydao/` Python package (handlers, utils, models, hooks, types, sql)
- `hasura/` Hasura metadata (optional)
- `dipdup.yml` DipDup configuration (contracts, datasources, indexes)
- `docker-compose.yml` Postgres, Hasura (mapped to `http://localhost:9088`), indexer

## Development Notes
- Format with Black and isort (see `requirements.txt`)
- Handlers live in `registrydao/handlers/` as `on_<event>.py`
- Prefer shared logic in `registrydao/utils/`

## Configuration
- Review `dipdup.yml` before enabling new indexes (check `first_level`, network)
- Optional: `tzkt-proxy` and `vector` services are included in compose

## TzKT Proxy (1.16 Compatibility)
- Why: TzKT 1.16 replaces the SignalR events hub (`/v1/events`) with a native WebSocket endpoint (`/v1/ws`). Some clients (including current DipDup usage) still call `/v1/events`.
- How: The `tzkt-proxy` Nginx service rewrites `/v1/events` and `/v1/events/*` to the new WebSocket path and upgrades the connection, while proxying other `/v1/*` REST calls unchanged.
- Wiring: In `docker-compose.yml`, the proxy is reachable as `tzkt-mainnet` and `tzkt-ghostnet` (network aliases). `dipdup.yml` points datasources to `http://tzkt-mainnet` and `http://tzkt-ghostnet`, enabling streaming against TzKT 1.16.
- Config: See `nginx-tzkt.conf`. Adjust upstreams if using a self-hosted TzKT; keep server names consistent with `dipdup.yml`.

# Deprecation Notices

https://x.com/dipdup_io/status/1955649362069201026