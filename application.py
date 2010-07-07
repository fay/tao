from google.appengine.ext.webapp.util import run_wsgi_app
from tao.views import app
from flask import Flask

def main():
    app.debug = True
    app.run()

if __name__ == '__main__':
    main()
