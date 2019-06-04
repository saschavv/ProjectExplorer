import shutil

from app.models import *

def copyTestOutput( locator, test ):
  srcDir = locator.srcdir
  tstDir = locator.testdir

  baseTest = test.split('/')[-1]
  
  srcFile = os.path.join( tstDir, test + ".dir/" + baseTest + ".new" )
  destFile = os.path.join( srcDir, test + ".res" )
  copyTxt = 'cp ' + srcFile + ' ' + destFile
  try:
    shutil.copy( srcFile, destFile )
    status = True
  except IOError as e:
    status = False
    print( "Unable to copy file. %s" % e )

  return { 'status' : status, 'message' : copyTxt }

def copyTestFile( locator, srcFile, destFile ):

  copyTxt = 'cp ' + srcFile + ' ' + destFile
  try:
    shutil.copy( srcFile, destFile )
    status = True
  except IOError as e:
    status = False
    print( "Unable to copy file. %s" % e )

  return { 'status' : status, 'message' : copyTxt }



