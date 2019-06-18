import os
import os.path
import pprint
import datetime
from flask import Flask, url_for, render_template, send_file, send_from_directory

def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)

class Entry():
  def __init__( self, root, relpath ):
    self._root = root
    self._relpath = relpath

  def name(self):
    return None

  def rootDir(self):
    return self._root

  def is_root(self):
    return self._relpath == "." or self._relpath == ""

  def relativePath(self):
    return self._relpath

  def icon(self):
    return None

  def lastModified(self):
    return ""

  def size(self):
    return ""

  def absolutePath(self):  
    return self._root.absolutePath(self._relpath)   


  def __str__(self): 
    return "entry: " + self._root + " " + self._relpath

class File(Entry):

  default_icon = "page_white.png"
  icon_map = []

  def __init__(self, root, relpath):
    Entry.__init__(self, root, relpath)
    abs_path = self.absolutePath()
    self._extension = os.path.splitext(abs_path)[1][1:]
    stat = os.stat(abs_path)
    self._last_modified = stat.st_mtime
    self._size = stat.st_size
    self._name = os.path.basename(relpath)

  def name(self):
    return self._name
    
  def isCode(self):
    codeExt = [ 'h', 'cpp', 'xml', 'py', ]
    if self._extension in codeExt:
      return True

  def isText(self):
    textExt = [ 'h', 'cpp', 'run', 'xml', 'py', 'res', 'log' ]
    if self._extension in textExt:
      return True

  def canDownload(self):
    abs_path = self.absolutePath()
    if os.path.isfile( abs_path ):
      return True

  def data(self):
    abs_path = self.absolutePath()
    with open(abs_path, 'r') as file:
      content = file.read()
    return content  

  def guess_icon(self):
    for icon, rule in self.icon_map:
      match = rule(self)
      if match:
        return icon
    return self.default_icon

  def icon(self):
    return self.guess_icon()

  @classmethod
  def add_icon_rule(cls, icon, rule=None):
    """Adds a new icon rule globally."""
    cls.icon_map.append((icon, rule))

  def lastModified(self):
    return datetime.datetime.fromtimestamp(self._last_modified).strftime("%m/%d/%Y, %H:%M:%S")

  def size(self):
    return sizeof_fmt( self._size )

  @classmethod
  def add_icon_rule_by_ext(cls, icon, ext):
    """Adds a new icon rule by the file extension globally."""
    cls.add_icon_rule(icon, lambda f: f._extension == ext)

  def __str__(self):        
    return "file: " + self._name 

class Directory(Entry):

  def __init__(self, root, dir, name = None, icon = 'folder.png'):
    Entry.__init__(self, root, dir)
    abs_path = self.absolutePath()
    stat = os.stat( abs_path )
    self._last_modified = stat.st_mtime
    self._entries = []
    if name == None:
      self._name = os.path.basename( dir )
    else:
      self._name = name
    self._icon = icon  

  def parent(self):
    if self.is_root():
      return None
    return Directory( self.rootDir(), os.path.dirname( self.relativePath() ) )

  def name(self):
    return self._name

  def icon(self):
    return self._icon 

  def lastModified(self):
    return datetime.datetime.fromtimestamp(self._last_modified).strftime("%m/%d/%Y, %H:%M:%S")

  def load(self):
    self._entries = []

    parent, dir = os.path.split(self.relativePath())

    if not self.parent().is_root():
      back_dir = Directory( self.rootDir(), parent,  "Parent directory", "arrow_turn_up.png" )
      self._entries.append( back_dir )

    absPath = self.absolutePath()
    dirlist = [x for x in os.listdir(absPath) if os.path.isdir(os.path.join(absPath, x))]
    filelist = [x for x in os.listdir(absPath) if not os.path.isdir(os.path.join(absPath, x))]
    itemList = sorted(dirlist) + sorted(filelist)

    for item in itemList:
      abspath = os.path.join( absPath, item )
      if os.path.isfile( abspath ):
        self._entries.append( File( self.rootDir(), os.path.join( self.relativePath(), item ) ) )
      if os.path.isdir( abspath ):
        self._entries.append( Directory( self.rootDir(), os.path.join( self.relativePath(), item ) ) )

  def list(self):
    return self._entries;

  def __str__(self):        
    return "folder: " + self._name

class RootDirectory:
  def __init__(self, root):
    self.root = root

  def root(self):
    return self.root

  def absolutePath(self, relpath):  
    return os.path.join( self.root, relpath)   

  def __str__(self):
    return "root: " + self.root 

class Explorer:
  def __init__(self, ref, root, relpath):
    self.root = RootDirectory( root )
    self.relpath = relpath
    self.ref = ref

  def render(self):
    abspath = self.root.absolutePath( self.relpath )   
    if os.path.isfile( abspath ):
      f = File( self.root, self.relpath )
      if f.isCode():
        data = f.data()
        return render_template('code.html', title='browser', currentFile=self.relpath, code=data)
      if f.isText():
        data = f.data()
        return render_template('text.html', title='browser', currentFile=self.relpath, data=data)
      return send_file(abspath)

    if os.path.isdir(abspath):
      directory = Directory(self.root, self.relpath)
      directory.load()
      return render_template('browse.html', title='browser', directory=directory, folder=self.relpath, ref=self.ref)

def main():
  e = Explorer( '/home/saschavv/development/', 'DianaProject' )
  e.render()

if __name__ == "__main__":
    # execute only if run as a script
    main()
