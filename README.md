# Homebase Indexer (v3)

Minimal DipDup (v7.x) + Hasura + Postgres indexer for Homebase/RegistryDAO. It indexes on-chain events into Postgres and exposes them via Hasura GraphQL.

## Quick Start (Docker)
- Start services: `docker-compose up -d`
- Hasura Console: open `http://localhost:9013`
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
- `docker-compose.yml` Postgres, Hasura (mapped to `http://localhost:9013`), indexer

## Development Notes
- Format with Black and isort (see `requirements.txt`)
- Handlers live in `registrydao/handlers/` as `on_<event>.py`
- Prefer shared logic in `registrydao/utils/`

## Configuration
- Review `dipdup.yml` before enabling new indexes (check `first_level`, network)
- Optional: `vector` service for log shipping to Axiom is included in compose
- DipDup 7.x has native WebSocket support for TzKT 1.16+, connecting directly to `https://api.tzkt.io` and `https://api.ghostnet.tzkt.io`

# Deprecation Notices

https://x.com/dipdup_io/status/1955649362069201026
