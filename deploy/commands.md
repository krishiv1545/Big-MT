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

## Docker Daemon

**Service:**
```bash
# Enable dockerd to start automatically on boot
sudo systemctl enable docker

# Start dockerd
sudo systemctl start docker

# Check current status
sudo systemctl status docker
```