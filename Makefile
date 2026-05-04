UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
  VENV_DIR=.venv-linux
else
  VENV_DIR=.venv-osx
endif

init: $(VENV_DIR)
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install --upgrade -r requirements.txt
	#./scripts/install_cv2.sh

local:
	jupyter-lab --ip 0.0.0.0

$(VENV_DIR):
	python3 -m venv $(VENV_DIR)

