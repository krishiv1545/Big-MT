# Big-MT Staging Server Commands

This document contains the server-side commands and configuration paths required to run Big-MT as a staging deployment on Ubuntu Server.

## Gunicorn

**Configuration:**
`/etc/systemd/system/gunicorn_staging.service`

```bash
# Reload systemd so it picks up changes to the service file
sudo systemctl daemon-reload

# Enable the service to start automatically on boot
sudo systemctl enable gunicorn_staging

# Start the Gunicorn staging service
sudo systemctl start gunicorn_staging

# Restart the service (e.g. after a code deploy or config change)
sudo systemctl restart gunicorn_staging

# Stop the service
sudo systemctl stop gunicorn_staging

# Check current status (active/inactive, recent logs, PID)
sudo systemctl status gunicorn_staging

# Tail live logs for the service (Ctrl+C to exit)
sudo journalctl -u gunicorn_staging -f
```

## NGINX

**Configuration:**
`/etc/nginx/sites-available/bigmt_nginx_staging`

**Enable site:**
```bash
# Create a symlink so NGINX picks up this site config from sites-enabled
sudo ln -s /etc/nginx/sites-available/bigmt_nginx_staging /etc/nginx/sites-enabled/bigmt_nginx_staging
```

**Validate configuration:**
```bash
# Test NGINX config syntax before reloading/restarting (run after any config change)
sudo nginx -t
```

**Service:**
```bash
# Enable NGINX to start automatically on boot
sudo systemctl enable nginx

# Start NGINX
sudo systemctl start nginx

# Reload config without dropping active connections (use after config changes)
sudo systemctl reload nginx

# Fully restart NGINX (drops connections briefly)
sudo systemctl restart nginx

# Check current status
sudo systemctl status nginx
```

## POSTGRESQL

```bash
# Installation
sudo apt install postgresql postgresql-contrib -y

# Enable psql to start automatically on boot
sudo systemctl enable postgresql

# Start psql
sudo systemctl start postgresql

# Check current status
sudo systemctl status postgresql

# PostgreSQL console
sudo -u postgres psql
```

**Configuration**
```bash
# Create new identity in cluster (postgresql instance (:4532))
CREATE ROLE bigmt_app
    LOGIN
    PASSWORD 'password';

# Create database
CREATE DATABASE bigmt
    OWNER bigmt_app;
```

**Meta commands**
```bash
# List databases (names & ownership)
\l

# List users/roles
\du
\du <role>

# List all user tables in current connected schema
\dt

# \dt with more info (disk space, etc.)
\dt+

# All schemas inside current db
\dn

# List functions
\df

# Describe table metadata
\d <table_name>

# Connect to db as current user
\c <dbname>

# Connect to db as a particular user
\c <dbname> <username>

# Describe active host/port/socket/dbname
\conninfo

# Exit
\q
```

**postgresql.conf**
```bash
# psql version=16; cluster name=main
sudo nano /etc/postgresql/16/main/postgresql.conf

# Set IP addr. under 'Connections And Authentication' section (eg., Tailscale IP)
listen_addresses = '100.100.00.00'

# psql = client, PostgreSQL = server (program actually running the databases)
# psql -> "192.100.1.10:5432" (server) (e.g., "psql -h 192.168.1.10 -p 5432")
# listen_address is where PostgreSQL can listen to
# e.g., "100.100.0.10:5432" if it was the Tailscale IP of server,
# then it wont accept connections through IPv4, only the tailscale IP.
```

**pg_hba.conf**
```bash
# Find pg_hba.conf file
sudo -u postgres psql -c "SHOW hba_file;"

sudo nano /etc/postgresql/16/main/pg_hba.conf

# Add a new rule (learnt subnetting because of this b.s. ngl, very cool)
host    bigmt    bigmt_app    100.100.00.00/32    scram-sha-256

# Reload
sudo systemctl reload postgresql

# Expected output is 't'
sudo -u postgres psql -c "SELECT pg_reload_conf();"

# Test connection
psql -h <your_magic_dns>.ts.net -U bigmt_app -d bigmt
Password for user bigmt_app:
```