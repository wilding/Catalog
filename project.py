###############################    SETUP    ######################################################################


# Flask setup
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
app = Flask(__name__)

# import CRUD operations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload_all
from database_setup import Base, Category, Article, User, Comment

# create session and connect to database
engine = create_engine('sqlite:///newspaper.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
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
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Newspaper"

from datetime import datetime

# Atom setup
from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed


###############################    G-SIGNIN    ######################################################################


# CONNECT
@app.route('/gconnect/', methods=['POST'])
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
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
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
    stored_credentials = login_session.get('access_token')
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
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if user exists; if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = '<i class="fa fa-spinner fa-spin"></i><strong> Logging in as ' + login_session['username'] + '</strong>'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# DISCONNECT - revoke current user's token and reset their login_session
@app.route('/<path:redirect_url>/gdisconnect/')
def gdisconnect(redirect_url):
    # only disconnect a connected user
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # execute HTTP GET request to revoke current token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's session
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successfully logged out")
        return redirect(redirect_url)
    else:
        # for whatever reason, the given token was invalid
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


###############################    MENU PAGES    ######################################################################


# MAIN MENU
@app.route('/categories/')
@app.route('/category/')
@app.route('/')
def showCategories():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    categories = session.query(Category).all()
    articles = session.query(Article).order_by(Article.date.desc()).all()
    if 'username' not in login_session:
        return render_template('publicmainmenu.html', categories=categories, articles=articles, STATE=state)
    else:
        return render_template('mainmenu.html', categories=categories, articles=articles, profile_pic=login_session['picture'], profile_id=getUserID(login_session['email']))


# CATEGORY MENU
@app.route('/category/<int:category_id>/article/')
@app.route('/category/<int:category_id>/')
def showCatalog(category_id):
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()
    articles = session.query(Article).filter_by(category_id=category_id).order_by(Article.date.desc()).all()
    if 'username' not in login_session:
        return render_template('publiccategorymenu.html', categories=categories, category=category, articles=articles, STATE=state)
    else:
        return render_template('categorymenu.html', categories=categories, category=category, articles=articles, profile_pic=login_session['picture'], profile_id=getUserID(login_session['email']))


# AUTHOR MENU
@app.route('/author/<int:author_id>/')
def showAuthor(author_id):
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    categories = session.query(Category).all()
    author = session.query(User).filter_by(id=author_id).one()
    articles = session.query(Article).filter_by(user_id=author_id).order_by(Article.date.desc()).all()
    if 'username' not in login_session:
        return render_template('publicauthormenu.html', categories=categories, author=author, articles=articles, STATE=state)
    else:
        return render_template('authormenu.html', categories=categories, author=author, articles=articles, profile_pic=login_session['picture'], profile_id=getUserID(login_session['email']))


# FULL ARTICLE
@app.route('/category/<int:category_id>/article/<int:article_id>/', methods=['GET', 'POST'])
def showArticle(category_id, article_id):
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()
    article = session.query(Article).filter_by(id=article_id).one()
    comments = session.query(Comment).filter_by(article_id=article_id).order_by(Comment.date.desc()).all()
    if request.method == 'POST':
        current_time = str(datetime.now())
        newcomment = Comment(text=request.form['text'], date=current_time, last_edited=current_time, article_id=article_id, user_id=login_session['user_id'])
        session.add(newcomment)
        session.commit()
        flash('New comment created!')
        return redirect(url_for('showArticle', category_id=category_id, article_id=article_id))
    if 'username' not in login_session:
        return render_template('publicarticle.html', categories=categories, category=category, article=article, comments=comments, STATE=state)
    else:
        return render_template('article.html', categories=categories, category=category, article=article, comments=comments, profile_pic=login_session['picture'], profile_id=getUserID(login_session['email']))


###############################    CREATE PAGES    ######################################################################


# NEW CATEGORY
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        flash('You must log in to create a category')
        return redirect(url_for('showCategories'))
    if login_session['user_id'] != 1:
        flash('Only the site owner may create categories')
        return redirect(url_for('showCategories'))
    if request.method == 'POST':
        newcategory = Category(name=request.form['name'], user_id=login_session['user_id'])
        session.add(newcategory)
        session.commit()
        flash('New category created!')
        return redirect(url_for('showCategories'))
    else:
        return render_template('newcategory.html')


# NEW ARTICLE
@app.route('/category/<int:category_id>/article/new/', methods=['GET', 'POST'])
def newArticle(category_id):
    if 'username' not in login_session:
        flash('You must log in to create an article')
        return redirect(url_for('showCatalog', category_id=category_id))
    if request.method == 'POST':
        current_time = str(datetime.now())
        newarticle = Article(title=request.form['title'], tagline=request.form['tagline'], text=request.form['text'], picture=request.form['picture'], date=current_time, last_edited=current_time, category_id=category_id, user_id=login_session['user_id'])
        session.add(newarticle)
        session.commit()
        flash('New article created!')
        return redirect(url_for('showCatalog', category_id=category_id))
    else:
        return render_template('newarticle.html', category_id=category_id)


###############################    EDIT PAGES    ######################################################################


# EDIT CATEGORY
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    if 'username' not in login_session:
        flash('You must log in to edit a category')
        return redirect(url_for('showCatalog', category_id=category_id))
    category = session.query(Category).filter_by(id=category_id).one()
    if category.user_id != login_session['user_id']:
        flash("Only the category's creator may edit it")
        return redirect(url_for('showCatalog', category_id=category_id))
    if request.method == 'POST':
        if request.form['name']:
            category.name = request.form['name']
        session.add(category)
        session.commit()
        flash('Category edited!')
        return redirect(url_for('showCatalog', category_id=category_id))
    else:
        return render_template('editcategory.html', category=category)


# EDIT ARTICLE
@app.route('/category/<int:category_id>/article/<int:article_id>/edit/', methods=['GET', 'POST'])
def editArticle(category_id, article_id):
    if 'username' not in login_session:
        flash('You must log in to edit an article')
        return redirect(url_for('showArticle', category_id=category_id, article_id=article_id))
    article = session.query(Article).filter_by(id=article_id).one()
    if article.user_id != login_session['user_id']:
        flash('Only the author may edit this article')
        return redirect(url_for('showArticle', category_id=category_id, article_id=article_id))
    if request.method == 'POST':
        if request.form['title']:
            article.title = request.form['title']
        if request.form['tagline']:
            article.tagline = request.form['tagline']
        if request.form['text']:
            article.text = request.form['text']
        if request.form['picture']:
            article.picture = request.form['picture']
        article.last_edited = str(datetime.now())
        session.add(article)
        session.commit()
        flash("Article edited!")
        return redirect(url_for('showArticle', category_id=category_id, article_id=article_id))
    else:
        return render_template('editarticle.html', article=article)


# EDIT COMMENT
@app.route('/comment/<int:comment_id>/edit/', methods=['GET', 'POST'])
def editComment(comment_id):
    comment = session.query(Comment).filter_by(id=comment_id).one()
    if 'username' not in login_session:
        flash('You must log in to edit a comment')
        return redirect(url_for('showArticle', category_id=comment.article.category_id, article_id=comment.article_id))
    if comment.user_id != login_session['user_id']:
        flash('Only the commenter may edit this comment')
        return redirect(url_for('showArticle', category_id=comment.article.category_id, article_id=comment.article_id))
    if request.method == 'POST':
        if request.form['text']:
            comment.text = request.form['text']
        comment.last_edited = str(datetime.now())
        session.add(comment)
        session.commit()
        flash("Comment edited!")
        return redirect(url_for('showArticle', category_id=comment.article.category_id, article_id=comment.article.id))
    else:
        return render_template('showArticle', category_id=comment.article.category_id, article_id=comment.article.id)


###############################    DELETE PAGES    ######################################################################


# DELETE CATEGORY
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    if 'username' not in login_session:
        flash('You must log in to delete a category')
        return redirect(url_for('showCatalog', category_id=category_id))
    category = session.query(Category).filter_by(id=category_id).one()
    if category.user_id != login_session['user_id']:
        flash("Only the category's creator may delete it")
        return redirect(url_for('showCatalog', category_id=category_id))
    if request.method == 'POST':
        session.delete(category)
        session.commit()
        flash("Category deleted!")
        return redirect(url_for('showCategories'))
    else:
        return render_template('deletecategory.html', category=category)


# DELETE ARTICLE
@app.route('/category/<int:category_id>/article/<int:article_id>/delete/', methods=['GET', 'POST'])
def deleteArticle(category_id, article_id):
    if 'username' not in login_session:
        flash('You must log in to delete an article')
        return redirect(url_for('showArticle', category_id=category_id, article_id=article_id))
    article = session.query(Article).filter_by(id=article_id).one()
    if article.user_id != login_session['user_id']:
        flash('Only the author may delete this article')
        return redirect(url_for('showArticle', category_id=category_id, article_id=article_id))
    if request.method == 'POST':
        session.delete(article)
        session.commit()
        flash("Article deleted!")
        return redirect(url_for('showCatalog', category_id=category_id))
    else:
        return render_template('deletearticle.html', article=article)


# DELETE COMMENT
@app.route('/comment/<int:comment_id>/delete/', methods=['GET', 'POST'])
def deleteComment(comment_id):
    comment = session.query(Comment).options(joinedload_all('*')).filter_by(id=comment_id).one()
    if 'username' not in login_session:
        flash('You must log in to delete a comment')
        return redirect(url_for('showArticle', category_id=comment.article.category_id, article_id=comment.article_id))
    if comment.user_id != login_session['user_id']:
        flash('Only the commenter may delete this comment')
        return redirect(url_for('showArticle', category_id=comment.article.category_id, article_id=comment.article_id))
    if request.method == 'POST':
        session.delete(comment)
        session.commit()
        flash("Comment deleted!")
        return redirect(url_for('showArticle', category_id=comment.article.category_id, article_id=comment.article_id))
    else:
        return render_template('showArticle', category_id=comment.article.category_id, article_id=comment.article_id)


###############################    JSON    ######################################################################


# MAIN MENU JSON
@app.route('/categories/JSON/')
@app.route('/category/JSON/')
@app.route('/JSON/')
@app.route('/categories/json/')
@app.route('/category/json/')
@app.route('/json/')
def mainmenuJSON():
    articles = session.query(Article).order_by(Article.date.desc()).all()
    return jsonify(Articles=[article.serialize for article in articles])


# CATEGORY JSON
@app.route('/category/<int:category_id>/article/JSON/')
@app.route('/category/<int:category_id>/JSON/')
@app.route('/category/<int:category_id>/article/json/')
@app.route('/category/<int:category_id>/json/')
def categoryJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    articles = session.query(Article).filter_by(category_id=category_id).order_by(Article.date.desc()).all()
    return jsonify(Articles=[article.serialize for article in articles])


# AUTHOR JSON
@app.route('/author/<int:author_id>/JSON/')
@app.route('/author/<int:author_id>/json/')
def authorJSON(author_id):
    author = session.query(User).filter_by(id=author_id).one()
    articles = session.query(Article).filter_by(user_id=author_id).order_by(Article.date.desc()).all()
    return jsonify(Articles=[article.serialize for article in articles])


# FULL ARTICLE JSON
@app.route('/category/<int:category_id>/article/<int:article_id>/JSON/')
@app.route('/category/<int:category_id>/article/<int:article_id>/json/')
def articleJSON(category_id, article_id):
    article = session.query(Article).filter_by(id=article_id).one()
    return jsonify(Article=[article.serialize])


###############################    ATOM FEEDS    ######################################################################


# MAIN MENU FEED
@app.route('/categories/rss/')
@app.route('/category/rss/')
@app.route('/rss/')
@app.route('/categories/atom/')
@app.route('/category/atom/')
@app.route('/atom/')
def recentFeed():
    articles = session.query(Article).order_by(Article.date.desc()).limit(15).all()
    feed = AtomFeed('Recent Articles', feed_url=request.url, url=request.url_root)
    for article in articles:
        new_date = reformat_date(article.date)
        last_edited = reformat_date(article.last_edited)
        feed.add(article.title, unicode(article.text), content_type='html', author=article.user.name, url=make_external(url_for('showArticle', category_id=article.category.id, article_id=article.id)), updated=last_edited, published=new_date)
    return feed.get_response()


# CATEGORY MENU FEED
@app.route('/category/<int:category_id>/article/rss/')
@app.route('/category/<int:category_id>/rss/')
@app.route('/category/<int:category_id>/article/atom/')
@app.route('/category/<int:category_id>/atom/')
def categoryFeed(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    articles = session.query(Article).filter_by(category_id=category_id).order_by(Article.date.desc()).limit(15).all()
    feedname = category.name + " Articles"
    feed = AtomFeed(feedname, feed_url=request.url, url=request.url_root)
    for article in articles:
        new_date = reformat_date(article.date)
        last_edited = reformat_date(article.last_edited)
        feed.add(article.title, unicode(article.text), content_type='html', author=article.user.name, url=make_external(url_for('showArticle', category_id=article.category.id, article_id=article.id)), updated=last_edited, published=new_date)
    return feed.get_response()


# AUTHOR MENU FEED
@app.route('/author/<int:author_id>/rss/')
@app.route('/author/<int:author_id>/atom/')
def authorFeed(author_id):
    author = session.query(User).filter_by(id=author_id).one()
    articles = session.query(Article).filter_by(user_id=author_id).order_by(Article.date.desc()).limit(15).all()
    feedname = author.name + "'s Articles"
    feed = AtomFeed(feedname, feed_url=request.url, url=request.url_root)
    for article in articles:
        new_date = reformat_date(article.date)
        last_edited = reformat_date(article.last_edited)
        feed.add(article.title, unicode(article.text), content_type='html', author=article.user.name, url=make_external(url_for('showArticle', category_id=article.category.id, article_id=article.id)), updated=last_edited, published=new_date)
    return feed.get_response()


###############################    HELPER FUNCTIONS    ######################################################################


# Add user to database
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Get user from id
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# Get user id from email
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Atom feed helper function
def make_external(url):
    return urljoin(request.url_root, url)


# Change date string into a python datetime object
def reformat_date(datestring):
    new_date = datestring
    new_date = new_date[0:19]
    new_date = new_date.replace(" ", "T")
    new_date = datetime.strptime(new_date, "%Y-%m-%dT%H:%M:%S")
    return new_date


###############################    SETUP    ######################################################################


# Flask setup
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
