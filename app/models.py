# Collection of models
import os

#------------------------------------------------------------------------------
class ProjectLocator(object):

  def __init__( self, project, user ):
    self.__project = project
    self.__user = user

    self.__prjDir = '/uhome/{user}/projects'
    self.__srcDir = '/uhome/{user}/projects/{project}'
    self.__buildDir =  '/usr1/user/{user}/projects/{project}/debug'
    self.__testDir = '/usr1/user/{user}/projects/{project}/tmp'
    self.__tstDir = '/usr1/user/{user}/projects'
    self.__dianaRoot = '/usr1/diana/release'

  @property
  def project(self):
    return self.__project


  @property
  def user(self):
    return self.__user

  @property
  def testdir( self ):
    """ The full test path of a project """
    if self.project == 'diana':
      return self.__dianaRoot
    return self.__testDir.format( project=self.project, user=self.user )

  @property
  def srcdir( self ):
    """ The full (src) project dir for a project """
    if self.project == 'diana':
      return self.__dianaRoot
    return self.__srcDir.format( project=self.project, user=self.user )

  @property
  def projects( self ):
    """ The projects dir """
    return self.__prjDir.format( user=self.user )

  @property
  def tests(self):
    return self.__tstDir.format( user=self.user )

  @property
  def builddir( self ):
    """ The full build path of a project """
    if self.project == 'diana':
      return self.__dianaRoot
    return self.__buildDir.format( project=self.project, user=self.user )

#------------------------------------------------------------------------------
class TestOverviewModel(object):
  def __init__( self, tests = [], failed = [] ):
    self.__tests = tests
    self.__failed = failed

  @property
  def numberOfTests( self ):
    return len(self.__tests)

  @property
  def numberOfFailedTests( self ):
    return len(self.__failed)

  @property
  def hasErrors( self ):
    return self.numberOfFailedTests != 0

#------------------------------------------------------------------------------
class ProcessModel(object):
  def __init__( self ):
    self.active = False

  def building( self, active ):
    self.active = active
#------------------------------------------------------------------------------
class VersionModel(object):
  def __init__( self, url = '', revision  = ''):
    self.__url = url
    self.__revision = revision

  @property
  def url( self ):
    return self.__url

  @property
  def revision( self ):
    return self.__revision

#------------------------------------------------------------------------------
class ProjectModel(object):
  def __init__( self, project, user ):
    self.locator = ProjectLocator( project, user )
    self.__versionInfo = None
    self.__buildInfo = None
    self.__testInfo = None
    self.__runInfo = None
    self.__docInfo = None

  @property
  def name(self):
    return self.locator.project

  @property
  def docInfo(self):
    return self.__docInfo

  @docInfo.setter
  def docInfo(self, value):
    self.__docInfo = value

  @property
  def versionInfo(self):
    return self.__versionInfo

  @versionInfo.setter
  def versionInfo(self, value):
    self.__versionInfo = value

  @property
  def buildInfo(self):
    return self.__buildInfo

  @buildInfo.setter
  def buildInfo(self, value):
    self.__buildInfo = value

  @property
  def testInfo(self):
    return self.__testInfo

  @testInfo.setter
  def testInfo(self, value):
    self.__testInfo = value

  @property
  def runInfo(self):
    return self.__runInfo

  @runInfo.setter
  def runInfo(self, value):
    self.__runInfo = value

#------------------------------------------------------------------------------
class BuildModel(object):
  def __init__( self, lastModified ):
    self.__lastModified = lastModified

  @property
  def lastModified( self ):
    return self.__lastModified;

#------------------------------------------------------------------------------
class TestModel(object):
  def __init__( self,  locator, test ):
    self.__locator = locator 
    self.__test = test

  @property
  def test( self ):
    return self.__test

  @property
  def path( self ):
    return self.test[:self.test.rindex('/')]

  @property
  def name( self ):
    return  self.test[self.test.rindex('/') + 1:]

  @property
  def log( self ):
    fileName = self.logFile()
    if os.path.isfile( fileName ):
      f = open(fileName, "r")
      lines = f.readlines()
      return lines
    return ''

  def logFile( self ):
    fileName = os.path.join( self.__locator.testdir, self.test )
    fileName += ".log"
    return fileName

#------------------------------------------------------------------------------




