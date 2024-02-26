"""Log populator module"""
import datetime

from sqlalchemy.orm import sessionmaker

import database
from models import ActionLog

Session = sessionmaker(bind=database.engine)
session = Session()


def add_log(action: str, log: str, user: str):
    log_entry = ActionLog(action=action, user=user, log=log, log_date=datetime.date.today())
    session.add(log_entry)
    session.commit()
    session.close()
