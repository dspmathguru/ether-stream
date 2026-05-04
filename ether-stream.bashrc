export PATH=$PATH:$PWD/bin:$PWD/test

if [[ "$OSTYPE" == "linux-gnu" ]]; then
  echo "Linux"
  source .venv-linux/bin/activate
else
  echo "OSX"
  source .venv-osx/bin/activate
fi
