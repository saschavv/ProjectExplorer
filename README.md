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


