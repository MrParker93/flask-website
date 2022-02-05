import urllib
import functools
from app import app
from flask import Response, redirect, url_for, request, session

# Decorator 
def login_required(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        if session.get('logged_in'):
            return func(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return inner
            
# Helper functions

@app.template_filter('clean_querystring')
def clean_querystring(request_args, *keys_to_remove, **new_values):
    querystring = dict((key, value) for key, value in request_args.items())
    for key in keys_to_remove:
        querystring.pop(key, None)
    querystring.update(new_values)
    return urllib.urlencode(querystring)

@app.errorhandler(404)
def not_found(exc):
    return Response('<h3>Not found</h3>'), 404