from flask import abort
from flask import Flask
from flask import flash
from flask import jsonify
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from flask import url_for
from werkzeug.security import generate_password_hash

from flask_login import LoginManager
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from flask_pymongo import PyMongo

from models import User
from forms import LoginForm

from bson.objectid import ObjectId

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'

mongo = PyMongo(app)

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/')
def main():
    return redirect(url_for('.login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if not request.json:
            abort(400)

        if not mongo.db.users.find_one({
            'username': request.json['username']
        }):
            mongo.db.users.insert_one({
                'username': request.json['username'],
                'password': generate_password_hash(request.json['password']),
            })

            return jsonify({'ok': True})
        return jsonify({'ok': False, 'error': 'Username already exists'})

    return render_template('register_form.html')

@login_manager.user_loader
def load_user(username):
    user = mongo.db.users.find_one({'username': username})
    if not user:
        return None
    return User(user['username'], user['password'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = mongo.db.users.find_one({'username': form.username.data})
        if user:
            user_obj = User(user['username'], user['password'])
            if user_obj.check_password(form.password.data):
                login_user(user_obj)
                session['username'] = user_obj.username
                return redirect(url_for('.todo_list'))

    return render_template('index.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    session['username'] = ''
    return redirect(url_for('.login'))

@app.route('/todo-list')
@login_required
def todo_list():
    todo_list = mongo.db.todo_list.find({'username': session['username']})
    return render_template(
        'todo_dashboard.html',
        todo_list=todo_list,
        username=session['username'],
    )

@app.route('/todo-list/complete-task', methods=['POST'])
def complete_task():
    if request.method == 'POST':
        if request.json:
            completed = False
            if request.json['completed']:
                completed = True

            mongo.db.todo_list.update_one(
                {'_id': ObjectId(request.json['id'])},
                {'$set': {'completed': completed}}
            )
            return jsonify({'ok': True})
        return jsonify({'ok': False})

@app.route('/todo-list/add-task', methods=['POST'])
def add_task():
    if request.method == 'POST':
        if request.json:
            mongo.db.todo_list.insert_one({
                'username': session['username'],
                'title': request.json['title'],
                'completed': False,
            })

            return jsonify({'ok': True})
        return jsonify({'ok': False})


if __name__ == '__main__':
    app.run()