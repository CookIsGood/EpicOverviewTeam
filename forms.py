from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, IntegerField
from wtforms.validators import Email, DataRequired, Length, EqualTo, NumberRange, ValidationError
import re

def check_discord_name(form, field):
    match = re.fullmatch(r"\b[0-9a-zA-Z]{1,20}[#]\d{4}", field.data)
    if not match:
        raise ValidationError('You entered a discord nickname not according to the format! For example: nickname#1111')



class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email(), DataRequired()])
    password = PasswordField("Password: ", validators=[DataRequired(), Length(min=5, max=30)])
    submit = SubmitField("Log In")


class RegisterForm(FlaskForm):
    login = StringField("Login: ", validators=[DataRequired(), Length(min=3, max=10)])
    email = StringField("Email: ", validators=[Email(), DataRequired(), Length(min=10, max=25)])
    discord_nickname = StringField('Discord: ', validators=[DataRequired(), Length(min=6, max=25), check_discord_name])
    password = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirm'), Length(min=5, max=30)])
    confirm = PasswordField('Repeat Password', validators=[DataRequired()])
    submit = SubmitField("Register")

class ForgotPasswordForm(FlaskForm):

    email = StringField("Email: ", validators=[Email(), DataRequired(), Length(min=10, max=25)])
    password = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirm'), Length(min=5, max=30)])
    confirm = PasswordField('Repeat Password', validators=[DataRequired()])
    submit = SubmitField("Change password!")


class CreateGameAccountForm(FlaskForm):
    name = StringField("Name: ", validators=[DataRequired(), Length(min=3, max=5)])
    garaunteed_roll = SelectField('Garaunteed Roll', choices=[('Yes', 'Yes'), ('No', 'No')])
    price = IntegerField(validators=[DataRequired(), NumberRange(min=1, max=1000)])
    submit = SubmitField("Create")


class ChangeSettingsGameAccountForm(FlaskForm):
    garaunteed_roll = SelectField('Garaunteed Roll', choices=[('Yes', 'Yes'), ('No', 'No')])
    price = IntegerField(validators=[DataRequired(), NumberRange(min=1, max=1000)])
    status_code = SelectField('Garaunteed Roll',
                              choices=[('SELLING', 'SELLING'), ('SOLD', 'SOLD'), ('PROCESSED', 'PROCESSED')])
    submit = SubmitField("Change")

class CreateRoleForm(FlaskForm):
    role = StringField("Role name: ", validators=[DataRequired(), Length(min=5, max=20)])
    submit = SubmitField("Create")

class ActionWithRole(FlaskForm):
    roles = SelectField('Roles', coerce=str)
    submit = SubmitField("Change")

class CreateStatusForm(FlaskForm):
    status = StringField("Status name: ", validators=[DataRequired(), Length(min=5, max=20)])
    submit = SubmitField("Create")

class ActionWithStatus(FlaskForm):
    statuses = SelectField('Statuses', coerce=str)
    submit = SubmitField("Change")

class ChangeDiscord(FlaskForm):
    discord = StringField('Discord: ', validators=[DataRequired(), Length(min=6, max=25), check_discord_name])
    submit = SubmitField("Change")


