UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
  VENV_DIR=.venv-linux
else
  VENV_DIR=.venv-osx
endif

PYTHON := $(VENV_DIR)/bin/python
PIP    := $(VENV_DIR)/bin/pip

# =============================================================================
# One-time setup (run this after clone or when dependencies change)
# =============================================================================
submodules:
	git submodule update --init --recursive

$(VENV_DIR):
	python3 -m venv $(VENV_DIR)

init: $(VENV_DIR) submodules
	@echo ">>> Upgrading pip..."
	$(PIP) install --upgrade pip
	@echo ">>> Installing project requirements..."
	$(PIP) install -r requirements.txt
	@echo ">>> Setting up LiteX..."
	cd deps/litex && ./litex_setup.py --init --install
	@echo ">>> Done. You can now use 'make test'."

# =============================================================================
# Fast test target (does NOT run init)
# =============================================================================
test:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Error: Virtual environment not found."; \
		echo "Please run 'make init' first (only needed once)."; \
		exit 1; \
	fi
	@echo ">>> Running protocol simulation..."
	$(PYTHON) test/test_protocol.py

test-vcd: test
	@echo ">>> Opening waveform..."
	@which gtkwave >/dev/null && gtkwave protocol.vcd || \
	 which surfer  >/dev/null && surfer  protocol.vcd || \
	 echo "Install gtkwave or surfer to view the waveform."

# =============================================================================
# Other targets
# =============================================================================
local:
	jupyter-lab --ip 0.0.0.0

clean:
	rm -rf build/ __pycache__/ *.vcd *.fst

.PHONY: init submodules test test-vcd local clean

