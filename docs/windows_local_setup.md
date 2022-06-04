# Windows CUDA / WSL2 / VSCode Guide

This guide will allow you to run & develop Olympus from a CUDA-compatible Windows machine. I made this because I still want to play linux-incompatible games but also develop inside UNIX. Kill me please.

This guide assumes that WSL2 will be installing Ubuntu 20.04. If this changes in the future, that's your problem.

## Install WSL 2

1. Ensure virtualization is enabled in BIOS

    - AMD: Enable **SVM**
    - Intel: Enable **VT-d/VT-x**  

2. Download the latest Nvidia drivers
3. Run Powershell as administrator, then run

        wsl.exe --install -d Ubuntu-20.04

4. Wait for installation, reboot, then setup Ubuntu user/password when prompted
    - **Note:** Sometimes Ubuntu will not auto-install. If a new unix terminal doesn't appear after startup (or the command `wsl` says "No installed distributions") then download Ubuntu 20.04 LTS from the Windows Store. 
6. Ensure WSL2 is up-to-date with

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

    ssh-keygen -t ed25519 -C "you@example.com"
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_ed25519
    cat ~/.ssh/id_ed25519.pub
    git clone git@github.com:ThatCooperLewis/olympus.git
    cd olympus
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    git config --global user.email "you@example.com"
    git config --global user.name "Your Name"

### Setup CUDA Toolkit

This process is delicate - One must be careful not to overwrite existing drivers that were imported through WSL. However, those imported drivers do not support Nvidia Toolkit. [Source](https://docs.nvidia.com/cuda/wsl-user-guide/index.html#cuda-support-for-wsl2).

Remove existing GPG Key

    sudo apt-key del 7fa2af80

Install CUDA Toolkit

    wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu.pin
    sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600
    wget https://developer.download.nvidia.com/compute/cuda/11.7.0/local_installers/cuda-repo-wsl-ubuntu-11-7-local_11.7.0-1_amd64.deb
    sudo dpkg -i cuda-repo-wsl-ubuntu-11-7-local_11.7.0-1_amd64.deb

This last `dpkg` step may warn you to install the CUDA GPG Key. If so, run this:

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
    sudo apt-get install libcudnn8 libcudnn8-dev
    rm cuda-repo-wsl-ubuntu-11-7-local_11.7.0-1_amd64.deb

## (Optional) Setup Visual Studio Code

Follow this section if you want to edit the repo within VS Code as if you're on a linux machine

### **Setup remote development**

Download & install the following

- [VS Code](https://code.visualstudio.com/download)
- [FiraCode Nerd Font](https://www.nerdfonts.com/font-downloads) 
    - Only install the font `Fira Mono Regular Nerd Font Complete Mono Windows Compatible.otf`
- [Git for Windows](https://git-scm.com/download/win)
- [Remote Development for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)

Enter Ubuntu WSL 

    cd path/to/olympus
    code .

Some things should install, then VS Code should open & connect to the WSL. No need to open Code from WSL after this first launch.

### **Fix environment**

To more easily source private keys into the WSL environment, run this in the olympus directory

    echo "source .env.production" >> venv/bin/activate

Python's environment won't automatically activate when using the WSL terminal through VS Code. To have it automatically run `source venv/bin/activate`, navigate to `~/.vscode-server/data/Machine/settings.json` and add the following:

    "python.terminal.activateEnvironment": true

Then restart the VS Code terminal.

### **Install ZSH & PowerLevel10K**

Follows [this guide](https://medium.com/@shivam1/make-your-terminal-beautiful-and-fast-with-zsh-shell-and-powerlevel10k-6484461c6efb)

    sudo apt install zsh
    chsh -s $(which zsh)
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
    git clone https://github.com/romkatv/powerlevel10k.git $ZSH_CUSTOM/themes/powerlevel10k
    git clone https://github.com/zsh-users/zsh-autosuggestions.git $ZSH_CUSTOM/plugins/zsh-autosuggestions
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git $ZSH_CUSTOM/plugins/zsh-syntax-highlighting
    nano ~/.zshrc

Add/Update the following lines, then save the file

    ZSH_THEME="powerlevel10k/powerlevel10k"
    POWERLEVEL9K_MODE="nerdfont-complete"
    ENABLE_CORRECTION="true"
    plugins=(git zsh-autosuggestions zsh-syntax-highlighting)

Enable nerd fonts:
1. Hit `Ctrl-Shift-P` in VS Code and get to Terminal: Configure Terminal Settings
2. Find `Terminal > Integrated > Font Family`
3. Enter `FiraMono NF`, Ctrl-S and restart Code

## (Optional) Setup WSL + OpenSSH

Follow this section if you want to access this machine remotely.
### WSL 2 Setup

Install and configure OpenSSH

    sudo apt install openssh-server
    sudo ssh-keygen -A
    sudo nano /etc/ssh/sshd_config

Update the following lines and save file:

    Port 2222
    ListenAddress 0.0.0.0
    PasswordAuthentication yes

Configure SSH to start without `sudo`

    sudo visudo

Add the following line after `...ALL=(ALL:ALL) ALL` and save

    %sudo ALL=NOPASSWD: /etc/init.d/ssh start

Leave WSL using `exit`

### Windows Host Setup

Wanna easily SSH into your WSL instance? Tough shit. WSL Changes IP on every cold start, so port forwarding must be dynamically changed. Download the [ssh_port_configuration](../scripts/ssh_port_config.ps1) file to your host machine, and unblock it in an Admin Powershell:

    unblock-file C:\path\to\ssh_port_configuration.ps1

Run this file to confirm no errors appear. It boots WSL, gets the IP, and exposes it to the network. If successful, you should be able to ssh from another machine using

    ssh wsluser@windowsip -p 2222

To make this run on startup:

1. Open Task Scheduler
2. Create a basic task
3. Give it a name
4. Set trigger to 'When I log on'
5. Choose 'Start a program'
    a. Program/script: `powershell.exe`
    b. Add arguments: `-file "C:\path\to\ssh_port_configuration.ps1"`
6. Select `Open the Properties dialog...` and click 'Finish'
7. In properties window
    a. Select 'Run whether user is logged in'
    b. Check 'Run with highest privileges'
8. Save & enter Windows password

### "Service" setup

Wanna use the `systemd` scripts in WSL to run on startup? Tough shit. WSL doesn't play well with `systemd`, so we must create another task.

1. Copy the powershell script(s) located in [the services/wsl direcotry](../services/wsl/) into a Windows directory
2. Follow the steps in the previous section, but choose the services script instead.