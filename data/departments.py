from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase


class Department(SqlAlchemyBase):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    chief_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    members = Column(String(500), nullable=False)
    email = Column(String(100), nullable=True)
    who_created = Column(Integer, nullable=False)

    chief = relationship('User', backref='departments_led')