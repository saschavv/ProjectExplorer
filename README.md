# Project explorer

Web explorer of src/buid/test results.

## Run

First clone repository on local machine.

Manually setup environment

~~~
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt 
~~~

Then run flask

~~~
export FLASK_APP=projectexplorer.py
python3 -m flask run --host=0.0.0.0 --port=5001
~~~

There is a helper script that executes the step above:

~~~
server.sh --port=5001
~~~

## Save requirements

~~~
pip freeze > requirements.txt
~~~

## Task list

  - [x] show image diffs via before/after image slider
  - [x] add documentation (markdown files in directory)
  - [x] add project documentation (markdown files in top directory)
  - [x] support markdown files in browser
  - [x] better file browser 
  - [x] add timestamps to image results
  - [ ] compare project test with nightly build
  - [x] faster file comparison (current lib is very slow for large files)
  - [x] make support (only the ninja build file is checked)
  - [x] browse diana files
  - [ ] show changed files on the dashboard


