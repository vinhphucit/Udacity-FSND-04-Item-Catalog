#! /usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify
from flask import session as login_session
from flask import make_response
from database.database_manager import DatabaseManager
import random
import string
from login_required_decorator import login_required
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import json
import httplib2
import requests
import urllib.request as ur
import urllib.parse as par
from urllib.error import HTTPError
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

CLIENT_ID = json.loads(open("client_secrets.json", "r").read())["web"]["client_id"]

app = Flask(__name__)

# ===================ROUTE==================


# Get all catalogs
@app.route("/")
@app.route("/catalog/")
def show_latest_catalog():
    databaseManager = DatabaseManager()
    categories = databaseManager.get_categories()
    items = databaseManager.get_latest_items()
    return render_template("latest_item_catalog.html", categories = categories, items = items, category_id = 0)

@app.route("/catalog/<int:id>")
def show_catalog(id):
    databaseManager = DatabaseManager()
    categories = databaseManager.get_categories()
    items = databaseManager.get_items(id)
    itemcount = databaseManager.get_items_count(id)
    return render_template("catalog.html", categories = categories, items = items, category_id = id, itemcount = itemcount)

# show item
@app.route("/items/<int:item_id>?<int:category_id>", methods=["GET"])
def show_item(item_id, category_id):
    databaseManager = DatabaseManager()
    item = databaseManager.get_item(item_id)
    return render_template("show_item.html", item = item, category_id = category_id)

# Create new item
@app.route("/catalogs/<int:category_id>/items/new", methods=["GET", "POST"])
@login_required
def create_new_item(category_id):
    databaseManager = DatabaseManager()
    if request.method == "POST":
        databaseManager.create_items(request.form["category"], request.form["name"], request.form["description"], user_id=login_session['user_id'])
        if category_id == 0:
            return redirect(url_for("show_latest_catalog"))
        else:
            return redirect(url_for("show_catalog", id = category_id))
    else:
        categories = databaseManager.get_categories()
        return render_template("create_item.html", category_id = category_id, categories = categories)


# Edit item
@app.route("/items/<int:item_id>/edit?<int:category_id>", methods=["GET", "POST"])
@login_required
def edit_item(item_id, category_id):
    databaseManager = DatabaseManager()
    if request.method == "GET":
        item = databaseManager.get_item(item_id)
        categories = databaseManager.get_categories()
        return render_template("edit_item.html", item = item, categories = categories, category_id = category_id)
    else:
        item = databaseManager.update_item(item_id, request.form["name"], request.form["description"], request.form["category"])
        flash("update item successfully")
        if category_id ==0:
            return redirect(url_for("show_latest_catalog"))
        else:
            return redirect(url_for("show_catalog", id = item.category_id))

# Delete item
@app.route("/items/<int:item_id>/delete?<int:category_id>", methods=["GET", "POST"])
@login_required
def delete_item(item_id, category_id):
    if request.method == "GET":
        databaseManager = DatabaseManager()
        item = databaseManager.get_item(item_id)
        return render_template("delete_item.html", item = item, category_id = category_id)
    else:
        flash("delete item successfully")
        databaseManager = DatabaseManager()
        databaseManager.delete_item(item_id)
        if category_id ==0:
            return redirect(url_for("show_latest_catalog"))
        else:
            return redirect(url_for("show_catalog", id = category_id))

# Login
@app.route("/login")
def showLogin():
    state = "".join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session["state"] = state
    return render_template("login.html", STATE=state)

# Connect and login to google
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    
    html = ur.urlopen(url).read()
    
    result = json.loads(html.decode('utf-8'))
    
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    databaseManager = DatabaseManager()
    user_id = databaseManager.get_user_id(login_session["email"])
    if not user_id:
        databaseManager = DatabaseManager()
        user_id = databaseManager.create_user(login_session['username'], login_session['email'], login_session['picture'])
    
    login_session["user_id"] = user_id
    
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    print("done!")
    return output


# Logout google
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    print("accesstoken: " + access_token)
    url =   "https://accounts.google.com/o/oauth2/revoke?token=" + login_session['access_token']

    try:
        html = ur.urlopen(url).read()
        print(html)
        result = json.loads(html.decode('utf-8'))
    except HTTPError:
        print("error")

    # if result['status'] == '200':
    del login_session['access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    response = make_response(json.dumps('Successfully disconnected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    return redirect(url_for("show_latest_catalog"))


# JSON endpoints


# API to get all categories
@app.route("/catalog/JSON")
def get_catalog_json():
    databaseManager = DatabaseManager()
    categories = databaseManager.get_categories()
    return jsonify(categories = [i.serialize for i in categories])


# API to get list of latest items
@app.route("/items/JSON")
def get_latest_items():
    databaseManager = DatabaseManager()
    items = databaseManager.get_latest_items()
    return jsonify(items = [i.serialize for i in items])


# API to get list of items by category id
@app.route("/categories/<int:id>/items/JSON")
def get_items_by_category(id):
    databaseManager = DatabaseManager()
    items = databaseManager.get_items(id)
    return jsonify(items = [i.serialize for i in items])


# API to get specific item by id
@app.route("/items/<int:item_id>/JSON")
def get_items_by_id(item_id):
    databaseManager = DatabaseManager()
    item = databaseManager.get_item(item_id)
    return jsonify(item.serialize)
# ===================END ROUTE==================

if __name__ == '__main__':
    app.secret_key = "this_is_the_secret_key"
    app.debug = True
    app.run(host = "0.0.0.0", port = 8080)
