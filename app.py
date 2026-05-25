import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, IntegerField, BooleanField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional

# Инициализация расширений
db = SQLAlchemy()
login_manager = LoginManager()

# Конфигурация
class Config:
    SECRET_KEY = 'pickme-secret-key-2024-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pickme.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)

    photo = db.Column(db.String(255), nullable=True)
    eye_color = db.Column(db.String(50), nullable=True)
    hair_color = db.Column(db.String(50), nullable=True)
    height = db.Column(db.Integer, nullable=True)

    interests = db.Column(db.JSON, default=list)
    relationship_status = db.Column(db.String(50), default='active_search')

    preferred_age_min = db.Column(db.Integer, nullable=True)
    preferred_age_max = db.Column(db.Integer, nullable=True)
    preferred_city = db.Column(db.String(100), nullable=True)
    preferred_eye_color = db.Column(db.String(50), nullable=True)
    preferred_hair_color = db.Column(db.String(50), nullable=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(),
                                                   Length(min=6, message='Пароль должен быть не менее 6 символов')])
    confirm_password = PasswordField('Подтвердите пароль',
                                     validators=[DataRequired(), EqualTo('password', message='Пароли не совпадают')])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите в систему'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Создание таблиц и админа
with app.app_context():
    db.create_all()

    admin = User.query.filter_by(email='admin@pickme.com').first()
    if not admin:
        admin = User(email='admin@pickme.com', is_admin=True, is_verified=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.flush()

        admin_profile = Profile(
            user_id=admin.id,
            first_name='Admin',
            last_name='PickMe',
            age=25,
            city='Moscow',
            relationship_status='active_search'
        )
        db.session.add(admin_profile)
        db.session.commit()
        print("Admin user created: admin@pickme.com / admin123")
    else:
        print("Admin user already exists")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile_view'))

    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Пользователь с таким email уже существует', 'danger')
        else:
            user = User(email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Регистрация успешно завершена! Заполните свой профиль.', 'success')
            return redirect(url_for('profile_edit'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile_view'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            user.last_active = datetime.utcnow()
            db.session.commit()
            flash(f'Добро пожаловать, {user.email}!', 'success')
            return redirect(url_for('profile_view'))
        flash('Неверный email или пароль', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
