#!/usr/bin/bash
scriptdir=$(dirname $0)

# Create python virtual env if not there yet (e.g. after fresh clone of repo)
if [ ! -d $scriptdir/venv ]; then
  (cd $scriptdir; python3 -m venv venv)
  source $scriptdir/venv/bin/activate
  pip install -r requirements.txt
else
  # Just activate the python virtual env
  source $scriptdir/venv/bin/activate
fi

export FLASK_APP=projectexplorer.py 
# $@ allows passing --port and/or other options
python3 -m flask run --host=0.0.0.0 "$@"

