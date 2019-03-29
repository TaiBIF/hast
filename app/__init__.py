import re
import os

from flask import Flask
#from jinja2 import evalcontextfilter, Markup, escape
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)

app.config.from_object('config')
if os.environ.get('IS_PROD', '') == 'heroku':
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL','')
else:
    # instance folder
    app.config.from_pyfile('config.py')

    
db = SQLAlchemy(app)


@app.cli.command()
def initdb():
    print ('initdb')
    #db.create_all()

#@app.template_filter()
#@evalcontextfilter
#def nl2br(eval_ctx, value):
#    _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')    
#    result = u'\n\n'.join(u'%s' % p.replace('\n', Markup('<br>\n'))
#                          for p in _paragraph_re.split(escape(value)))
#    if eval_ctx.autoescape:
#        result = Markup(result)
#    return result


from app import routes
