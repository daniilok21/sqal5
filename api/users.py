from flask import jsonify, request
from flask_restful import abort, Resource
from datetime import datetime
from data import db_session
from data.users import User


def if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({
            'user': user.to_dict(only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email'))
        })

    def delete(self, user_id):
        if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, user_id):
        if_user_not_found(user_id)
        args = request.json
        if not args:
            return jsonify({'error': 'Empty request'})

        session = db_session.create_session()
        user = session.query(User).get(user_id)

        if 'surname' in args:
            user.surname = args['surname']
        if 'name' in args:
            user.name = args['name']
        if 'age' in args:
            user.age = args['age']
        if 'position' in args:
            user.position = args['position']
        if 'speciality' in args:
            user.speciality = args['speciality']
        if 'address' in args:
            user.address(args['address'])
        if 'email' in args:
            user.email = args['email']
        if 'password' in args:
            user.set_password(args['password'])

        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({
            'users': [user.to_dict(only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email'))
                      for user in users]
        })

    def post(self):
        args = request.json
        if not args or not all(key in args for key in ['surname', 'name', 'age', 'position', 'speciality', 'address', 'email', 'password']):
            return jsonify({'error': 'Bad request'})

        session = db_session.create_session()
        if session.query(User).filter(User.email == args['email']).first():
            return jsonify({'error': 'Email already exists'})

        user = User(
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            position=args['position'],
            speciality=args['speciality'],
            address=args['address'],
            email=args['email'],
            modified_date=datetime.now()
        )

        user.set_password(args['password'])

        session.add(user)
        session.commit()
        return jsonify({'success': 'OK', 'id': user.id})