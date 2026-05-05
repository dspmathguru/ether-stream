# ether-stream.bashrc
export PROJECT_ROOT="$PWD"

# Add LiteX to PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT/deps/litex:$PYTHONPATH"

# Add your own code paths (useful for imports)
export PYTHONPATH="$PROJECT_ROOT/ckts:$PROJECT_ROOT/test:$PYTHONPATH"

# Activate the correct virtualenv
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "[ether-stream] Linux detected"
    source "$PROJECT_ROOT/.venv-linux/bin/activate"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "[ether-stream] macOS detected"
    source "$PROJECT_ROOT/.venv-osx/bin/activate"
fi

