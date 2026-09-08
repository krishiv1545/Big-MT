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

**Backup**
```bash
# Create backup directory
sudo mkdir -p /var/backups/postgresql/bigmt

# Update permissions
sudo chmod 700 /var/backups/postgresql/bigmt
# 7 = owner
# 0 = group
# 0 = others
#
# 4 = read
# 2 = write
# 1 = execute
#
# 1 + 2 + 4 = 7

# Change owner (chown)
sudo chown postgres:postgres /var/backups/postgresql/bigmt
```

**PgBackRest**
```bash
# Install
sudo apt install pgbackrest

# Create directories for PgBR repository data & logs
sudo mkdir -p /var/backups/pgbackrest
sudo mkdir -p /var/log/pgbackrest

# Change owner (chown)
sudo chown -R postgres:postgres /var/backups/pgbackrest
sudo chown -R postgres:postgres /var/log/pgbackrest

# Change permissions
sudo chmod 750 /var/backups/pgbackrest # No write access for 'postgres' group
sudo chmod 750 /var/log/pgbackrest     # No write access for 'postgres' group

# Update pgbackrest.conf
sudo nano /etc/pgbackrest.conf
```

Final content should be following:-

```conf
[global]
repo1-path=/var/lib/pgbackrest
repo1-retention-full=2
#repo1-cipher-pass=...
#repo1-cipher-type=aes-256-cbc
repo1-retention-diff=4

log-level-console=info
log-level-file=detail
log-path=/var/log/pgbackrest

start-fast=y
delta=y

#[main]
#pg1-path=/var/lib/postgresql/13/main

[bigmt]
pg1-path=/var/lib/postgresql/16/main
```

bigmt is a new 'stanza' that just represents a cluster
repo1-retention-full --> how many full backups
repo1-retention-diff --> how many differential backups (only backup diffs since last full backup)
pg1-path --> stanza location

```bash
# Update permissions
sudo chmod 640 /etc/pgbackrest.conf

# Initialize stanza
sudo -u postgres pgbackrest --stanza=bigmt stanza-create

# psql version=16; cluster name=main
sudo nano /etc/postgresql/16/main/postgresql.conf

# Set archive_mode and archive_command under 'Write-Ahead Log' section
archive_mode = on
archive_command = 'pgbackrest --stanza=bigmt archive-push %p'

# Restart and check
sudo -u postgres pgbackrest --stanza=bigmt check

# Take a full backup
sudo -u postgres pgbackrest --stanza=bigmt backup --type=full
# incr (default) -> incremental
# diff -> differential

sudo -u postgres pgbackrest --stanza=bigmt info
```

**Automate**
```bash
# Create a FULL BACKUP service
sudo nano /etc/systemd/system/pgbackrest-bigmt-full.service
```
Content:-
```conf
[Unit]
Description=Big-MT PostgreSQL full backup
Wants=postgresql.service
After=postgresql.service

[Service]
Type=oneshot
User=postgres
ExecStart=/usr/bin/pgbackrest --stanza=bigmt backup --type=full
```

```bash
# Create a DIFFERENTIAL BACKUP service
sudo nano /etc/systemd/system/pgbackrest-bigmt-diff.service
```
Content:-
```conf
[Unit]
Description=Big-MT PostgreSQL differential backup
Wants=postgresql.service
After=postgresql.service

[Service]
Type=oneshot
User=postgres
ExecStart=/usr/bin/pgbackrest --stanza=bigmt backup --type=diff
```

```bash
# Create a timer for FULL backup
# "pgbackrest --stanza=bigmt backup --type=full"
sudo nano /etc/systemd/system/pgbackrest-bigmt-full.timer
```
Content:-
```conf
[Unit]
Description=Weekly Big-MT PostgreSQL full backup

[Timer]
OnCalendar=Sun 03:00
Persistent=true
Unit=pgbackrest-bigmt-full.service

[Install]
WantedBy=timers.target
```

```bash
# Create a timer for DIFFERENTIAL backup
# "pgbackrest --stanza=bigmt backup --type=diff"
sudo nano /etc/systemd/system/pgbackrest-bigmt-diff.timer
```
Content:-
```conf
[Unit]
Description=Daily Big-MT PostgreSQL differential backup

[Timer]
OnCalendar=Mon..Sat 03:00
Persistent=true
Unit=pgbackrest-bigmt-diff.service

[Install]
WantedBy=timers.target
```

`Persistent=true` means that if the server is powered off when the scheduled time passes, systemd will run the missed backup when the server comes back online.
`Unit=` tells which service the timer needs to trigger.

```bash
# Reload and enable
sudo systemctl daemon-reload
sudo systemctl enable --now pgbackrest-bigmt-full.timer
sudo systemctl enable --now pgbackrest-bigmt-diff.timer
```

**Disaster Recovery**
```bash
# now() returns current timestamp; pg_current_wal_lsn() --> "1/8001878",
# 1 refers to file's logical ID, 8001878 is byte-offset, 
# it's a hex representing exact byte where Postgres will write it's next log
sudo -u postgres psql -d bigmt -c "SELECT now(), pg_current_wal_lsn();"

# pg_switch_wal() forces Postgres to close current WAL file and start fresh with new 16mb segment
sudo -u postgres psql -d bigmt -c "SELECT pg_switch_wal();"

# To make sure all WAL segments reached repo (disk, S3, etc.)
sudo -u postgres pgbackrest --stanza=bigmt check

# Stop everything so no data is further written to Postgres
sudo systemctl stop gunicorn_staging
sudo systemctl stop postgresql

# Verify Postgres is down
pg_lsclusters

# Rename database directory (backup of damaged main, basically)
sudo mv /var/lib/postgresql/16/main /var/lib/postgresql/16/main-after-disaster

# Create fresh database directory to recover into
sudo mkdir /var/lib/postgresql/16/main
sudo chown postgres:postgres /var/lib/postgresql/16/main
sudo chmod 700 /var/lib/postgresql/16/main

# Get SET value of latest differential backup
sudo -u postgres pgbackrest --stanza=bigmt info

# Restore
# Set comes from info command
# Target is the choice of PITR (Point-in-time Recovery)
# This automatically recovers FULL BACKUP + last DIFFERENTIAL BACKUP + archived WAL logs upto target
sudo -u postgres pgbackrest \
    --stanza=bigmt \
    --set=20260905-065422F_20260908-030000D \
    --type=time \
    --target="2026-09-08 04:42:00+00" \
    --target-action=promote \
    --pg1-path=/var/lib/postgresql/16/main \
    restore

# Restart Postgres
sudo systemctl start postgresql
```