import os

class Config(object):
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'akeyfortheprojectbrowser'
  TEMPLATES_AUTO_RELOAD = True

