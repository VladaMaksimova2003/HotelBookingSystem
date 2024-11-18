from flask import Blueprint, render_template, redirect, flash, url_for, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from ..forms import RegistrationForm, LoginForm
from ..extensions import db
from ..models.customer import Customer


customer = Blueprint('customer', __name__)

@customer.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()  # Создание экземпляра формы

    if form.validate_on_submit():  # Проверка валидации данных формы
        hashed_password = generate_password_hash(form.password.data)  # Хэширование пароля
        new_customer = Customer(
            firstname=form.first_name.data,
            lastname=form.last_name.data,
            email=form.email.data,
            phone=form.phone_number.data,
            password_hash=hashed_password
        )
        try: 
            # Добавление и сохранение нового пользователя в базе данных
            db.session.add(new_customer)
            db.session.commit()      
            flash('Регистрация прошла успешно. Войдите в систему.', 'success')
            return redirect(url_for('customer.login'))  # Перенаправление на страницу входа после успешной регистрации
        except Exception as e:
            db.session.rollback()  # Откат транзакции в случае ошибки
            print(str(e))
            flash(f"При регистрации произошла ошибка", "danger")
    return render_template('user/register.html', form=form)  # Передача формы в шаблон


@customer.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Customer.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f"Поздравляем, {user.firstname}! Вы успешно авторизованы", "success")
            return redirect(next_page) if next_page else redirect(url_for('hotel.list_hotels'))
        else:
            flash(f"Ошибка входа. Пожалуйста проверьте логин и пароль!", "danger")
    return render_template('user/login.html', form=form)


@customer.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('hotel.list_hotels'))


