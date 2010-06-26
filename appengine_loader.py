import logging
import os
import re
import sys
import zipfile


DIR_PATH = os.path.abspath(os.path.dirname(__file__))
#PARENT_DIR = os.path.dirname(DIR_PATH)
sys.path = [DIR_PATH,] + sys.path

def LoadSdk():
  # Try to import the appengine code from the system path.
  try:
    from google.appengine.api import apiproxy_stub_map
  except ImportError, e:
    # Hack to fix reports of import errors on Ubuntu 9.10.
    if 'google' in sys.modules:
      del sys.modules['google']
    # Not on the system path. Build a list of alternative paths where it may be.
    # First look within the project for a local copy, then look for where the Mac
    # OS SDK installs it.
    paths = [os.path.join(DIR_PATH, '.google_appengine'),
             os.path.join(DIR_PATH, 'google_appengine'),
             '/usr/local/google_appengine']
    print paths
    # Then if on windows, look for where the Windows SDK installed it.
    for path in os.environ.get('PATH', '').split(';'):
      path = path.rstrip('\\')
      if path.endswith('google_appengine'):
        paths.append(path)
    try:
      from win32com.shell import shell
      from win32com.shell import shellcon
      id_list = shell.SHGetSpecialFolderLocation(
          0, shellcon.CSIDL_PROGRAM_FILES)
      program_files = shell.SHGetPathFromIDList(id_list)
      paths.append(os.path.join(program_files, 'Google',
                                'google_appengine'))
    except ImportError, e:
      # Not windows.
      pass
    # Loop through all possible paths and look for the SDK dir.
    SDK_PATH = None
    for sdk_path in paths:
      if os.path.exists(sdk_path):
        SDK_PATH = os.path.realpath(sdk_path)
        break
    if SDK_PATH is None:
      # The SDK could not be found in any known location.
      sys.stderr.write("The Google App Engine SDK could not be found!\n")
      sys.stderr.write("See README for installation instructions.\n")
      sys.exit(1)
    if SDK_PATH == os.path.join(DIR_PATH, 'google_appengine'):
      logging.warn('Loading the SDK from the \'google_appengine\' subdirectory '
                   'is now deprecated!')
      logging.warn('Please move the SDK to a subdirectory named '
                   '\'.google_appengine\' instead.')
      logging.warn('See README for further details.')
    # Add the SDK and the libraries within it to the system path.
    EXTRA_PATHS = [
        SDK_PATH,
        os.path.join(SDK_PATH, 'lib', 'antlr3'),
        os.path.join(SDK_PATH, 'lib', 'django'),
        os.path.join(SDK_PATH, 'lib', 'ipaddr'),
        os.path.join(SDK_PATH, 'lib', 'webob'),
        os.path.join(SDK_PATH, 'lib', 'yaml', 'lib'),
    ]
    # Add SDK paths at the start of sys.path, but after the local directory which
    # was added to the start of sys.path on line 50 above. The local directory
    # must come first to allow the local imports to override the SDK and
    # site-packages directories.
    sys.path = sys.path[0:1] + EXTRA_PATHS + sys.path[1:]
