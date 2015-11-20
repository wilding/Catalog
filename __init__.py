# Flask setup
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
app = Flask(__name__)

#import CRUD operations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Article

#create session and connect to database
engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

# OAuth setup
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
CLIENT_ID = json.loads(open('/var/www/Catalog/Catalog/client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Newspaper"

# LOGIN
@app.route('/login/')
def showLogin():
  state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
  login_session['state'] = state
  return render_template('login.html', STATE = state)

# CONNECT
@app.route('/gconnect/', methods = ['POST'])
def gconnect():
  # Validate state token
  if request.args.get('state') != login_session['state']:
    response = make_response(json.dumps('Invalid state parameter'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  # Obtain authorization code
  code = request.data

  try:
    # Upgrade the authorization code into a credentials object
    oauth_flow = flow_from_clientsecrets('/var/www/Catalog/Catalog/client_secrets.json', scope='')
    oauth_flow.redirect_uri = 'postmessage'
    credentials = oauth_flow.step2_exchange(code)
  except FlowExchangeError:
    response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response

  # Check that the access token is valid
  access_token = credentials.access_token
  url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
  h = httplib2.Http()
  result = json.loads(h.request(url, 'GET')[1])
  # If there was an error in the access token info, abort
  if result.get('error') is not None:
    response = make_response(json.dumps(result.get('error')), 500)
    response.headers['Content-Type'] = 'application/json'

  # Verify that the access token is used for the intended user
  gplus_id = credentials.id_token['sub']
  if result['user_id'] != gplus_id:
    response = make_response(json.dumps("Token's user ID doesn't match given user ID"), 401)
    response.headers['Content-Type'] = 'application/json'
    return response

  # Verifiy that the access token is valid for this app
  if result['issued_to'] != CLIENT_ID:
    response = make_response(json.dumps("Token's client ID does not match app's."), 401)
    print "Token's client ID does not match app's."
    response.headers['Content-Type'] = 'application/json'
    return response

  # Check to see if the user is already logged in
  stored_credentials = login_session.get('credentials')
  stored_gplus_id = login_session.get('gplus_id')
  if stored_credentials is not None and gplus_id == stored_gplus_id:
    response = make_response(json.dumps('Current user is already connected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response

  # Store the access token in the session for later use
  login_session['access_token'] = credentials.access_token
  login_session['gplus_id'] = gplus_id

  # Get user info
  userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
  params = {'access_token': credentials.access_token, 'alt':'json'}
  answer = requests.get(userinfo_url, params=params)
  data = answer.json()
  login_session['username'] = data['name']
  login_session['picture'] = data['picture']
  login_session['email'] = data['email']

  output = ''
  output += '<h1>Welcome, '
  output += login_session['username']
  output += '!</h1>'
  output += '<img src="'
  output += login_session['picture']
  output += ' " style="width: 300px; height: 300px; border-radius: 150px; -webkit-border-radius: 150px; -moz-border-radius: 150px;">'
  flash("you are now logged in as %s" % login_session['username'])
  print "done!"
  return output

# DISCONNECT - revoke current user's token and reset their login_session
@app.route('/gdisconnect/')
def gdisconnect():
  # only disconnect a connected user
  credentials = login_session.get('credentials')
  if credentials is None:
    response = make_response(json.dumps('Current user not connected.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  # execute HTTP GET request to revoke current token
  access_token = credentials.access_token
  url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
  h = httplib2.Http()
  result = h.request(url, 'GET')[0]

  if result['status'] == '200':
    # Reset the user's session
    del login_session['credentials']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']

    response = make_response(json.dumps('Successfully disconnected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response
  else:
    # for whatever reason, the given token was invalid
    response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
    response.headers['Content-Type'] = 'application/json'
    return response


# CATEGORIES JSON
@app.route('/category/JSON/')
@app.route('/categories/JSON/')
def categoriesJSON():
	categories = session.query(Category).all()
	return jsonify(Categories=[category.serialize for category in categories])

# ARTICLES JSON
@app.route('/category/<int:category_id>/JSON/')
@app.route('/category/<int:category_id>/catalog/JSON/')
def catalogJSON(category_id):
	category = session.query(Category).filter_by(id = category_id).one()
	articles = session.query(Article).filter_by(category_id = category_id).all()
	return jsonify(Articles=[article.serialize for article in articles])

# SINGLE ARTICLE JSON
@app.route('/category/<int:category_id>/catalog/<int:article_id>/JSON/')
def articleJSON(category_id, article_id):
	article = session.query(Article).filter_by(id = article_id).one()
	return jsonify(Article=[article.serialize])

# HOMEPAGE
@app.route('/')
@app.route('/categories/')
@app.route('/category/')
def showCategories():
	categories = session.query(Category).all()
	return render_template('mainmenu.html', categories = categories)

# CATEGORY MENU
@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/catalog/')
def showCatalog(category_id):
	categories = session.query(Category).all()
	category = session.query(Category).filter_by(id = category_id).one()
	articles = session.query(Article).filter_by(category_id = category_id).all()
	return render_template('categorymenu.html', categories = categories, category = category, articles = articles)

# ARTICLE
@app.route('/category/<int:category_id>/catalog/<int:article_id>/')
def showArticle(category_id, article_id):
	categories = session.query(Category).all()
	category = session.query(Category).filter_by(id = category_id).one()
	article = session.query(Article).filter_by(id = article_id).one()
	return render_template('article.html', categories = categories, category = category, article = article)

# NEW CATEGORY
@app.route('/category/new/', methods = ['GET', 'POST'])
def newCategory():
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	if request.method == 'POST':
		newcategory = Category(name = request.form['name'])
		session.add(newcategory)
		session.commit()
		flash('New category created!')
		return redirect(url_for('showCategories'))
	else:
		return render_template('newcategory.html')

# EDIT CATEGORY
@app.route('/category/<int:category_id>/catalog/edit/', methods = ['GET', 'POST'])
def editCategory(category_id):
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	category = session.query(Category).filter_by(id = category_id).one()
	if request.method == 'POST':
		if request.form['name']:
			category.name = request.form['name']
		session.add(category)
		session.commit()
		flash('Category edited!')
		return redirect(url_for('showCatalog', category_id = category_id))
	else:
		return render_template('editcategory.html', category = category)

# DELETE CATEGORY
@app.route('/category/<int:category_id>/catalog/delete/', methods = ['GET', 'POST'])
def deleteCategory(category_id):
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	category = session.query(Category).filter_by(id = category_id).one()
	if request.method == 'POST':
		session.delete(category)
		session.commit()
		flash("Category deleted!")
		return redirect(url_for('showCategories'))
	else:
		return render_template('deletecategory.html', category = category)

# NEW ARTICLE
@app.route('/category/<int:category_id>/catalog/new/', methods = ['GET', 'POST'])
def newArticle(category_id):
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	if request.method == 'POST':
		newarticle = Article(title = request.form['title'], tagline = request.form['tagline'], text = request.form['text'], author = request.form['author'], date = request.form['date'], category_id = category_id)
		session.add(newarticle)
		session.commit()
		flash('New article created!')
		return redirect(url_for('showCatalog', category_id = category_id))
	else:
		return render_template('newarticle.html', category_id = category_id)

# EDIT ARTICLE
@app.route('/category/<int:category_id>/catalog/<int:article_id>/edit/', methods = ['GET', 'POST'])
def editArticle(category_id, article_id):
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	article = session.query(Article).filter_by(id = article_id).one()
	if request.method == 'POST':
		if request.form['title']:
			article.title = request.form['title']
		if request.form['tagline']:
			article.tagline = request.form['tagline']
		if request.form['text']:
			article.text = request.form['text']
		if request.form['author']:
			article.author = request.form['author']
		if request.form['date']:
			article.date = request.form['date']
		session.add(article)
		session.commit()
		flash("Article edited!")
		return redirect(url_for('showArticle', category_id = category_id, article_id = article_id))
	else:
		return render_template('editarticle.html', article = article)

# DELETE ARTICLE
@app.route('/category/<int:category_id>/catalog/<int:article_id>/delete/', methods = ['GET', 'POST'])
def deleteArticle(category_id, article_id):
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	article = session.query(Article).filter_by(id = article_id).one()
	if request.method == 'POST':
		session.delete(article)
		session.commit()
		flash("Article deleted!")
		return redirect(url_for('showCatalog', category_id = category_id))
	else:
		return render_template('deletearticle.html', article = article)

# Flask setup
if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 8080)
