from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from dotenv import load_dotenv

import datetime
import os
from string import ascii_uppercase, digits
from random import choices, randint


from database import db
from models import User, Link, GameResult

load_dotenv()

TIME_DELTA = int(os.environ.get("TIME_DELTA"))
LINK_CREATE_DELTA = int(os.environ.get("LINK_DELTA"))


def create_link() -> str:
    links = Link.query.all()
    link = "".join(choices(ascii_uppercase + digits, k=7))
    while link in links:
        link = "".join(choices(ascii_uppercase + digits, k=7))
    return link


def find_user(request):
    email = request.form.get("email")
    user = User.query.filter_by(email=email).first()
    return user


views = Blueprint(name="views", import_name=__name__)


@views.route(rule="/register/", methods=["get", "post"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        if not username:
            flash(message="Необходимо указать имя пользователя", category="error")
            return redirect(url_for("views.register"))
        if not email:
            flash(message="Необходимо указать email пользователя", category="error")
            return redirect(url_for("views.register"))
        if not password:
            flash(message="Необходимо указать пароль пользователя", category="error")
            return redirect(url_for("views.register"))
        user = User.query.filter_by(email=email).first()
        if user:
            flash(message="Пользователь с указанным email существует", category="error")
            return redirect(url_for("views.login"))
        new_user = User(username=username, email=email, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
        except Exception as e:
            print(e)
            return redirect(url_for("views.register"))
        new_link = Link(user_id=new_user.id)
        new_link.link = create_link()
        try:
            db.session.add(new_link)
            db.session.commit()
        except Exception as e:
            print(e)
        flash(message="Регистрация выполнена", category="success")
        return redirect(url_for("views.home"))
    return render_template("register.html")


@views.route("/login/", methods=["get", "post"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        user = find_user(request)
        if user and user.password == password:
            login_user(user, remember=True)
            flash(message="Вход произведен", category="success")
            return redirect(url_for("views.home"))
        else:
            flash(message="Неверный адрес почты или пароль", category="error")
            return redirect(url_for("views.login"))
    return render_template("login.html")


@views.route("/logout/")
@login_required
def logout():
    logout_user()
    flash(message="Выход произведен", category="success")
    return redirect(url_for("views.login"))


@views.route(rule="/", methods=["get"])
@login_required
def home():
    results = (
        GameResult.query.filter_by(user_id=current_user.id)
        .order_by(GameResult.id.desc())
        .limit(3)
    )
    return render_template("index.html", user=current_user, results=results)


@views.route("/<link>")
def login_with_link(link):
    user_link = Link.query.filter_by(link=link).first()
    if user_link and user_link.exp_date < datetime.datetime.now():
        user_link.active = False
        db.session.commit()
        logout_user()
        flash(message="Истек срок действия данной ссылки", category="error")
        redirect(url_for("views.login"))
    if user_link and user_link.active and user_link.exp_date > datetime.datetime.now():
        user = user_link.user
        login_user(user, remember=True)
        flash(message="Вход выполнен", category="success")
        return redirect(url_for("views.home"))
    flash(message="Данной ссылки не существует", category="error")
    return redirect(url_for("views.login"))


@views.route("/random_number/")
@login_required
def random_number():
    number = randint(1, 1000)
    result = GameResult()
    result.number = number
    result.user_id = current_user.id
    if number % 2:
        result.win = "Вы ничего не выиграли"
    elif number > 900:
        result.win = f"Вы выиграли {round(number*0.7, 2)}"
    elif number > 600 and number <= 900:
        result.win = f"Вы выиграли {round(number*0.5, 2)}"
    elif number > 300 and (number <= 600 or number <= 900):
        result.win = f"Вы выиграли {round(number*0.3, 2)}"
    elif number <= 300:
        result.win = f"Вы выиграли {round(number*0.1, 2)}"
    try:
        db.session.add(result)
        db.session.commit()
    except Exception as e:
        print(e)
    return redirect(url_for("views.home"))


@views.route("/update/")
@login_required
def update_link():
    if (
        current_user.link.created + datetime.timedelta(days=LINK_CREATE_DELTA)
    ) > datetime.datetime.now():
        flash(message="Можно создавать ссылку каждые 24 часа", category="error")
        return redirect(url_for("views.home"))
    updated_link = current_user.link
    updated_link.exp_date = datetime.datetime.now() + datetime.timedelta(
        days=TIME_DELTA
    )
    updated_link.created = datetime.datetime.now()
    updated_link.link = create_link()
    try:
        current_user.link = updated_link
        db.session.commit()
    except Exception as e:
        print(e)
    return redirect(url_for("views.home"))
