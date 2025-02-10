install:
	pip install -e .


debug-env:
	export PATH="$HOME/.pyenv/bin:$PATH"
	eval "$(pyenv init --path)"
	eval "$(pyenv virtualenv-init -)"
	source ~/.bashrc


set-up-env:
	sudo apt-get update
	sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
	libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
	libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

	curl https://pyenv.run | bash

	export PATH="$HOME/.pyenv/bin:$PATH"
	eval "$(pyenv init --path)"
	eval "$(pyenv virtualenv-init -)"

	source ~/.bashrc

	pyenv install 3.11.0
	pyenv global 3.11.0

	pyenv virtualenv 3.11.0 SEcomp3083
	pyenv global SEcomp3083