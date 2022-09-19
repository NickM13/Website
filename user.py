from dis import disco
import re

import database
import servers

discord_regex = r'\b^.{3,32}#[0-9]{4}$\b'
email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


class User():

    def __init__(self, username, email, password, display_name, discord, picture=None):
        self.id = username
        self.username = username
        self.display_name = display_name
        self.email = email
        self.password = password
        self.discord = discord
        self.picture = picture
        self.notifications = []

        self.is_active = True
        self.is_authenticated = True
        self.is_anonymous = False

    def is_active(self):
        return self.is_active

    def is_authenticated(self):
        return self.is_authenticated

    def is_anonymous(self):
        return self.is_anonymous

    def get_id(self):
        return self.username

    def get_notifications(self):
        return self.notifications

    def get_picture(self):
        return ('uploads/' + self.picture) if self.picture else ('img/GuineaPig.png')

    def get_owned_servers(self):
        return servers.get_all_servers(f"owner = '{self.username}'")


def allowed_discord(discord: str):
    return re.fullmatch(discord_regex, discord)


def allowed_email(email: str):
    return re.fullmatch(email_regex, email)


def update_profile(user: User, display_name: str, email: str, discord: str, picture: str):
    if user.email == email and user.display_name == display_name and picture == None and user.discord == discord:
        return 0

    user.display_name = display_name
    user.email = email if allowed_email(email) else user.email
    user.discord = discord if allowed_discord(discord) else user.discord
    user.picture = picture

    database.execute("update users set display_name=(%s), email=(%s), picture=(%s), discord=(%s), modified=current_timestamp where username=(%s)",
     (user.display_name, user.email, user.picture, user.discord, user.username))
    return 1


def register_new_user(username: str, password: str, email: str, display_name: str, discord: str):
    database.execute(
        "insert into users (username, password, email, display_name, discord, created) values (%s, %s, %s, %s, %s, current_timestamp)", (username, password, email, display_name, discord))

    return User(username=username, email=email, password=password, display_name=display_name, discord=discord)


def get_by_login(username: str, password: str):
    query = database.query(
        "select * from users where lower(username) = (%s) and password = (%s)", (username.lower(), password), True)

    if not query:
        return None

    return User(username=query['username'],
                email=query['email'],
                password=query['password'],
                display_name=query['display_name'],
                discord=query['discord'],
                picture=query['picture'])


def get_by_username(username: str):
    query = database.query(
        "select * from users where lower(username) = (%s)", (username.lower(),), True)

    if not query:
        return None

    return User(username=query['username'],
                email=query['email'],
                password=query['password'],
                display_name=query['display_name'],
                discord=query['discord'],
                picture=query['picture'])
