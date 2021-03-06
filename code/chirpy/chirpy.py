# Imports always come first
import uuid
import hashlib
import requests
from datetime import datetime
from flask import Flask, request, render_template, abort, redirect, url_for


# Our first task is to create an instance
# of the Flask class. This is the core of
# our web application.
app = Flask('chirpy')

# By convention, all config entries are uppercase
DEBUG = True
PORT = 8686
SECRET_KEY = 'suchsecretwow'

# Tell our Flask instance to use the above settings
app.config.from_object(__name__)




# Our very wonderful database
# Now, more complex!
chirpy_posts_db = {}


# We create our first 'route'
# This tells our Flask instance that anyone connecting to
# http://chirpy/ will get this reponse
@app.route('/')
def index():
    return render_template('chirpy.html', posts=chirpy_posts_db)


# A second route, this time for submitting
# new posts. Note that we only allow http
# 'POST' methods.
@app.route('/submit', methods=['POST'])
def submit_post():
    post = {'uuid': str(uuid.uuid4()), 'created': datetime.utcnow()}
    post['email'] = request.form.get('email').lower().strip()
    post['post'] = request.form.get('post')

    # Let's just move this magic into it's own line
    email_hash = hashlib.md5(post['email'].encode('utf-8')).hexdigest()

    response = requests.get('https://www.gravatar.com/{}.json'.format(email_hash))
    # Once we ask for the profile data, we have to check that we got valid info back!
    if response.status_code == 200:  # All clear!
        profile = response.json()['entry'][0]  # Now we get JSON :)
        post['username'] = profile['preferredUsername']
        post['avatar'] = profile['thumbnailUrl']
    else:
        # We should handle invalid/missing accounts
        post['username'] = 'anonymous'
        post['avatar'] = 'https://www.gravatar.com/avatar/{}?d=mm'.format(email_hash)
    chirpy_posts_db[post['uuid']] = post
    return redirect(url_for('index'))


# MORE ROUTES! This route supports passing
# a variable, giving us the ability to
# interact with individual posts!
# We will accept POST requests since HTML
# forms don't support the DELETE method
@app.route('/post/<post_id>/delete', methods=['POST', 'DELETE'])
def delete_post(post_id):
    if post_id in chirpy_posts_db:
        del chirpy_posts_db[post_id]
    return redirect(url_for('index'))
