# Homebase Indexer

## Overview
**Homebase Indexer** is a specialized tool crafted using DipDup, Tezos's Python framework. It serves as an equivalent to [a subgraph](https://thegraph.com/) and provides a GraphQL API, enabling efficient interaction with the Tezos blockchain. Primarily driven by the `dipdup.yml` file, it efficiently handles contract events. The main branches for the current version are `v3-master` and `v3-develop` (production and development respectively), although version 2 branches are still maintained for some DAOs that have not transitioned to version 3.

## Prerequisites
Before installing Homebase Indexer, ensure you have the following:
- Python 3.8 or higher
- Docker and Docker Compose
- Basic understanding of blockchain concepts and Tezos

## Installation and Setup
1. **Clone the Repository**: `git clone https://github.com/dOrgTech/homebase-indexer.git -b v3-develop`
2. **Navigate to the Project Directory**: `cd homebase-indexer`
3. **Build the Docker Image**: `docker build -t homebase-indexer .`
4. **Initialize Using Docker Compose**: `docker-compose up`

## Usage
To run the Homebase Indexer:
```
docker-compose up
```
This will start the indexer and initiate syncing with the Tezos node as per the configuration.

## Configuration
Configure the indexer using the `dipdup.yml` file. For advanced settings and customization, refer to the [DipDup's documentation](https://docs.dipdup.io).

## Contribution Guidelines
Contributions are welcome! To contribute:
1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Open a pull request

## Troubleshooting
- **Issue**: Docker build fails.
  **Solution**: Ensure Docker is running and you have the necessary permissions.

- **Issue**: Indexer not syncing.
  **Solution**: Check the `dipdup.yml` configuration and ensure network connectivity.

## License
Homebase Indexer is licensed under [MIT License](LICENSE).