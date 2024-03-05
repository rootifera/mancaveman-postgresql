#!/bin/bash

ENV_FILE="./.env"

print_color() {
    COLOR="$1"
    TEXT="$2"
    echo -e "${COLOR}${TEXT}${NC}"
}

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Colour

print_separator() {
    print_color "$BLUE" "===================================================="
}

if [ ! -f "$ENV_FILE" ]; then
    print_color "$YELLOW" "Creating .env file..."
    print_separator

    POSTGRES_USER=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 8)
    POSTGRES_PASSWORD=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 12)
    POSTGRES_DB="cavedb"
    REDIS_URL="redis://redis"
    SECRET_KEY=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 64)
    ALGORITHM="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES="60"
    REFRESH_TOKEN_EXPIRE_HOURS="72"
    PORT="8080"

    cat <<EOF > "$ENV_FILE"
### Database Config ###
POSTGRES_DB=$POSTGRES_DB
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
SQLALCHEMY_DATABASE_URL=postgresql://\${POSTGRES_USER}:\${POSTGRES_PASSWORD}@postgres/\${POSTGRES_DB}
REDIS_URL=$REDIS_URL
### Keys and Authentication ###
SECRET_KEY=$SECRET_KEY
ALGORITHM=$ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES=$ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_HOURS=$REFRESH_TOKEN_EXPIRE_HOURS
### Server Config (See README.md) ###
PORT=$PORT
EOF

    print_separator
    print_color "$GREEN" "########## .env file created successfully. ##########"
else
    print_color "$YELLOW" "########## .env file already exists. Skipping creation. ##########"
fi

print_separator

print_color "$BLUE" "########## Pulling Docker Images ##########"
docker compose pull || print_color "$RED" "Failed to pull Docker images!"

print_separator

print_color "$BLUE" "########## Starting the Application in 3 Seconds... ##########"
print_color "$YELLOW" "########## CTRL-C To Interrupt ##########"
sleep 3
docker compose up -d || print_color "$RED" "Failed to start the application!"

print_separator
print_color "$GREEN" "########## Application Started Successfully ##########"
