from wtforms import Form, StringField, PasswordField, validators, FileField, TextAreaField
import user
import flask


class ProfileForm(Form):
    display_name = StringField('Display Name', [validators.Length(
        min=1, max=40)])
    email = StringField('Email', [validators.Length(
        min=6, max=40)])
    picture = FileField('Profile Picture')

    def validate_on_submit(self):
        return self.validate


class AddServerForm(Form):
    game = StringField('Game', [validators.Length(min=1, max=40)])
    name = StringField('Name', [validators.Length(min=1, max=40)])
    ip = StringField('IP Address', [validators.Length(min=1, max=40)])
    description = TextAreaField('Description')

    def validate_on_submit(self):
        return self.validate


class RegistrationForm(Form):
    email = StringField('Email', [validators.Length(min=6, max=40)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    display_name = StringField(
        'Display Name', [validators.Length(min=1, max=40)])
    discord = StringField('Discord Username', [
                          validators.Length(min=4, max=28)])
    password = PasswordField('Password', [validators.Length(min=4, max=28)])
    password_confirm = PasswordField(
        'Confirm Password', [validators.Length(min=4, max=28)])

    def validate_on_submit(self):
        success = True
        if not self.validate():
            flask.flash("Failed to validate")
            success = False

        if not user.allowed_email(self.email.data):
            flask.flash("Email is not valid")
            success = False

        if user.get_by_username(self.username.data) is not None:
            flask.flash("Username already taken")
            success = False

        return success


class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=1)])
    password = PasswordField('Password', [validators.Length(min=1)])

    def validate_on_submit(self):
        if not self.validate():
            return False

        self.user = user.get_by_login(self.username.data, self.password.data)

        return self.user is not None
