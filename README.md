# Olympus
Bitcoin price approximation & trading

## Requirements

- Ubuntu 20.04 or Windows 11 machine with CUDA-compatible Nvidia GPU 
- Visual Studio Code
- Crosstower trading account w/ API Key
- Nvidia Developer account

## Installation Guides

- [Ubuntu Local Setup](docs/ubuntu_local_setup.md)
- [Windows Local Setup](docs/windows_local_setup.md)
- [Raspberry Pi Server](docs/raspi_server_setup.md)
- [Postgres Server](docs/postgres_server_setup.md)
- [Crosstower account]()

## Components

### The Olympians

To make things a little more difficult for those who lack the sheer will to make this code work for themselves, I obscured all the components with Greek Mythology codewords

- **Zeus** : Manages all entities

- **Athena** : Scrapes price data from CrossTower API

- **Prometheus** : Trains a keras model based on Athena's historical price data

- **Delphi** : Utilizes latest price history & the Prometheus model to make predictions

- **Hermes** : Intakes predictions from Delphi and makes market orders based on its recommendations 

- **PrimordialChaos** : Superclass of all others, manages starting/stopping of threads and handles alerts

## Docker Containers

All services are run using docker-compose, because I hate myself and can't be bothered to learn Terraform or any other alternative for this.

To run the services, you'll need Docker and `docker-compose` installed, which are included in [Docker Desktop](https://www.docker.com/products/docker-desktop/). Then, run this command..

      docker-compose --env-file .env.production up -d

This will initialize a Postgres DB, create the proper tables/webportal, and run the app's services once the DB is healthy.

## Tools

- `tools/filter_csv.py`
        
  - Used to reduce historical data into larger granules. Data with sporadic timing can be filtered to regular segments of time.
  - Expects a CSV with two columns: "timestamp" and "price". Both should be numerical. Timestamp should be epoch seconds.
