from flask import Flask, g, render_template, flash, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import check_password_hash
import models
import forms

DEBUG=True
PORT=8000
HOST='0.0.0.0'

app= Flask(__name__)
app.secret_key = 'jkl23b547843othcni.c.t0tc.5ctt.y54dfdsjkbvuivbioh!'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None

@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db=models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the dataabse comnection after each request""" 
    g.db.close()
    return response   

@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("You registered!", "success")
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)   


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                    login_user(user)
                    flash("You have logged in", "success")
                    return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    return render_template('login.html',form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You' ve been logged out!", "success")
    return redirect(url_for('index'))

@app.route('/new_post', methods=('GET', 'POST'))  
@login_required
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        models.Post.create(user=g.user._get_current_object(),
                           content=form.content.data.strip())
        flash("Message posted! Thanks!", "success")    
        return redirect(url_for('index'))
    return render_template('login.html',form=form)
    

@app.route('/')
def index():
    return 'Hey'    

if __name__ == '__main__':
    models.initialize()
    try:
       models.User.create_user(
          username='rashid',
          email='coderahsapl@gmail.com',
          password='password',
          admin=True
         )
    except ValueError:
        pass     
    app.run(debug=DEBUG, host=HOST, port=PORT)    