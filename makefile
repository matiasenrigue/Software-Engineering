SHELL := /bin/bash  # Ensure we're using bash, since our commands are bash-specific


.PHONY: setup install activate debug-env


install:
	@echo "Installing package in editable mode..."
	pip install -e .


debug-env:
	@echo "=== Debug Environment ==="
	@echo "PATH: $$PATH"
	@echo "pyenv root: $$(pyenv root)"
	@echo "Python version: $$(python --version)"
	@echo "Virtualenvs available:"
	@pyenv virtualenvs
	@echo "Local pyenv version:"
	@pyenv version
	@echo "=== End Debug ==="



setup:
	@echo "Updating system and installing build dependencies..."
	sudo apt-get update
	sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
		libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev \
		libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
	sudo apt-get install default-libmysqlclient-dev 
	@echo "Installing pyenv..."
	if [ ! -d "$$HOME/.pyenv" ]; then \
	  curl https://pyenv.run | bash; \
	else \
	  echo "pyenv already installed, skipping installation."; \
	fi
	@echo "Setting up pyenv environment in this shell..."
	# Set the necessary environment variables explicitly
	export PYENV_ROOT="$$HOME/.pyenv"; \
	export PATH="$$PYENV_ROOT/bin:$$PATH"; \
	# Optionally, you could source your ~/.bashrc if it sets these variables
	source ~/.bashrc; \
	\
	echo "Installing Python 3.11.0 via pyenv (if not already installed)..."; \
	pyenv install 3.11.0 || echo "Python 3.11.0 is already installed."; \
	echo "Creating virtual environment 'SEcomp3083' via pyenv..."; \
	pyenv virtualenv 3.11.0 SEcomp3083 || echo "Virtual environment 'SEcomp3083' already exists."; \
	echo "Setting local pyenv version to 'SEcomp3083' for this project..."; \
	pyenv local SEcomp3083






# Target: activate
# Prints instructions for activating the virtual environment.
# (Note: 'source' in a make target will not affect your current shell.)
activate:
	@echo "To activate your virtual environment, run the following command in your shell:"
	@echo "source $$(pyenv root)/versions/SEcomp3083/bin/activate"
	source $$(pyenv root)/versions/SEcomp3083/bin/activate

