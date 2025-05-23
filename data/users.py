from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from werkzeug.security import generate_password_hash, check_password_hash
from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    surname = Column(String, nullable=False)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    position = Column(String, nullable=False)
    speciality = Column(String, nullable=False)
    address = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    modified_date = Column(DateTime)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def to_dict(self, only=()):
        fields = {
            'id': self.id,
            'surname': self.surname,
            'name': self.name,
            'age': self.age,
            'position': self.position,
            'speciality': self.speciality,
            'address': self.address,
            'email': self.email,
            'modified_date': self.modified_date.isoformat() if self.modified_date else ''
        }
        if only:
            return {key: fields[key] for key in only}
        return fields