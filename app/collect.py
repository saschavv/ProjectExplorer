
from glob import glob

import os
import os.path, time
import stat
import pprint
import svn.local
import svn.exception
import difflib
import psutil
import markdown

from app.models import *

def getProjectNames( user ):
  """ 
      Get all the projects for the current user. 
  """
  projectRoot='/uhome/' + user + '/projects/'
  projectsPath= projectRoot + os.sep + "*" + os.sep + ".svn"
  files = glob(projectsPath)
  # The 'special' global diana project.
  projects = [ 'diana' ]
  for listFile in files :
    projects.append( listFile.split('/')[-2] )
  return sorted(projects)

def getProjectFolder( user):
  return '/uhome/' + user + '/projects/'

def getDoc( folder ):
  mdFile = os.path.join( folder, 'README.md' )
  if os.path.exists( mdFile ):
    with open ( mdFile, "r") as myfile:
      return markdown.markdown( myfile.read() )
  rstFile =  os.path.join(folder, 'README.rst' ) 
  if os.path.exists( rstFile ):
    with open ( rstFile, "r") as myfile:
      return myfile.read()
  return None

def getProjectDoc( user ):
  folder = getProjectFolder( user )
  return getDoc( folder )

def getProjectModelsByName( names, user ):
  models = []
  for name in names:
    projectModel = ProjectModel( name, user )
    projectModel.buildInfo = getBuildModel( projectModel.locator )
    if name != 'diana':
      projectModel.versionInfo = getVersionModel( projectModel.locator )
      projectModel.testInfo = TestOverviewModel( 
          getRunnedTests( projectModel.locator ),
          getFailedTests( projectModel.locator ) )
      projectModel.doc = getDoc( projectModel.locator.srcdir )
        
      # projectModel.processInfo = getProcessModel( projectModel.locator )
    else:
      projectModel.testInfo = TestOverviewModel( [], [] )
      projectModel.doc = None 

    models.append( projectModel )
  return models 
     
def getVersionModel( locator ):
  try:
      if os.path.exists( locator.srcdir ):
        r = svn.local.LocalClient( locator.srcdir )
        info = r.info()
        return VersionModel( info['url'], info['commit_revision' ] )
  except svn.exception.SvnException:
    return None
  except AttributeError:
    return None

  return None

def getBuildModel( locator ):
  fileToCheck = os.path.join( locator.builddir, '.ninja_log' ) 
  if os.path.exists( fileToCheck ):
    modified = time.ctime(os.path.getmtime(fileToCheck))
    return BuildModel( modified )
  fileToCheck = os.path.join( locator.builddir, 'modules/diana/__init__.py' )
  if os.path.exists( fileToCheck ):
    modified = time.ctime(os.path.getmtime(fileToCheck))
    return BuildModel( modified )
  return BuildModel( 0 )

def getProcessModel( locator ):
  model = ProcessModel()
  for proc in psutil.process_iter():
    try:
      pinfo = proc.as_dict(attrs=['username','pid', 'name', 'cwd', 'cmdline'])
      # {'name': 'ninja', 'username': 'vts', 'pid': 21840, 
      # 'cmdline': ['/opt/cmake-3.10.2/bin/ninja', 'all'], 'cwd': '/usr1/user/vts/projects/bravo/debug'}
      if pinfo['username'] == locator.user and pinfo['name'] == 'ninja':
          project = pinfo['cwd'].split('/')[-2]
          if project == locator.project:
            model.building( True )
            return model
    except psutil.NoSuchProcess:
      pass
  return model

def getTestModels( locator ):
  testNames = getFailedTests( locator )
  failedTests = []
  for test in testNames:
    testModel = TestModel( locator, test )
    failedTests.append( testModel )
  return failedTests

def getFailedTests( locator ):
  tests = []
  fileName = os.path.join( locator.testdir, 'Tests.failed' )
  if os.path.isfile( fileName ):
    with open( fileName, "r" ) as f:
      for i, l in enumerate(f):
        tests.append( l.rstrip() )
  return tests   

def getRunnedTests( locator ):
  tests = []
  fileName = os.path.join( locator.testdir, 'Tests.done' )
  if os.path.isfile( fileName ):
    with open( fileName, "r" ) as f:
      for i, l in enumerate(f):
        tests.append( l.rstrip() )
  return tests   

def makeDiff( left, right ):
  unifiedDiff = os.popen('diff -u "' + left + '" "' + right + '"')
  return unifiedDiff.read()

def makeLogFromXml( xmlFile ):
  return ''

def makeSquishOutput( pl, test ):
  srcDir = pl.srcdir
  testDir = pl.testdir
  fullTestDir = os.path.join( testDir, test + ".dir" )

  result = os.path.join( fullTestDir, 'results.xml' )

  cmdTxt = 'python2 /opt/squish-6.3.2/examples/regressiontesting/squishxml2html.py'
  cmdTxt += ' -d ' + fullTestDir
  cmdTxt += ' ' + result

  os.system( cmdTxt )

def getTestOutput( pl, test ):
  srcDir = pl.srcdir
  testDir = pl.testdir
  fullTestDir = os.path.join( testDir, test + ".dir" )

  testListing = []
  if os.path.isdir(fullTestDir):
    # Diff all *res and *new files.
    names = os.listdir( fullTestDir )
    newFiles = [ f for f in names if f.endswith('.new') ]
    for newFile in newFiles:
       newFile = os.path.join( fullTestDir, newFile ) 
       resFile = os.path.join( srcDir, test + ".res" )
       if os.path.exists( resFile ):
          testDiff = {}
          testDiff['type' ] = 'diff'
          testDiff['name' ] = os.path.basename( resFile )
          testDiff['diff' ] = makeDiff( resFile, newFile )
          testListing.append( testDiff ) 
    # Collect all png diffs.
    newFiles = [ f for f in names if f.endswith('_new.png') ]
    for newFile in newFiles:
       newFile = newFile
       diffFile = newFile.replace( "_new", "_diff" )
       orgFile = newFile.replace( "_new", "_ref" )
       orgPlatormFile = newFile.replace( "_new", "___Linux_ref" )

       items = test.split('/')
        
       testDiff = {}
       testDiff['type' ] = 'image'
       testDiff['test' ] = items[-1]
       testDiff['testpath' ] = '/'.join(items[:-1])
       testDiff['new' ] = newFile
       testDiff['diff' ] = diffFile
       path = os.path.join( srcDir, testDiff['testpath'] )

       fileLoc = os.path.join( fullTestDir, diffFile )
       print('File: ' + fileLoc)
       if os.path.exists( fileLoc ):
         sbuf = os.fstat(os.open(fileLoc, os.O_RDONLY))
         testDiff['diff_mtime'] =sbuf.st_mtime

       fileLoc = os.path.join( fullTestDir, newFile )
       if os.path.exists( fileLoc ):
         sbuf = os.fstat(os.open(fileLoc, os.O_RDONLY))
         testDiff['new_mtime'] =sbuf.st_mtime

       fileLoc = os.path.join( path, orgFile )
       if os.path.exists( fileLoc ):
         sbuf = os.fstat(os.open(fileLoc, os.O_RDONLY))
         testDiff['orginal_mtime'] = sbuf.st_mtime 
         testDiff['original'] = orgFile

       fileLoc = os.path.join( path, orgPlatormFile )
       if os.path.exists( fileLoc ):
         sbuf = os.fstat(os.open(fileLoc, os.O_RDONLY))
         testDiff['orginal_mtime'] = sbuf.st_mtime 
         testDiff['original'] = orgPlatormFile
       testListing.append( testDiff ) 
  return testListing

