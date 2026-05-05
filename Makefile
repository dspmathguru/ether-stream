UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
  VENV_DIR=.venv-linux
else
  VENV_DIR=.venv-osx
endif

PYTHON := $(VENV_DIR)/bin/python
PIP    := $(VENV_DIR)/bin/pip
COCOTB_DIR := test

# =============================================================================
# One-time setup
# =============================================================================
submodules:
	git submodule update --init --recursive

$(VENV_DIR):
	python3 -m venv $(VENV_DIR)

init: $(VENV_DIR) submodules
	@echo ">>> Upgrading pip..."
	$(PIP) install --upgrade pip
	@echo ">>> Installing requirements..."
	$(PIP) install -r requirements.txt
	@echo ">>> Setting up LiteX..."
	cd deps/litex && ./litex_setup.py --init --install
	@echo ">>> Done."

# =============================================================================
# Fast targets (do NOT re-run init)
# =============================================================================
test:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Error: Run 'make init' first"; exit 1; \
	fi
	$(PYTHON) test/test_protocol.py

test-vcd: test
	@if command -v surfer >/dev/null; then surfer protocol.vcd; \
	elif command -v gtkwave >/dev/null; then gtkwave protocol.vcd; \
	else echo "Install surfer or gtkwave"; fi

# cocotb target - does NOT depend on init
cocotb:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Error: Virtualenv not found. Run 'make init' first."; \
		exit 1; \
	fi
	@echo ">>> Running cocotb + Verilator test..."
	cd $(COCOTB_DIR) && $(MAKE)

cocotb-clean:
	cd $(COCOTB_DIR) && $(MAKE) clean

clean:
	rm -rf build/ __pycache__/ *.vcd *.fst sim_build/ results.xml

.PHONY: init submodules test test-vcd cocotb cocotb-clean clean

