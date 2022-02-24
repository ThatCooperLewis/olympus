# PostgreSQL Remote Server

Install PostgreSQL on a server via SSH, for collecting & storing price data. [Mostly taken from this guide](https://blog.logrocket.com/setting-up-a-remote-postgres-database-server-on-ubuntu-18-04/)

## Requirements

- Remote server running Ubuntu Server 20.04 or something similarly compatible
- That server's IPv4 IP address

## Install Postgres

    ssh <server_user>@<server_ip>
    sudo apt-get update
    sudo apt-get install postgresql postgresql-contrib

## Configure server

Assume postgres user role 

    sudo -i -u postgres

Create a new user for logging in remotely

    createuser --interactive --pwprompt

Create a new database for that user

    createdb -O <user_name> <db_name>

## Remote access config

Edit this file

    nano /etc/postgresql/10/main/postgresql.conf

Change this line:

    #listen_addresses = 'localhost'

Into this, then save and exit

    listen_addresses = '*'

Edit this file

    nano /etc/postgresql/10/main/pg_hba.conf

Change this:

    # IPv4 local connections:
    host    all             all             127.0.0.1/32            md5

Into this, then save and exit

    # IPv4 local connections:
    host    all             all             0.0.0.0/0            md5

Exit postgres user, expose default port to the network, and restart postgres

    exit
    sudo ufw allow 5432/tcp
    sudo systemctl restart postgresql

## Client connection

To access the database from another CLI:

    sudo apt-get update
    sudo apt-get install postgresql postgresql-contrib
    psql -h <server_ip> -d <db_name> -U <user_name>

[TablePlus](https://tableplus.com/) is a pretty nice GUI to interact with the server. Available on macOS/linux/windows.