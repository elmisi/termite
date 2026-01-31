#!/bin/bash
set -e

cd "$(dirname "$0")"

# Carica configurazione da .env se esiste
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Warning: .env not found. Copy .env.example to .env and configure it."
    exit 1
fi

# Crea virtual env se non esiste
if [ ! -d "venv" ]; then
    echo "Creazione virtual environment..."
    python3 -m venv venv
fi

# Attiva virtual env
source venv/bin/activate

# Installa dipendenze
echo "Installazione dipendenze..."
pip install -e . --quiet

# Disabilita altri provider LLM
unset OPENAI_API_KEY
unset ANTHROPIC_API_KEY
export OLLAMA_MODEL="${CODING_MODEL}"

# Lancia termite
echo "Avvio termite..."
echo "  Host: ${OLLAMA_HOST}"
echo "  Reasoning: ${REASONING_MODEL}"
echo "  Coding: ${CODING_MODEL}"
termite --library "${LIBRARY}" \
    --reasoning-model "${REASONING_MODEL}" \
    --coding-model "${CODING_MODEL}" \
    "$@"
