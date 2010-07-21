from google.appengine.ext.webapp.util import run_wsgi_app
from tao.views import app
import urllib
env = app.jinja_env

def urlencode(value):
    return urllib.quote(value,'')
env.filters['urlencode'] = urlencode
def main():
    app.debug = True
    run_wsgi_app(app)

if __name__ == '__main__':
    main()
