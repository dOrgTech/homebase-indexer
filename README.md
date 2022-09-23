# Homebase App Indexer

## Related repositories

1. [homebase-app](https://github.com/dOrgTech/homebase-app) Front-end
2. [base-dao-dockerized](https://github.com/dOrgTech/baseDAO-dockerized)

## Setup Dev Environment

### Requirements

Have python >= 3.10.4 installed

### Virtual environment

Depending on your python binary PATH
Step 1:

```
$ python -m venv venv`
```

or

```
`$ python3 -m venv venv`
```

Step 2:

```
$ source venv/bin/activate
```

### Install dependencies

```
$ pip install -r requirements.txt
```

or

```
$ make install
```

### Create PGDB docker container

```
docker network create mnetwork
postgres -  docker run --network=mnetwork --name hb-indexer-postgres -p 5432:5432 -e POSTGRES_USER=indexer -e POSTGRES_PASSWORD=qwerty -e POSTGRES_DB=indexer_db  -d postgres
```

### Environment Variables

```
$ cp .env.example .env
```

### Runing the indexer

```
$ dipdup -e .env run
```

or

```
make start
```
