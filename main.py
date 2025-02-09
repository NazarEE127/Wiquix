from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os
from instance.DataBase import *
import requests


ALLOWED_EXTENSIONS = {'png', 'jpg', 'dng', 'raw', 'ARW', 'mp4', 'avi', 'mov'}
PHOTO_FORMAT = {'png', 'jpg', 'dng', 'raw', 'ARW'}
VIDEO_FORMAT = {'mp4', 'avi', 'mov'}

app = Flask(__name__)
app.secret_key = '79d77d1e7f9348c59a384d4376a9e53f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOAD_FOLDER'] = 'static/img'
db.init_app(app)
manager = LoginManager(app)


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/profile')
def profile():
    user = User.query.get(current_user.id)
    return render_template("profile.html", user=user)


"""РЕГИСТРАЦИЯ, ВХОД И ВЫХОД"""


@app.route('/sign-up', methods=["POST", "GET"])
def sign_up():
    if request.method == "GET":
        return render_template("sign-up.html")
    mail = request.form.get('mail')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    fio = request.form.get('F') + " " + request.form.get('I') + " " + request.form.get('O')
    user = User.query.filter_by(mail=mail).first()
    file = request.files['file']
    file.save(os.path.join('static/img', file.filename))
    if len(mail) > 50:
        flash("Слишком длинный логин")
        return render_template("sign-up.html")
    if user is not None:
        flash('Имя пользователя занято!')
        return render_template("sign-up.html")

    if password != password2:
        flash("Пароли не совпадают!")
        return render_template("sign-up.html")
    try:
        hash_pwd = generate_password_hash(password)
        new_user = User(mail=mail, password=hash_pwd, fio=fio, ava=file.filename)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/")

    except:
        flash("Возникла ошибка при регистрации")
        return render_template("sign-up.html")


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        mail = request.form.get('mail')
        password = request.form.get('password')
        user = User.query.filter_by(mail=mail).first()
        if user is not None:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect('/')
            else:
                flash('Неверный логин или пароль')
        else:
            flash('Такого пользователя не существует')
    return render_template("login.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
