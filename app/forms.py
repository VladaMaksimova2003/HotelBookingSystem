from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import *
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email, NumberRange, Optional
from .models.customer import Customer


class RegistrationForm(FlaskForm):
    first_name = StringField('Your First name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Your Last name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Your Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Repeat your password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        email = Customer.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Данный email уже зарегистрирован. Пожалуйста, используйте другой.')


class LoginForm(FlaskForm):
    email = StringField('Your Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')


class FeatureForm(FlaskForm):
    feature_type = StringField('Тип удобства', validators=[Optional()])
    feature_input = FieldList(StringField('Удобство', validators=[Optional()]), min_entries=1)


class HotelForm(FlaskForm):
    name = StringField('Hotel Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    new_country = StringField('Country', validators=[DataRequired()])
    new_city = StringField('City', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    photos = MultipleFileField('Hotel Photos', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only image files are allowed!'),
    ])
    features = FieldList(FormField(FeatureForm), min_entries=1)
    features_json = HiddenField('Features JSON')
    submit = SubmitField('Add Hotel')


class FeaturesFilterForm(FlaskForm):
    features = FieldList(FormField(FeatureForm), min_entries=1)
    submit = SubmitField('Применить фильтры')


class RoomTypeForm(FlaskForm):
    name = StringField('Название типа комнаты', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    price = FloatField('Цена', validators=[DataRequired(), NumberRange(min=0)])
    currency = SelectField('Валюта', choices=[('USD', 'USD'), ('EUR', 'EUR'), ('RUB', 'RUB')], validators=[DataRequired()])
    features = FieldList(FormField(FeatureForm), min_entries=1)
    features_json = HiddenField('Features JSON') 
    photos = MultipleFileField('Фотографии') 
    submit = SubmitField('Добавить тип комнаты')


# class RoomForm(FlaskForm):
#     number = StringField('Номер комнаты', validators=[DataRequired()])
#     floor_number = IntegerField('Этаж', validators=[DataRequired()])
#     price = DecimalField('Цена', validators=[DataRequired(), NumberRange(min=0)], places=2)
#     currency = SelectField('Валюта', choices=[
#         ('USD', 'Доллар США (USD)'),
#         ('EUR', 'Евро (EUR)'),
#         ('RUB', 'Российский рубль (RUB)'),
#         ('GBP', 'Британский фунт (GBP)'),
#         ('JPY', 'Японская йена (JPY)')
#     ], validators=[DataRequired()])
#     status = SelectField('Статус', choices=[
#         ('Available', 'Доступна'),
#         ('Occupied', 'Занята'),
#         ('Out of Service', 'Вне эксплуатации')
#     ], validators=[DataRequired()])
#     room_class = SelectField('Класс комнаты', choices=[
#         ('Deluxe', 'Делюкс'),
#         ('Standard', 'Стандарт'),
#         ('Economy', 'Эконом'),
#         ('Suite', 'Сюит')
#     ], validators=[DataRequired()])
    
#     feature_type = StringField('Тип удобств (введите или выберите)', validators=[Optional()])
#     feature_input = StringField('Удобство (введите или выберите)', validators=[Optional()])
