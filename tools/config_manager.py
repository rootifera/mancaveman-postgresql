"""Config Generator module"""
import ipaddress
import logging
import os
import re
import secrets
import shutil
import socket
import sys
from datetime import datetime

import validators
from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

import database
from definitions import CONFIG_PATH, DESC_SKIP
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


def health_check_keygen():
    hc_key = secrets.token_hex(16)
    config.set('HEALTH', 'KEY', hc_key)
    _save_config()


def get_health_check_key():
    return config.get('HEALTH', 'KEY')


def get_email_credentials():
    enabled = config.get('EMAIL', 'ENABLED')
    username = config.get('EMAIL', 'USERNAME')
    password = config.get('EMAIL', 'APP_PASSWORD')
    if enabled == 'False':
        return False
    else:
        return username, password


def get_domain_name():
    return config.get('SERVER', 'DOMAIN')


def _backup_config(conf_file: str = CONFIG_PATH):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    shutil.copy(conf_file, 'backups/config.bak-{}'.format(timestamp))


def _is_ip_valid(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def _is_port_valid(user_port: str) -> bool:
    if not user_port.isdigit():
        return False

    user_port = int(user_port)

    if 1024 <= user_port <= 49151:
        return True
    elif user_port < 1024:
        print("INFO: Port {} would only work if you start the application with sudo or as root".format(user_port))
        print("INFO: Ideally please select a port between 1024 and 49151")
        print("INFO: You can change the value in the config.ini and restart the application")
        return True
    else:
        return False


def _is_domain_valid(domain: str) -> bool:
    return validators.domain(domain)


def _is_port_in_use(host_ip: str, port: str) -> bool:
    if not _is_port_valid(port):
        return True
    else:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((host_ip, int(port))) == 0


def _is_no_users():
    userlist = session.query(Users.username).all()
    if len(userlist) == 0:
        return True
    return False


def _secret_keygen(unattended: bool = False):
    if config.get('CREDENTIALS', 'SECRET_KEY') != '':
        print('WARNING: Secret Key FOUND in config.ini. Creatting backup')
        _backup_config()

    if unattended:
        config.set('CREDENTIALS', 'SECRET_KEY', secrets.token_hex(48))
        _save_config()
        return None

    while True:
        selection = input(
            'Would you like to autogenerate and set the secret key? (y/n) or (q) to Quit: ').strip()
        if selection.lower() in ['y', 'yes']:
            key = secrets.token_hex(48)
            config.set('CREDENTIALS', 'SECRET_KEY', key)
            print('Your key is: {}'.format(key))
            break
        elif selection.lower() in ['n', 'no']:
            key = ''
            while len(key) < 8:
                key = input('Please enter your secret key (min 8 characters): ').strip()
            config.set('CREDENTIALS', 'SECRET_KEY', key)
            print('Your key is: {}'.format(key))
            break
        elif selection.lower() in ['q', 'quit']:
            print('Quitting...')
            sys.exit()
        else:
            print('ERROR: Invalid option please try again')

    _save_config()


def _algorithm_selection(unattended: bool = False):
    if unattended:
        config.set('CREDENTIALS', 'ALGORITHM', 'HS256')
        _save_config()
        return None

    print("Please select a JSON Web Signature algorithm")
    print("0: HS256 (default)\n"
          "1: HS384\n"
          "2: HS512")
    user_alg = input('Selection (Press enter for default): ').strip()

    match user_alg:
        case "0":
            config.set('CREDENTIALS', 'ALGORITHM', 'HS256')
            print("Signature set to HS256")
        case "1":
            config.set('CREDENTIALS', 'ALGORITHM', 'HS384')
            print("Signature set to HS384")
        case "2":
            config.set('CREDENTIALS', 'ALGORITHM', 'HS512')
            print("Signature set to HS512")
        case _:
            print(DESC_SKIP)
            config.set('CREDENTIALS', 'ALGORITHM', 'HS256')

    _save_config()


def _ip_selection(unattended: bool = False):
    if unattended:
        config.set('SERVER', 'IP', '0.0.0.0')
        _save_config()
        return None

    while True:
        user_ip = input(
            'Please enter host listen IP (press enter for default: 0.0.0.0): ').strip()
        if user_ip == '':
            config.set('SERVER', 'IP', '0.0.0.0')
            print(DESC_SKIP)
            _save_config()
            break
        elif not _is_ip_valid(user_ip):
            print("ERROR: Invalid IP, please try again.")
        else:
            config.set('SERVER', 'IP', user_ip)
            _save_config()
            break


def _port_selection(unattended: bool = False):
    listen_ip = config.get('SERVER', 'IP')
    if unattended:
        """config.ini is shipped with 0.0.0.0 but please call _ip_selection() 
        before _port_selection() in first_run() so it tests the right IP"""
        set_port = "8080"
        if _is_port_in_use(listen_ip, set_port):
            set_port = int(set_port)
            while _is_port_in_use(listen_ip, str(set_port)):
                set_port += 1
            config.set('SERVER', 'PORT', str(set_port))
            _save_config()
        return None

    while True:
        user_port = input(
            'Please enter the port (press enter for default: 8080): ').strip()
        if user_port == '' and not _is_port_in_use(listen_ip, "8080"):
            config.set('SERVER', 'PORT', '8080')
            print(DESC_SKIP)
            _save_config()
            return None

        if user_port != '':
            while _is_port_in_use(listen_ip, user_port):
                new_port = input(
                    "ERROR: Invalid port or the port is already in use. Please enter a different port: ").strip()
                user_port = new_port
            config.set('SERVER', 'PORT', user_port)
            _save_config()
            return None


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


def _set_redis_url(unattended: bool = False, docker_autoconfig: bool = False):
    if unattended:
        config.set('DB', 'REDIS', 'redis://localhost')  # standalone  default
    elif docker_autoconfig:
        config.set('DB', 'REDIS', 'redis://redis')  # docker compose default
    else:
        redis_url = input('Please enter your redis hostname (Hit enter for localhost): ').strip()
        if not redis_url:
            config.set('DB', 'REDIS', 'redis://localhost')
        else:
            config.set('DB', 'REDIS', 'redis://' + redis_url)

    _save_config()


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


def docker_build_config(unattended: bool = True):
    if is_initdb():
        _algorithm_selection(unattended)
        _domain_selection(unattended)
        _set_redis_url(docker_autoconfig=True)


def docker_config(unattended: bool = True):
    if is_initdb():
        _secret_keygen(unattended)
        _algorithm_selection(unattended)
        _domain_selection(unattended)
        _create_admin_user()
        _inject_initial_data()
        _set_redis_url(docker_autoconfig=True)
        health_check_keygen()

    set_initdb(True)
