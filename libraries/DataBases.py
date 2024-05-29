from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, mapper
from models import Base, TasksTerms
from sqlalchemy.sql import exists
from main import Session, engine


class Methods:

    def add(self, task_name, base_name, year=0, month=0, day=0):

        with Session() as session:
            if year != 0:
                data_base = base_name(
                    task_name=task_name,
                    year=year,
                    month=month,
                    day=day
                )
            else:
                data_base = base_name(
                    task_name=task_name
                )
            session.add(data_base)
            session.commit()

    @staticmethod
    def add_user(base_name, email, password, old_password):
        with Session() as session:
            data_base = base_name(
                email=email,
                password=password,
                old_password=old_password
            )
            session.add(data_base)
            session.commit()


    def is_element_exists(self, base_name, task_name):

        with Session() as session:
            data_base = session.query(exists().where(base_name.task_name == task_name)).scalar()

        return data_base

    @staticmethod
    def is_user_exists(base_name, email, password):
        with Session() as session:
            email_check = session.query(exists().where(base_name.email == email)).scalar()
            password_check = session.query(exists().where(base_name.password == password)).scalar()
        return email_check and password_check

    @staticmethod
    def get_date(base_name, task_name):

        with Session() as session:
            date = list()
            database = session.query(base_name).filter_by(task_name=task_name).first()
            date.append(database)
        return database

    def remove_element(self, base_name, task_name):
        with Session() as session:
            database = session.query(base_name).filter_by(task_name=task_name).delete()
            session.commit()

