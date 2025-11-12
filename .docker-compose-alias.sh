#!/bin/bash
# Quick alias helper - source this file or add to your .bashrc/.zshrc
# Usage: After sourcing, you can use 'dc' instead of the full command

alias dc='docker compose -f config/docker-compose.yml'
alias dcu='docker compose -f config/docker-compose.yml up'
alias dcb='docker compose -f config/docker-compose.yml up --build'
alias dcd='docker compose -f config/docker-compose.yml up -d'
alias dce='docker compose -f config/docker-compose.yml exec'
alias dcdown='docker compose -f config/docker-compose.yml down'
alias dcps='docker compose -f config/docker-compose.yml ps'
alias dclogs='docker compose -f config/docker-compose.yml logs'

echo "Docker Compose aliases loaded!"
echo "  dc      - docker compose -f config/docker-compose.yml"
echo "  dcu     - docker compose up"
echo "  dcb     - docker compose up --build"
echo "  dcd     - docker compose up -d"
echo "  dce     - docker compose exec"
echo "  dcdown  - docker compose down"
echo "  dcps    - docker compose ps"
echo "  dclogs  - docker compose logs"

