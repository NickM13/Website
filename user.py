import database
import flask


class User():

    def __init__(self, username, email, password, display_name):
        self.id = username
        self.username = username
        self.display_name = display_name
        self.email = email
        self.password = password
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


def update_profile(user: User, display_name: str, email: str):
    if user.email == email and user.display_name == display_name:
        return 0

    user.display_name = display_name
    user.email = email

    database.execute(
        "update users set display_name=(%s), email=(%s), modified=current_timestamp where username=(%s)", (user.display_name, user.email, user.username))
    return 1


def register_new_user(username: str, password: str, email: str, display_name: str):
    database.execute(
        "insert into users (username, password, email, display_name, created) values (%s, %s, %s, %s, current_timestamp)", (username, password, email, display_name))

    return User(username=username, email=email, password=password, display_name=display_name)


def get_by_login(username: str, password: str):
    query = database.query(
        "select * from users where lower(username) = (%s) and password = (%s)", (username.lower(), password), True)

    if not query:
        return None

    return User(display_name=query['display_name'],
                username=query['username'],
                email=query['email'],
                password=query['password'])


def get_by_username(username: str):
    query = database.query(
        "select * from users where lower(username) = (%s)", (username.lower(),), True)

    if not query:
        return None

    return User(username=query['username'],
                email=query['email'],
                password=query['password'],
                display_name=query['display_name'])
