#!/bin/bash
if ! [ -d ".venv" ]; then
    echo "Creating .venv"
    python3 -m venv .venv
fi

echo "Entering .venv"
source .venv/bin/activate

echo "Installing requirements"
pip install -r requirements.txt

if ! [ -f "config.yml" ]; then
    echo "Copying default config"
    cp "default.yml" "config.yml"
fi

echo "Done."