# Project explorer

Explorer of src/buid/test results.

Uses Flask to explorer via a browser.

## Install

~~~
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt 
# or
#python3 -m pip install simplepam
#python3 -m pip install svn
~~~

## Save requirements

~~~
pip freeze > requirements.txt
~~~

## Task list

  - [x] show image diffs via before/after image slider
  - [ ] add documentation (markdown files in directory)
  - [x] add project documentation (markdown files in top directory)
  - [x] support markdown files in browser
  - [x] better file browser 
  - [x] add timestamps to image results
  - [ ] compare project test with nightly build
  - [ ] faster file comparison (current lib is very slow for large files)
  - [ ] make support (only the ninja build file is checked)
  - [ ] browse diana files


