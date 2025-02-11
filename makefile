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


# Target: setup
# Installs system dependencies and pyenv (if not already installed)
setup:
	@echo "Updating system and installing build dependencies..."
	sudo apt-get update
	sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
		libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev \
		libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
	@echo "Installing pyenv..."
	# This script installs pyenv; if already installed, you might want to skip or check first
	curl https://pyenv.run | bash
	@echo "Setting up pyenv in ~/.bashrc (if not already present)..."
	@grep -qxF 'export PATH="$$HOME/.pyenv/bin:$$PATH"' ~/.bashrc || echo 'export PATH="$$HOME/.pyenv/bin:$$PATH"' >> ~/.bashrc
	@grep -qxF 'eval "$$(pyenv init --path)"' ~/.bashrc || echo 'eval "$$(pyenv init --path)"' >> ~/.bashrc
	@grep -qxF 'eval "$$(pyenv virtualenv-init -)"' ~/.bashrc || echo 'eval "$$(pyenv virtualenv-init -)"' >> ~/.bashrc
	@echo "Reload your shell or run 'source ~/.bashrc' to complete the pyenv setup."
	@echo "Installing Python 3.11.0 via pyenv (if not already installed)..."
	pyenv install 3.11.0 || echo "Python 3.11.0 is already installed."
	@echo "Creating virtual environment 'SEcomp3083' via pyenv..."
	pyenv virtualenv 3.11.0 SEcomp3083 || echo "Virtual environment 'SEcomp3083' already exists."
	@echo "Setting local pyenv version to 'SEcomp3083' for this project..."
	pyenv local SEcomp3083




# Target: activate
# Prints instructions for activating the virtual environment.
# (Note: 'source' in a make target will not affect your current shell.)
activate:
	@echo "To activate your virtual environment, run the following command in your shell:"
	@echo "source $$(pyenv root)/versions/SEcomp3083/bin/activate"




EC2-connect:
	ssh -i "aws-flask.pem" ubuntu@ec2-13-60-43-45.eu-north-1.compute.amazonaws.com