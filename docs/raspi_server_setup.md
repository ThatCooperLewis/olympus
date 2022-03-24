# Raspberry Pi Server Installation

Similar to the local setup guide, this is a walkthrough of vanilla ubuntu server -> functioning services.

### Create SSH key & Add to Github 

    ssh-keygen -t ed25519 -C "your_email@example.com"
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_ed25519
    cat ~/.ssh/id_ed25519.pub
    git clone git@github.com:ThatCooperLewis/olympus.git

### Install Python 3.10

    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    # Python installation
    sudo apt install python3.10 python3.10-venv python3.10-dev libpq-dev build-essential

### Add aliases to .bashrc

    echo "alias python=\"python3.10\"" >> ~/.bashrc
    echo "alias pip=\"python3.10 -m pip\"" >> ~/.bashrc
    source ~/.bashrc

### Setup Python Environment

    cd olympus
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements-no-cuda.txt

### Enable desired service

    ./scripts/setup_systemd_service.sh service_name.service