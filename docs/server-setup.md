# Server Setup

Tested on Debian 12. Run once on a fresh server before first deploy.

## Requirements
- Debian 12
- Root or sudo access

## 1. Update system
sudo apt update && sudo apt upgrade -y

## 2. Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

## 3. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

## 4. Install git
sudo apt install git -y

## 5. Verify
docker --version        # expect 29+
docker compose version  # expect v5+
uv --version            # expect 0.12+
git --version