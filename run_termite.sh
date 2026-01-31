#!/bin/bash
set -e

cd "$(dirname "$0")"

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

# Configura Ollama con gemma3
unset OPENAI_API_KEY
unset ANTHROPIC_API_KEY
export OLLAMA_MODEL=qwen2.5-coder:14b

# Lancia termite con eventuali argomenti passati allo script
echo "Avvio termite con Ollama qwen2.5-coder:14b..."
termite --library rich "$@"
