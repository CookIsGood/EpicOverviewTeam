from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, IntegerField, FloatField, TextAreaField
from wtforms.validators import Email, DataRequired, Length, EqualTo, NumberRange, ValidationError
import re

from wtforms.widgets import TextArea


def check_discord_name(form, field):
    match = re.fullmatch(r"\b[0-9a-zA-Z]{1,20}[#]\d{4}", field.data)
    if not match:
        raise ValidationError('You entered a discord nickname not according to the format! For example: nickname#1111')


def check_game_account_name(form, field):
    match = re.fullmatch(r"[0-9a-zA-Z]{2,8}", field.data)
    if not match:
        raise ValidationError('Your game account name contains invalid characters!')


def check_role_name(form, field):
    match = re.fullmatch(r"[a-zA-Z]{5,20}", field.data)
    if not match:
        raise ValidationError('Role name contains invalid characters!')


def check_status_name(form, field):
    match = re.fullmatch(r"[a-zA-Z]{5,20}", field.data)
    if not match:
        raise ValidationError('Status name contains invalid characters!')


def check_hero_name(form, field):
    match = re.fullmatch(r"[a-z-_&.]{2,30}", field.data)
    if not match:
        raise ValidationError('Hero name contains invalid characters!')


def check_artifact_name(form, field):
    match = re.fullmatch(r"[a-z-_&.]{2,50}", field.data)
    if not match:
        raise ValidationError('Artifact name contains invalid characters!')


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email(message="You entered your email out of format!"),
                                               DataRequired(message="You have not filled in the email field!"),
                                               Length(min=5, max=50,
                                                      message="Email length must be between 5 and 50 characters!")], render_kw={
        'id': 'email',
    })
    password = PasswordField("Password: ", validators=[DataRequired(message="You did not fill out the password field!"),
                                                       Length(min=5, max=30, message=
                                                       "The password must be between 5 and 30 characters long!")], render_kw={
        'id': 'password',
    })
    submit = SubmitField("Log In")


class RegisterForm(FlaskForm):
    login = StringField("Login: ", validators=[DataRequired(message="You have not filled in the login field!"),
                                               Length(min=3, max=10,
                                                      message="Login length must be from 3 to 10 characters!")], render_kw={
        'id': 'login',
    })
    email = StringField("Email: ", validators=[Email(message="You entered your email out of format!"),
                                               DataRequired(message="You have not filled in the email field!"),
                                               Length(min=5, max=50,
                                                      message="Email length must be between 5 and 50 characters!")], render_kw={
        'id': 'email',
    })
    discord_nickname = StringField('Discord: ', validators=[DataRequired(message=
                                                                         "You did not fill in the discord field!"),
                                                            Length(min=6, max=25, message="The discord must be "
                                                                                          "between 6 and 25 "
                                                                                          "characters long!"),
                                                            check_discord_name], render_kw={
        'id': 'discord_nickname',
    })
    password = PasswordField('New Password', validators=[DataRequired(message=
                                                                      "You did not fill in the password field!"),
                                                         EqualTo('confirm',
                                                                 message="Password mismatch!"),
                                                         Length(min=5, max=30,
                                                                message="The password must be between 5 and "
                                                                        "30 characters long!")], render_kw={
        'id': 'password',
    })
    confirm = PasswordField('Repeat Password', validators=[DataRequired(message=
                                                                        "You did not fill in the repeat "
                                                                        "password field!")], render_kw={
        'id': 'confirm',
    })
    submit = SubmitField("Register")


class ForgotPasswordForm(FlaskForm):
    email = StringField("Email: ", validators=[Email(message="You entered your email out of format!"),
                                               DataRequired(message="You have not filled in the email field!"),
                                               Length(min=5, max=50,
                                                      message="Email length must be between 5 and 50 characters!")], render_kw={
        'id': 'email',
    })
    password = PasswordField('New Password', validators=[DataRequired(message=
                                                                      "You did not fill in the password field!"),
                                                         EqualTo('confirm', message="Password mismatch!"),
                                                         Length(min=5, max=30, message=
                                                         "The password must be between 5 and 30 characters long!")], render_kw={
        'id': 'password',
    })
    confirm = PasswordField('Repeat Password', validators=[DataRequired(message=
                                                                        "You did not fill in the repeat "
                                                                        "password field!")], render_kw={
        'id': 'confirm',
    })
    submit = SubmitField("Change password!")


class CreateGameAccountForm(FlaskForm):
    name = StringField("Name: ", validators=[DataRequired(message="You did not fill in the name field!"),
                                             Length(min=2, max=8, message=
                                             "The length of the game account name must be from 2 to 8 characters!"),
                                             check_game_account_name], render_kw={
        'id': 'name',
    })
    garaunteed_roll = SelectField('Garaunteed Roll', choices=[('Yes', 'Yes'), ('No', 'No')])
    price = IntegerField(validators=[DataRequired(message="You have not filled out the price field!"),
                                     NumberRange(min=1, max=1000,
                                                 message="The price of a game account "
                                                         "must be between $ 1 and $ 1000!")], render_kw={
        'id': 'price',
    })
    submit = SubmitField("Create")


class ChangeSettingsGameAccountForm(FlaskForm):
    garaunteed_roll = SelectField('Garaunteed Roll', choices=[('Yes', 'Yes'), ('No', 'No')])
    price = IntegerField(validators=[DataRequired(message="You did not fill in the price field!"),
                                     NumberRange(min=1, max=1000, message="The price of a game account "
                                                                          "must be between $ 1 and $ 1000!")], render_kw={
        'id': 'price',
    })
    status_code = SelectField('Garaunteed Roll',
                              choices=[('SELLING', 'SELLING'), ('SOLD', 'SOLD'), ('PROCESSED', 'PROCESSED')])
    submit = SubmitField("Change")


class CreateRoleForm(FlaskForm):
    role = StringField("Role name: ", validators=[DataRequired(message="You haven't filled out the role field!"),
                                                  Length(min=5, max=20,
                                                         message="Role name must be between 5 and 20 characters!"),
                                                  check_role_name], render_kw={
        'id': 'role',
    })
    submit = SubmitField("Create")


class ActionWithRole(FlaskForm):
    roles = SelectField('Roles', coerce=str)
    submit = SubmitField("Change")


class CreateStatusForm(FlaskForm):
    status = StringField("Status name: ", validators=[DataRequired(message="You haven't filled out the status field!"),
                                                      Length(min=5, max=20,
                                                             message="Status name must be between 5 and 20 characters!"),
                                                      check_status_name], render_kw={
        'id': 'status',
    })
    submit = SubmitField("Create")


class ActionWithStatus(FlaskForm):
    statuses = SelectField('Statuses', coerce=str)
    submit = SubmitField("Change")


class ChangeDiscord(FlaskForm):
    discord = StringField('Discord: ', validators=[DataRequired(message="You did not fill in the discord field!"),
                                                   Length(min=6, max=25, message="The discord must be between "
                                                                                 "6 and 25 characters long!"),
                                                   check_discord_name], render_kw={
        'id': 'discord',
    })
    submit = SubmitField("Change")


class CreateHero(FlaskForm):
    name_hero = StringField('Name: ', validators=[DataRequired(message="You did not fill in the name field!"),
                                                  Length(min=2, max=30,
                                                         message="The length of the hero name must be "
                                                                 "between 2 and 30 characters!"),
                                                  check_hero_name], render_kw={
        'id': 'name_hero',
    })
    star_hero = IntegerField('Star: ', validators=[DataRequired(message="You have not filled out the star field!"),
                                                   NumberRange(min=4, max=5,
                                                               message="The number of stars for "
                                                                       "an hero can be from 4 to 5 stars!")], render_kw={
        'id': 'star_hero',
    })
    rate_hero = FloatField('Rate: ', validators=[DataRequired(message="You have not filled out the rate field!"),
                                                 NumberRange(min=1.0, max=10.0,
                                                             message="The rating of the hero can be from 1.0 to 10.0!")], render_kw={
        'id': 'rate_hero',
    })
    element_hero = SelectField('Element: ',
                               choices=[('fire', 'Fire'), ('ice', 'Ice'), ('earth', 'Earth'), ('light', 'Light'),
                                        ('Dark', 'dark')])
    classes_hero = SelectField('Class: ',
                               choices=[('knight', 'Knight'), ('warrior', 'Warrior'), ('thief', 'Thief'),
                                        ('mage', 'Mage'), ('soul_weaver', 'Soul weaver'), ('ranger', 'Ranger')])
    submit = SubmitField("Create hero")


class ChangeHero(FlaskForm):
    name_hero = StringField('Name: ', validators=[DataRequired(message="You did not fill in the name field!"),
                                                  Length(min=2, max=30,
                                                         message="The length of the hero name must be "
                                                                 "between 2 and 30 characters!"),
                                                  check_hero_name], render_kw={
        'id': 'name_hero',
    })
    star_hero = IntegerField('Star: ', validators=[DataRequired(message="You have not filled out the star field!"),
                                                   NumberRange(min=4, max=5,
                                                               message="The number of stars for "
                                                                       "an hero can be from 4 to 5 stars!")], render_kw={
        'id': 'star_hero',
    })
    rate_hero = FloatField('Rate: ', validators=[DataRequired(message="You have not filled out the rate field!"),
                                                 NumberRange(min=1.0, max=10.0,
                                                             message="The rating of the hero can be from 1.0 to 10.0!")], render_kw={
        'id': 'rate_hero',
    })
    element_hero = SelectField('Element: ',
                               choices=[('fire', 'Fire'), ('ice', 'Ice'), ('earth', 'Earth'), ('light', 'Light'),
                                        ('Dark', 'dark')])
    classes_hero = SelectField('Class: ',
                               choices=[('knight', 'Knight'), ('warrior', 'Warrior'), ('thief', 'Thief'),
                                        ('mage', 'Mage'), ('soul_weaver', 'Soul weaver'), ('ranger', 'Ranger')])
    submit = SubmitField("Change hero")


class CreateArtifact(FlaskForm):
    name_artifact = StringField('Name: ', validators=[DataRequired(message="You did not fill in the name field!"),
                                                      Length(min=2, max=50,
                                                             message="The length of the artifact name must be "
                                                                     "between 2 and 50 characters!"),
                                                      check_artifact_name], render_kw={
        'id': 'name_artifact',
    })
    star_artifact = IntegerField('Star: ', validators=[DataRequired(message="You have not filled out the star field!"),
                                                       NumberRange(min=4, max=5,
                                                                   message="The number of stars for "
                                                                           "an artifact can be from 4 to 5 stars!")], render_kw={
        'id': 'star_artifact',
    })
    classes_artifact = SelectField('Class: ',
                                   choices=[('knight', 'Knight'), ('warrior', 'Warrior'), ('thief', 'Thief'),
                                            ('mage', 'Mage'), ('soul_weaver', 'Soul weaver'), ('ranger', 'Ranger')])
    submit = SubmitField("Create artifact")


class ChangeArtifact(FlaskForm):
    name_artifact = StringField('Name: ', validators=[DataRequired(message="You did not fill in the name field!"),
                                                      Length(min=2, max=50,
                                                             message="The length of the artifact name must be "
                                                                     "between 2 and 50 characters!"),
                                                      check_artifact_name], render_kw={
        'id': 'name_artifact',
    })
    star_artifact = IntegerField('Star: ', validators=[DataRequired(message="You have not filled out the star field!"),
                                                       NumberRange(min=4, max=5,
                                                                   message="The number of stars for "
                                                                           "an artifact can be from 4 to 5 stars!")], render_kw={
        'id': 'star_artifact',
    })
    classes_artifact = SelectField('Class: ',
                                   choices=[('knight', 'Knight'), ('warrior', 'Warrior'), ('thief', 'Thief'),
                                            ('mage', 'Mage'), ('soul_weaver', 'Soul weaver'), ('ranger', 'Ranger')])
    submit = SubmitField("Change artifact")


class ContactForm(FlaskForm):
    discord = StringField('Discord: ', validators=[DataRequired(message='You did not fill in the discord field!'),
                                                   Length(min=6, max=25, message='The discord must be between '
                                                                                 '6 and 25 characters long!'),
                                                   check_discord_name], render_kw={
        'class': 'form-control',
        'id': 'discord',
        'type': 'text',
        'placeholder': 'Enter your discord...',
        'data-sb-validations': 'required',

    })
    email = StringField('Email: ', validators=[DataRequired(message='You have not filled out the email field!'),
                                               Email(message='You entered your email out of format!'),
                                               Length(min=5, max=50,
                                                      message="Email length must be between 5 and 50 characters!")
                                               ], render_kw={
        'class': 'form-control',
        'id': 'email',
        'type': 'email',
        'placeholder': 'Enter your email...',
        'data-sb-validations': 'required,email',

    })
    title = StringField('Title: ', validators=[DataRequired(message='You didn`t fill out the title field!'),
                                               Length(min=5, max=100, message='The title field must be between 5 '
                                                                              'and 100 characters long!')], render_kw={
        'class': 'form-control',
        'id': 'title',
        'type': 'text',
        'placeholder': 'Enter your title...',
        'data-sb-validations': 'required',

    })
    message = TextAreaField('Message: ', validators=[DataRequired(message='You have not filled out the message field!'),
                                                   Length(min=10, max=1000, message='The length of the message field '
                                                                                    'must be between 10 and 1000 '
                                                                                    'characters!')], render_kw={
        'class': 'form-control',
        'id': 'message',
        'type': 'text',
        'style': 'height: 10rem',
        'placeholder': 'Enter your message...',
        'data-sb-validations': 'required',

    })
    submit = SubmitField('Send message!', render_kw={
        'class': 'btn btn-primary btn-lg',
        'id': 'submitButton',
        'type': 'submit',
    })
