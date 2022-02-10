# Cryptographer
Bitcoin price approximation & trading

## Requirements

- Ubuntu 20.04 machine with CUDA-compatible Nvidia GPU 
  - Other operating systems may work, but the setup guide below is tailored for Linux Mint
- Visual Studio Code
- Crosstower trading account w/ API Key
- Nvidia Developer account

## Setup

- Update to latest Nvidia Drivers

- Setup Ubuntu CUDA, following all steps [here](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#ubuntu-installation) including pre- and post-installation instructions
  - CUDA Toolkit Parameters
    - Distro: `ubuntu2004`
    - Version: `11-6`
    - Arch: `x86_64`

- **Do not define any environment variables mentioned in the Nvidia guides, except for the following $PATH update.** Defining `LD_LIBRARY_PATH` should not be necessary if you use the Ubuntu `.deb` installations.

      export PATH=/usr/local/cuda-11.6/bin${PATH:+:${PATH}

- Install `libcudnn8`

      $ sudo apt install libcudnn8

- Setup virtual environment & install dependencies (in repo directory)
        
      $ python -m venv venv
      $ source venv/bin/activate
      $ pip install -r requirements.txt

TODO - Crosstower API Setup, credentials.json

## Components

### Crosstower

- TODO - SDK description

### Cryptographer

To make things a little more difficult for those who lack the sheer will to make this code work for themselves, I obscured all the components with Greek Mythology codewords

- **Olympus** : Creates & manages all entities

- **Athena** : Scrapes price data from CrossTower API

- **Prometheus** : Trains a keras model based on Athena's historical price data

- **Delphi** : Utilizes latest price history & the Prometheus model to make predictions

- **Hermes** : Intakes predictions from Delphi and makes market orders based on its recommendations 

## Tools

- `tools/filter_csv.py`
        
  - Used to reduce historical data into larger granuels. Data with sporadic timing can be filtered to regular segments of time.
  - Expects a CSV with two columns: "timestamp" and "price". Both should be numberical. Timstamp should be epoch seconds.
