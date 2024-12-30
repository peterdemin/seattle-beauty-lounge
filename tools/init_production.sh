#!/usr/bin/env bash

set -e -o pipefail

curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/noble.noarmor.gpg | tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/noble.tailscale-keyring.list | tee /etc/apt/sources.list.d/tailscale.list

apt-get update
apt-get upgrade -y
apt-get install -y \
    ca-certificates \
    curl \
    nginx \
    rsync \
    python3 \
    python3.12-venv \
    python-is-python3 \
    postgresql \
    postgresql-contrib \
    tailscale

if [ ! -e /usr/bin/certbot ]; then
    snap install --classic certbot
    ln -s /snap/bin/certbot /usr/bin/certbot
fi
certbot --non-interactive --agree-tos --nginx -m peter@seattle-beauty-lounge.com -d seattle-beauty-lounge.com

# Variables for database and user
DB_NAME="api"
DB_USER="api"
DB_PASSWORD="password"

# Check if the database exists
DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';")
if [ "$DB_EXISTS" != "1" ]; then
  echo "Creating database $DB_NAME..."
  sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
else
  echo "Database $DB_NAME already exists."
fi

# Check if the user exists
USER_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER';")
if [ "$USER_EXISTS" != "1" ]; then
  echo "Creating user $DB_USER..."
  sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
else
  echo "User $DB_USER already exists."
fi

# Grant privileges to the user on the database
echo "Granting privileges on $DB_NAME to $DB_USER..."

sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public to $DB_USER;"

sudo tailscale up
