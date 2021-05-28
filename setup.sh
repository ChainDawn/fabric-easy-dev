#/bin/bash
which virtualenv >> /dev/null
if [ $? -nq 0 ]; then
  echo "virtualenv not installed."
  exit 1
fi

if [ ! -d "venv" ]; then
  which Python3.9 >> /dev/null
  if [ $? -nq 0 ]; then
    echo "Python3.9 not found"
    exit 1
  fi
  echo "Setup python virtual env to Python3.9"
  virtualenv -p python3.9 venv
fi
source venv/bin/activate
python setup.py
if [ $? -eq 0 ]; then
  echo "Setup env success."
fi