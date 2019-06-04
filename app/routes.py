from flask import Flask, session, redirect, url_for, escape, request, render_template, send_file, send_from_directory, jsonify, flash
from simplepam import authenticate
from functools import wraps
from shutil import copyfile

import os
import os.path, time

from app.forms import LoginForm
from app.models import TestModel
from app.collect import *
from app.modify import *

from app import app


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

def userName():
  if 'username' in session:
    return session['username']
  return ''

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def injectForTemplates():
  return dict( globs= { 'user' : userName() } )

#----------------------------------------------------------------------
@app.route('/')
@app.route('/index')
@login_required
def index():
    projectNames = getProjectNames()
    model = getProjectModelsByName( projectNames, userName() )
    return render_template('index.html', title='Home', projects=model )

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
      username = form.username.data
      password = form.password.data
      # User simple pam authentication.
      if authenticate(str(username), str(password)):
        session['username'] = username
        return redirect(url_for('index'))
      else:
        flash('Invalid username or password')
        return redirect( url_for( 'login' ) )

    return render_template( 'login.html', title='Sign in', form=form )

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/failedtests/<string:project>')
@login_required
def failedTests( project ):
    pl = ProjectLocator( project, userName() )
    model = getTestModels( pl )
    return render_template('failedtests.html', tests=model, project=project, 
         title='Overview failed tests')

@app.route('/testoutput/<string:project>/<path:test>')
@login_required
def testoutput(project, test):
    pl = ProjectLocator( project, userName() )
    # Handle squish test via squish helpers.
    if 'Squish' in test:
      makeSquishOutput( pl, test ) 
      fileName = os.path.join( test + '.dir', 'results.html' )
      fullpath = os.path.join( pl.testdir, fileName )
      return send_file( fullpath )
 
    testOutput = getTestOutput( pl, test )
    return render_template('testoutput.html', testname=test, tests=testOutput, project=project, 
         title='Test difference')


@app.route('/img/<string:project>/<string:context>/<path:filename>')
@login_required
def sendImage(project, context, filename):
  if not filename.endswith('png'):
    return 'Only png files are supported'

  pl = ProjectLocator( project, userName() )

  if context == 'src':
    folder = pl.srcdir
    imageFile = os.path.join( folder, filename )
    if os.path.exists( imageFile ):
      return send_file( imageFile )
  if context == 'test':
    folder = pl.testdir
    imageFile = os.path.join( folder, filename )
    if os.path.exists( imageFile ):
      return send_file( imageFile )

  return 'invalid context'
   
@app.route('/accepttext', methods=['POST'])
@login_required
def acceptText():
    project = request.form.get('project')
    test = request.form.get('test')
    pl = ProjectLocator( project, userName() )

    r = copyTestOutput( pl, test )
    flash( r['message'] )

    return redirect( '/testoutput/' + project + "/" + test )

@app.route('/acceptimg', methods=['POST'])
@login_required
def acceptImg():
    project = request.form.get('project')
    org = request.form.get('input')
    test = request.form.get('test')
    out = request.form.get('output')
    pl = ProjectLocator( project, userName() )

    fullOrg = os.path.join( pl.srcdir, org )
    fullOut = os.path.join( pl.testdir, out )

    r = copyTestFile( pl, fullOut, fullOrg )

    flash( r['message'] )

    return redirect( '/testoutput/' + project + "/" + test )

@app.route('/status')
@login_required
def status():
  projectNames = getProjectNames()
  models = getProjectModelsByName( projectNames, userName() )
  status = []
  for model in models:
    info = {
     'name' : model.locator.project,
     'numberoferrors' : model.testInfo.numberOfFailedTests,
     'numberoftests': model.testInfo.numberOfTests,
     'last_modified': model.buildInfo.lastModified
    }
    status.append( info )
  return jsonify( status )

#
# Browser routines
#
def browse( browser, project, folder, path ):
  if path != None:
    fullPath = os.path.join( folder, path )
  else:
    fullPath = folder
  if os.path.realpath( fullPath ) !=  fullPath :
    return "no directory traversal please."

  if os.path.isdir( fullPath ):
    itemList = os.listdir( fullPath )
    itemList.sort()
    return render_template('browse.html', title='browser', 
              project=project, path=path, itemList=itemList, browser=browser)

  if os.path.isfile(fullPath):
    imgFile = [ '.png' ]
    if any( fullPath.endswith( ext ) for ext in imgFile ):
      # return image.
      return send_file( fullPath )
    textFile = [ '.h', '.cpp', '.run', '.xml', '.py', '.res', '.log' ]
    if any( fullPath.endswith( ext ) for ext in textFile ):
      # do some code hightlight
      data = ''
      with open(fullPath, 'r') as file:
        data = file.read()
        return render_template('code.html', title='browser',
               currentFile=fullPath, code=data)

    fileProperties = {"filepath": fullPath}
    sbuf = os.fstat(os.open(fullPath, os.O_RDONLY)) #Opening the file and getting metadata
    fileProperties['type'] = stat.S_IFMT(sbuf.st_mode) 
    fileProperties['mode'] = stat.S_IMODE(sbuf.st_mode) 
    fileProperties['mtime'] = sbuf.st_mtime 
    fileProperties['size'] = sbuf.st_size 
    return render_template('file.html', title='file properties',
           currentFile=fullPath, fileProperties=fileProperties)

  return "not a valid file"


@app.route('/viewsources/<string:project>/<path:urlFilePath>')
@app.route('/viewsources/<string:project>', defaults={'urlFilePath': None })
@login_required
def viewsources(project, urlFilePath):
  pl = ProjectLocator( project, userName() )
  folder = pl.srcdir
  return browse( 'viewsources', project, folder, urlFilePath )

@app.route('/viewtests/<string:project>/<path:urlFilePath>')
@app.route('/viewtests/<string:project>', defaults={'urlFilePath': None })
@login_required
def viewtests(project, urlFilePath):
  pl = ProjectLocator( project, userName() )
  folder = pl.testdir
  return browse( 'viewtests', project, folder, urlFilePath )



