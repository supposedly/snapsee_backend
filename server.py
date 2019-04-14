from pathlib import Path

import sqlalchemy
from sqlalchemy.sql.functions import coalesce
from flask import request, send_from_directory
from flask.json import jsonify

import faces
from app import app
from database import db, User


def _coalesce_all_columns(model):
    return {
      colname: coalesce(get(colname), getattr(model, colname))
      for colname in model.__table__.columns._data
    }


def _get_all(model):
    return {colname: get(colname) for colname in model.__table__.columns._data if get(colname) is not None}


def get(key):
    if key in request.files:
        return request.files.get(key).read()
    values = request.get_json() if request.is_json else request.values
    return values.get(key)


@app.route('/')
def hello_world():
    return 'hello world', 200


@app.route('/user/add', methods=['POST'])
def add_user():
    print(request, request.form)
    if not get('username'):
        return 'Must provide username', 400
    print('username supplied')
    try:
        db.session.add(**_get_all(User))
    except sqlalchemy.exc.IntegrityError as e:
        db.session.rollback()
        print('fug')
        return str(e), 400  # XXX: 409?
    db.session.commit()
    return '', 204


@app.route('/user/update', methods=['POST'])
def edit_user():
    if not get('username'):
        return 'Must provide username', 400
    try:
        User.query.filter_by(
          username=get('username')
        ).update(**_coalesce_all_columns(User))
    except sqlalchemy.exc.IntegrityError as e:
        db.session.rollback()
        return str(e), 400
    db.session.commit()
    return '', 204


@app.route('/user/get/', methods=['GET'])
def user_get():
    try:
        results = User.query.filter_by(
          **_get_all(User)
        ).all()
    except Exception as e:
        return str(e), 400
    return jsonify([i.to_dict() for i in results]), 200


@app.route('/user/get/<colname>', methods=['GET'])
def user_get_column(colname):
    try:
        results = [{colname: getattr(i, colname)} for i in User.query.filter_by(**_get_all(User)).all()]
    except Exception as e:
        return str(e), 400
    return jsonify(results), 200


@app.route('/image/match', methods=['POST'])
def match_image():
    return 'Not available', 404
    match_found = faces.match(get('image'))
