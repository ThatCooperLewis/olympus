# Windows CUDA / WSL2 / VSCode Guide

This guide will allow you to run & develop Olympus from a CUDA-compatible Windows machine. I made this because I still want to play linux-incompatible games but also develop inside UNIX. Kill me please.

This guide assumes that WSL2 will be installing Ubuntu 20.04. If this changes in the future, that's your problem.

## Install WSL 2

1. Ensure virtualization is enabled in BIOS

    - AMD: Enable **SVM**
    - Intel: Enable **VT-d/VT-x**  

2. Download the latest Nvidia drivers
3. Run Powershell as administrator, then run

        wsl.exe --install

4. Wait for installation, reboot, then setup Ubuntu user/password when prompted 
5. Ensure WSL2 is up-to-date with

        wsl --update
        wsl --shutdown

## Install linux dependencies

Open the Ubuntu program if not already running. Run the following:

### Install Python 3.10

    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install python3.10 python3.10-venv python3.10-dev libpq-dev build-essential
    echo "alias python=\"python3.10\"" >> ~/.bashrc
    echo "alias pip=\"python3.10 -m pip\"" >> ~/.bashrc
    source ~/.bashrc

### Setup repository

    ssh-keygen -t ed25519 -C "your_email@example.com"
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_ed25519
    cat ~/.ssh/id_ed25519.pub
    git clone git@github.com:ThatCooperLewis/olympus.git
    cd olympus
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements-no-cuda.txt

### Setup CUDA Toolkit

This process is delicate - One must be careful not to overwrite existing drivers that were imported through WSL. However, those imported drivers do not support Nvidia Toolkit. [Source](https://docs.nvidia.com/cuda/wsl-user-guide/index.html#cuda-support-for-wsl2).

Remove existing GPG Key

    sudo apt-key del 7fa2af80

Install CUDA Toolkit

    wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu.pin
    sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600
    wget https://developer.download.nvidia.com/compute/cuda/11.7.0/local_installers/cuda-repo-wsl-ubuntu-11-7-local_11.7.0-1_amd64.deb
    sudo dpkg -i cuda-repo-wsl-ubuntu-11-7-local_11.7.0-1_amd64.deb

This last `dpkg` step may warn you to install the CUDA GPG Key:

    sudo cp /var/cuda-repo-wsl-ubuntu-11-7-local/cuda-B81839D3-keyring.gpg /usr/share/keyrings/

Continue installation

    sudo apt-get update
    sudo apt-get -y install cuda

### Setup cuDNN

One last nvidia library necessary for the CUDA-specialized LSTM model. [Source](https://stackoverflow.com/questions/66977227/could-not-load-dynamic-library-libcudnn-so-8-when-running-tensorflow-on-ubun).

    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
    sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600

The following command may change in the future, check for the latest `.pub` filename [here](https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/).

    sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub

Continue installation

    sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /"
    sudo apt-get update
    sudo apt-get install libcudnn8
    sudo apt-get install libcudnn8-dev

### Setup VS Code Server

1. Download & install [Git for Windows](https://git-scm.com/download/win)
2. Install VS Code and the  [Remote Development](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) extension.
3. Enter Ubuntu WSL, navigate to directory, run `code .`

Some things should install, then VS Code should open & connect to the WSL. It will behave as a normal UNIX workspace now, even when re-opening VS Code (it isn't necessary to open it via WSL).
