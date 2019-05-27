from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000)) # Change made
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))  
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
    
def __init__(self, username, password):
        self.username = username
        self.password = password

def no_entry(text):
    if not text:
        return " is required."

def length_check(text):
    if len(text) < 3:
        return " must have at least 3 characters."

def password2_check(password, password2):
    if password != password2:
        return "Password 2 must match password."

@app.before_request ## defines what routes are allowed without login
def require_login():
    allowed_routes = ['login', 'signup', 'view_blogs', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        flash("You must log in to perform that action")
        return redirect('/login')

@app.route('/') ## sets homepage to show all blogs
def index():
    show_all = User.query.all()
    return render_template('index.html', users=show_all)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first() ## checks whether the username exists

        if user:
            if user.password == password:
                session['username'] = username ## stores the username in the session
                flash("Logged in")
                return redirect('/newpost')
            else:
                flash("Incorrect password entered")
                return redirect('/login')         
        else:
            flash('User does not exist')
            return redirect('/login')

    return render_template('login.html')    

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']
        existing_user = User.query.filter_by(username=username).first()  ## checks whether the user exists

        if not existing_user:
            if no_entry(username):
                flash("Username" + no_entry(username))
                return redirect('/signup')
            elif length_check(username):
                flash("Username" + length_check(username))
                return redirect('/signup')
            if no_entry(password):
                flash("Password" + no_entry(password))
                return redirect('/signup')
            elif length_check(password):
                flash("Password" + length_check(password))
                return redirect('/signup')
            if password2_check(password, password2):
                flash(password2_check(password, password2))
                return redirect('/signup')   
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username ## stores the username in the session
            return redirect('/newpost')
        else:
            flash("Username already exists")
            return redirect('/signup')
    return render_template('signup.html')

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    owner = User.query.filter_by(username=session['username']).first()  ##gets the current users username

    if request.method == 'POST':
        add_title = request.form['blog_title']
        add_blog = request.form['blog_post']

        add_all = Blog(add_title, add_blog, owner)

        if no_entry(add_title):
            flash("Title" + no_entry(add_title))
            return redirect('/newpost')
        if no_entry(add_blog):
            flash("Blog post" + no_entry(add_blog))
            return redirect('/newpost')
        db.session.add(add_all)
        db.session.commit()
        show_blog = "/all_blogs?id=" + str(add_all.id) ## redirects to the posted blog
        return redirect(show_blog)
    else:
        return render_template('newpost.html')

@app.route('/all_blogs')
def view_blogs():
    blog_id = request.args.get('id')
    user_id = request.args.get('user')

    if blog_id: ## if ?blog= is in route then shows that blog
        view_blog=Blog.query.get(blog_id)
        return render_template('view_blog.html', blog=view_blog)
    if user_id: ## if ?user= is in route then shows that users blogs
        view_blogs=Blog.query.filter_by(owner_id=user_id)
        return render_template('singleUser.html', blogs=view_blogs)

    show_all = Blog.query.all() ## else shows all blogs
    return render_template('all_blogs.html', blogs=show_all)

@app.route('/logout')
def logout():
    del session['username'] ## deleted the username from the session
    return redirect('/all_blogs')

if __name__ == '__main__':
    app.run()