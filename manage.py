import os
#use flask-script to automate tasks to manage applications
from flask_script import Manager

#Use app object from __init__
from blog import app

#Import database connection session and database table Post
from blog.database import session, Post

# Libraries/objects to manage users
from getpass import getpass
from werkzeug.security import generate_password_hash
from blog.database import User

# Libraries/objects to manage db migration using Flask-Migrate/Alembic
from flask_migrate import Migrate, MigrateCommand
from blog.database import Base

manager = Manager(app)

@manager.command
def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

@manager.command
def seed():
    content = """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""

    for i in range(25):
        post = Post(
            title="Test Post #{}".format(i),
            content=content
        )
        session.add(post)
    session.commit()

@manager.command
def adduser():
    name = raw_input("Name: ")
    email = raw_input("Email: ")
    if session.query(User).filter_by(email=email).first():
        print("User with that email address already exists")
        return

    password = ""
    password_2 = ""
    while len(password) < 8 or password != password_2:
        password = getpass("Password: ")
        password_2 = getpass("Re-enter password: ")
    user = User(name=name, email=email,
                password=generate_password_hash(password))
    session.add(user)
    session.commit()

class DB(object):
    def __init__(self, metadata):
        self.metadata = metadata

migrate = Migrate(app, DB(Base.metadata))
manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()