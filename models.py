from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TasksTerms(Base):
    __tablename__ = 'TaskTerms'
    id = Column(Integer, primary_key=True)
    task_name = Column(String)
    year = Column(Integer)
    month = Column(Integer)
    day = Column(Integer)

    def __repr__(self):
        return f'{self.id, self.task_name, self.year, self.month, self.day}'


class OverdueTasks(Base):
    __tablename__ = 'OverdueTasks'
    id = Column(Integer, primary_key=True)
    task_name = Column(String)

    def __repr__(self):
        return f'{self.task_name}'


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(String)
    old_password = Column(String)

    def __repr__(self):
        return f'{self.email}, {self.password}'
