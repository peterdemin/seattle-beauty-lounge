#!/usr/bin/env bash

set -e -o pipefail

if [ ! -e /usr/bin/certbot ]; then
    snap install --classic certbot
    ln -s /snap/bin/certbot /usr/bin/certbot
fi
certbot --non-interactive --agree-tos --nginx -m peter@seattle-beauty-lounge.com -d seattle-beauty-lounge.com -d www.seattle-beauty-lounge.com

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
mv alembic.minimal.ini ~api/alembic.ini
chown api:api ~api/alembic.ini

# Grant privileges to the user on the database
echo "Granting privileges on $DB_NAME to $DB_USER..."

sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public to $DB_USER;"

sudo tailscale up
