# Ubuntu 20.04 Installation Guide

This is a collection of instructions from [Nvidia's official docs](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html). If setting up a machine without CUDA, skip to Python Environment.

## Requirements

- Ubuntu 20.04 machine with CUDA-compatible Nvidia GPU 
  - Other operating systems may work, but the setup guide below is tailored for Linux Mint
- Nvidia Developer account
- Latest Nvidia GPU Drivers

## Pre-Installation

- Update package manager & deps for adding custom PPAs

        sudo apt update && sudo apt upgrade -y
        sudo apt install software-properties-common -y

- Ensure linux detects your Nvidia GPU. The model should be listed in [this list](https://developer.nvidia.com/cuda-gpus) of CUDA-compatible GPUs.

        lspci | grep -i nvidia

- Ensure `gcc` is installed on your machine

        gcc --version

- If not, install Ubuntu development tools

        sudo apt install build-essential 

- Install the correct linux kernel headers

        sudo apt-get install linux-headers-$(uname -r)

## Install CUDA Toolkit 11.6

    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin

    sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600

    wget https://developer.download.nvidia.com/compute/cuda/11.6.0/local_installers/cuda-repo-ubuntu2004-11-6-local_11.6.0-510.39.01-1_amd64.deb

    sudo dpkg -i cuda-repo-ubuntu2004-11-6-local_11.6.0-510.39.01-1_amd64.deb

    sudo apt-key add /var/cuda-repo-ubuntu2004-11-6-local/7fa2af80.pub

    sudo apt-get update
    
    sudo apt-get -y install cuda

## Install cuDNN

This may not work if you're not logged into the [Nvidia Developer Portal](https://developer.nvidia.com/cudnn)

    sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /"

    sudo apt-get install libcudnn8=8.3.2.44-1+cuda11.5

    sudo apt-get install libcudnn8-dev=8.3.2.44-1+cuda11.5

## Post-Installation

Update `$PATH` in either `~/.bashrc` or `~/.zshrc`

    export PATH=/usr/local/cuda-11.6/bin${PATH:+:${PATH}}

## Python Environment

If you don't have Python 3.10 & Postgres requirements installed:

    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    # Python installation
    sudo apt install python3.10
    sudo apt install python3.10-venv
    # Postgres-Python adapter prerequisites
    sudo apt install python3.10-dev libpq-dev build-essential

If python3.10 isn't found, its likely `sudo apt update` warns you that it `Could not resolve 'ppa.launchpad.net'`. Do this to fix, then install Python & Friends

    echo 'Acquire::ForceIPv4 "true";' | sudo tee /etc/apt/apt.conf.d/99force-ipv4
    sudo apt update

Ensure `pip` and `python` are aliased to 3.10 in either `~/.bashrc` or `~/.zshrc`

    echo "alias python=\"python3.10\"" >> ~/.bashrc
    echo "alias pip=\"python3.10 -m pip\"" >> ~/.bashrc
    source ~/.bashrc

Setup virtual environment & install dependencies (in repo directory)
        
    python -m venv venv
    source venv/bin/activate

If setting up a machine without CUDA capability, use `requirements-cudaless.txt` instead

    pip install -r requirements.txt

If you'd like your local env file to be automatically sourced when entering the python env, run this:

    echo "source .env.production" >> venv/bin/activate