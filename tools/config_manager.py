"""Config Generator module"""
import logging
import os
import re

import validators
from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

import database
from definitions import CONFIG_PATH
from models import Users, InitDB
from .config_loader import load_config

Session = sessionmaker(bind=database.engine)
session = Session()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
logging.getLogger('passlib').setLevel(logging.ERROR)

config = load_config()


def _save_config():
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
    except Exception as e:
        print(f"Error saving config file: {e}")


def _is_domain_valid(domain: str) -> bool:
    return validators.domain(domain)


def _is_no_users():
    userlist = session.query(Users.username).all()
    if len(userlist) == 0:
        return True
    return False


def _domain_selection(unattended: bool = False):
    if unattended:
        config.set('SERVER', 'DOMAIN', 'yourmancaveman.domain.com')
        _save_config()
        return None
    while True:
        domain = input(
            'Enter your application domain name. This is equired for password reset emails\n'
            'Enter domain name: ').strip()
        if _is_domain_valid(domain):
            config.set('SERVER', 'DOMAIN', domain)
            _save_config()
            return None
        else:
            print('ERROR: Invalid domain name. Please try again.')


def _set_smtp_config(unattended: bool = False):
    if unattended:
        print('WARNING: Password reset emails will NOT be sent. See config.ini!')
        config.set('EMAIL', 'ENABLED', 'False')
        _save_config()
        return None

    while True:
        gmail_user = input('Please enter your gmail username (without @gmail.com): ').strip()
        if '@' in gmail_user.lower():
            print('ERROR: Please enter your gmail account name without the @gmail.com part')
        else:
            config.set('EMAIL', 'USERNAME', gmail_user.lower())
            _save_config()
            break

    while True:
        gmail_app_pass = input('Please enter your gmail app password (abcd abcd abcd abcd): ').lower().strip()
        # I'm not sure if this is always the case. I created a few and turned out all same but who knows.
        app_pw_pattern = re.compile(r'[a-z]{4} [a-z]{4} [a-z]{4} [a-z]{4}')
        if not app_pw_pattern.fullmatch(gmail_app_pass):
            print(
                'ERROR: Invalid app password. It should look like "abcd abcd abcd abcd". Please try again'
            )
        else:
            config.set('EMAIL', 'APP_PASSWORD', gmail_app_pass)
            config.set('EMAIL', 'ENABLED', 'True')
            _save_config()
            return None


def _create_admin_user():
    if _is_no_users():
        new_admin = Users(username='admin', email='admin@admin.com', hashed_password=bcrypt_context.hash("admin"))
        session.add(new_admin)
        session.commit()
        session.close()


def _inject_sql_file(file_path):
    try:
        with open(file_path, 'r') as file:
            sql_commands = file.read()
            statements = sql_commands.split(';')
            for statement in statements:
                if statement.strip() != "":
                    session.execute(text(statement.strip()))
                    session.commit()
        print(f"{file_path} loaded successfully")
    except Exception as e:
        print(f"Error occurred while executing {file_path}: {e}")
        session.rollback()


def _inject_initial_data():
    for sql_file in ['brands.sql', 'categories.sql']:
        _inject_sql_file(f'sql/{sql_file}')

    components_path = 'sql/components'
    component_files = sorted(os.listdir(components_path))
    for component_file in component_files:
        if component_file.endswith('.sql'):
            _inject_sql_file(os.path.join(components_path, component_file))


def is_initdb():
    initdb_record = session.query(InitDB).first()
    return initdb_record is None


def set_initdb(status: bool):
    initdb_record = session.query(InitDB).filter(InitDB.id == 1).first()

    if initdb_record:
        initdb_record.status = status
    else:
        initdb_record = InitDB(id=1, status=status)
        session.add(initdb_record)

    session.commit()


def docker_config(unattended: bool = True):
    if is_initdb():
        _create_admin_user()
        _inject_initial_data()

    set_initdb(True)
