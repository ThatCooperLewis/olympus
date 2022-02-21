# Olympus
Bitcoin price approximation & trading

## Requirements

- Ubuntu 20.04 machine with CUDA-compatible Nvidia GPU 
  - Other operating systems may work, but the setup guide below is tailored for Linux Mint
- Visual Studio Code
- Crosstower trading account w/ API Key
- Nvidia Developer account

## Setup

For running on a local Ubuntu machine, [refer to this guide](docs/local_setup.md)

TODO - Crosstower API Setup, credentials.json

## Components

### Crosstower API

- TODO - SDK description

### The Olympians

To make things a little more difficult for those who lack the sheer will to make this code work for themselves, I obscured all the components with Greek Mythology codewords

- **Zeus** : Manages all entities

- **Athena** : Scrapes price data from CrossTower API

- **Prometheus** : Trains a keras model based on Athena's historical price data

- **Delphi** : Utilizes latest price history & the Prometheus model to make predictions

- **Hermes** : Intakes predictions from Delphi and makes market orders based on its recommendations 

- **PrimordialChaos** : Superclass of all others, manages starting/stopping of threads and handles alerts

## Tools

- `tools/filter_csv.py`
        
  - Used to reduce historical data into larger granuels. Data with sporadic timing can be filtered to regular segments of time.
  - Expects a CSV with two columns: "timestamp" and "price". Both should be numberical. Timstamp should be epoch seconds.
