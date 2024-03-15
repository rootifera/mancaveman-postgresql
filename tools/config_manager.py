"""Config Generator module"""
import logging
import os

from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

import database
from models import Users, InitDB

Session = sessionmaker(bind=database.engine)
session = Session()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
logging.getLogger('passlib').setLevel(logging.ERROR)


def _is_no_users():
    userlist = session.query(Users.username).all()
    if len(userlist) == 0:
        return True
    return False


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
    for sql_file in ['brands.sql']:
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


def first_start_config():
    if is_initdb():
        _create_admin_user()
        _inject_initial_data()
        set_initdb(True)
        return True
