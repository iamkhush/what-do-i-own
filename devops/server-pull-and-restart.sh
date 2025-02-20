#!/bin/bash

# Variables
SERVER_USER="ankush"
SERVER_IP="192.168.50.14"
GIT_REPO_PATH="/home/ankush/projects/what-do-i-own"
GUNICORN_SERVICE="gunicorn.service"
NGINX_SERVICE="nginx.service"

# SSH into the server and perform the operations
ssh ${SERVER_USER}@${SERVER_IP} << EOF
    cd ${GIT_REPO_PATH}
    git pull origin main
    source .venv/bin/activate
    pip install -r requirements.txt
    sudo systemctl restart ${GUNICORN_SERVICE}
    sudo systemctl restart ${NGINX_SERVICE}

echo "Git pull , Gunicorn & Nginx service restart completed on ${SERVER_IP}"