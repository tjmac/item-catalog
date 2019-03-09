#!/usr/bin/python2.7
from models import User, Category, CategoryItem, engine
from flask import Flask, jsonify, request, url_for, \
    render_template, redirect, flash
from sqlalchemy.orm import sessionmaker

import google_auth_oauthlib.flow
import flask


import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

import requests


app = Flask(__name__)
app.secret_key = 'super_secret_key'

# for Google auth flow
CLIENT_SECRETS_FILE = '/var/www/catalog/client_secrets_2.json'
SCOPES = ['https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/userinfo.email',
          'openid' ]


# create session
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    
    # Store the access token in the session for later use.
    flask.session['access_token'] = credentials.token

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()


    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(data['name'], data['email'], data['picture'])

    flask.session['user_id'] = user_id
    flask.session['username'] = data['name']
    flask.session['picture'] = data['picture']
    flask.session['email'] = data['email']
    flask.session['provider'] = 'google'

    flask.flash("You are now logged in as %s" % flask.session['username'])
    return flask.redirect('/')


@app.route('/logout')
def logout():
    flask.session.clear()
    return flask.redirect('/')


# non-auth related routes
# User Helper Functions
def createUser(username, email, picture):
    newUser = User(name=username, email=email, picture=picture)
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=email).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


def getCategoryId(category_name):
    # TODO change Category to Category
    category = session.query(Category).filter_by(name=category_name).one()
    return category.id


# Show catalog
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    # categories = session.query(Category).order_by(asc(Category.name))
    categories = session.query(Category)
    if 'username' not in flask.session:
        return render_template('publiccatalog.html', categories=categories)
    else:
        return render_template('catalog.html', categories=categories)


# Show a categories items
# include string in route http://flask.pocoo.org/docs/0.12/quickstart/ >>
# Variable Rules
@app.route('/catalog/<string:category>/')
@app.route('/catalog/<string:category>/Items/')
def showCategoryItems(category):
    category = session.query(Category).filter_by(name=category).one()
    items = session.query(CategoryItem).filter_by(category=category).all()
    if 'username' not in flask.session:
        return render_template(
            'publiccategoryitems.html',
            category=category,
            items=items)
    else:
        return render_template(
            'categoryitems.html',
            category=category,
            items=items)


# show individual items name, description...
@app.route('/catalog/<string:category>/<string:item_name>/')
def showCategoryItem(category, item_name):
    category = session.query(Category).filter_by(name=category).one()
    item_name = session.query(CategoryItem).filter_by(
        category=category, item_name=item_name).one()
    if 'username' not in flask.session:
        return render_template(
            'publicitem.html',
            item_name=item_name,
            category=category)
    else:
        return render_template(
            'item.html',
            item_name=item_name,
            category=category)


@app.route('/catalog/<string:category>/<string:item_name>/JSON')
def itemJSON(category, item_name):
    category = session.query(Category).filter_by(name=category).one()
    item = session.query(CategoryItem).filter_by(
        category=category, item_name=item_name).one()
    return jsonify(item=item.serialize)


# Create a new category
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in flask.session:
        return redirect('/login')
    if request.method == 'POST':
        # check for duplicates
        newCategory = Category(
            name=request.form['name'], user_id=flask.session['user_id'])
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newcategory.html')


# Create a new category item
@app.route('/catalog/<string:category>/Items/new/', methods=['GET', 'POST'])
def newItem(category):
    if 'username' not in flask.session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category).one()
    if request.method == 'POST':
        newItem = CategoryItem(
            item_name=request.form['name'],
            item_description=request.form['description'],
            user_id=flask.session['user_id'],
            category_id=category.id)
        session.add(newItem)
        flash('New Item %s Item Successfully Created' % (newItem.item_name))
        session.commit()
        return redirect(url_for('showCategoryItems', category=category.name))
    else:
        return render_template('newitem.html', category=category)


# Edit an item
@app.route(
    '/catalog/<string:category>/<string:item_name>/edit/',
    methods=[
        'GET',
        'POST'])
def editItem(category, item_name):
    # need to use category in query in the case the item is in multiple
    # categories
    category_id = getCategoryId(category)
    editedItem = session.query(CategoryItem).filter_by(
        category_id=category_id, item_name=item_name).one()
    if 'username' not in flask.session:
        return redirect('/login')
    if editedItem.user_id != flask.session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized\
            to edit this item. Please create your own item in order\
            to edit.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.item_name = request.form['name']
        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited, changed to %s' % editedItem.item_name)
        return redirect(url_for('showCatalog'))
    else:
        return render_template(
            'edititem.html',
            item_name=item_name,
            category=category)


# Delete an item
@app.route(
    '/catalog/<string:category>/<string:item_name>/delete/',
    methods=[
        'GET',
        'POST'])
def deleteItem(category, item_name):
    # TODO if item_name is in more than one category this would be incorrect...
    # need to use category in query in the case the item is in multiple
    # categories
    category_id = getCategoryId(category)
    itemToDelete = session.query(CategoryItem).filter_by(
        category_id=category_id, item_name=item_name).one()
    if 'username' not in flask.session:
        return redirect('/login')
    if itemToDelete.user_id != flask.session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized \
            to delete this item. Please create your own item in order \
            to delete.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        flash('%s Successfully Deleted' % itemToDelete.item_name)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template(
            'deleteitem.html',
            category=category,
            item_name=itemToDelete)


@app.route('/catalog.json')
def catalogJSON():
    # not the best that it returns all, query parameters could help make this
    # more flexible and usable.
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


if __name__ == '__main__':

    app.debug = True
    app.run(host='0.0.0.0', port=80)
