from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from tao.models import *

app = Flask(__name__)

@app.route('/')
def index():
    try:
        page = int(request.args.get('page'))
    except:
        page = 1
    urls = Url.all().order('-when').fetch(20, 20 * (page - 1))
    
    is_last = len(urls) < 20
    return render_template('index.html', urls=urls)
