import os
from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from forms import SignupForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.config["MONGO_DBNAME"] = 'recipe_me'
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

mongo = PyMongo(app)

@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def home():
    ''' function to display the landing page with all recipes '''
    
    return render_template('index.html', recipes=mongo.db.recipes.find())


@app.route('/about')
def about():
    ''' function to display the about page '''
    
    return render_template('about.html', title="About")
    

@app.route('/sign_up', methods=["GET", "POST"])
def sign_up():
    ''' function to display the sign up page with a form for 
        users to create an account. Firstly it checks that the form 
        has been filled in correctly. Then if there is no existing user, it 
        creates an account and notifies the users they are now logged in on that account.
        If the username already exists it gives them a message to try another name.'''
        
    form = SignupForm()
    # Checking form has been filled in correctly
    if form.validate_on_submit():
        users = mongo.db.users
        existing_user = users.find_one({'username' : request.form['username']})
        
        # If username isn't already in database
        if existing_user is None:
            hash_password = generate_password_hash(request.form['password'])
            # Create an account
            users.insert_one({'username': request.form['username'], 'password': hash_password})
            # Notify them
            flash(f'Account created for \'{form.username.data}\'!', 'success')
            session['username'] = request.form['username']
            session['logged'] = True
            return redirect(url_for('home'))
        else:
            # If username already exists then tell user to try another username
            flash(f'Username \'{form.username.data}\' already exists! Please choose a different username', 'danger')
            return redirect(url_for('sign_up'))
        
    return render_template('sign_up.html', title="Sign Up", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    ''' function to display the login page with a form for 
        users to enter their details. Firstly it checks that the form 
        has been filled in correctly. Then it checks that the username exists. 
        If it doesn't it notifies the user. If it does it checks the passwords match 
        and if they do logs the user in. 
        If they don't it notifies them of an incorrect password '''
    
    form = LoginForm()
    # Checking form has been filled in correctly
    if form.validate_on_submit():
        users = mongo.db.users
        get_user = users.find_one({'username': request.form['username']})
        # If the username exists, check passwords match and sign them in if they do
        if get_user:
            password = form.password.data
            if check_password_hash(get_user['password'], password):
                flash(f'You  are logged in as \'{form.username.data}\'', 'success')
                session['username'] = request.form['username']
                session['logged'] = True
                return redirect(url_for('home'))
            else:
                # If the passwords don't matach inform the user
                flash('Incorrect password please try again!', 'danger')
                return redirect(url_for('login'))
        else:
            # If the username doesn't exist inform the user
            flash(f'Username \'{form.username.data}\' does not exist', 'danger')
            return redirect(url_for('login'))
            
    return render_template('login.html', title="Login", form=form)
    
@app.route('/recipe/<id>', methods=['GET', 'POST'])
def recipe(id):
    ''' function to display a single recipe that the user has
        selected to view '''
        
    ad_equipment = ['pan']
    selected_recipe = mongo.db.recipes.find_one({'_id': ObjectId(id)})
    return render_template('view_recipe.html', recipe=selected_recipe, title='Recipe', ad_equipment=ad_equipment)

@app.route('/logout')
def logout():
    '''function that allows a user to logout'''

    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)