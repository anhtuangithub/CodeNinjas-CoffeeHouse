import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
@app.route('/drinks', methods=['GET'])
def get_drinks():
    lstDrink = Drink.query.all()
    
    if (len(lstDrink) == 0):
        abort(404)
    lstDrink = [i.short() for i in lstDrink]

    return jsonify({
        'success': True,
        'drinks': lstDrink
    })

@app.route('/drinks-detail',methods = ['GET'])
@requires_auth('get:drinks-detail')
def get_drink_detail(token):
    lstDrink = Drink.query.all()
    if lstDrink:
        lstDrink = [i.long() for i in lstDrink]
        return jsonify({
            'success': True,
            'drinks': lstDrink
        })

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(token):
    body = request.get_json()
    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)
    if isinstance(new_recipe, dict):
        new_recipe = [new_recipe]
    new_recipe = json.dumps(new_recipe)
    try:
        drink = Drink(title=new_title, recipe=new_recipe)
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': drink.long()
        })

    except Exception:
        abort(422)

@app.route('/drinks/<int:drinkId>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink_by_id(token, drinkId):
    body = request.get_json()
    try:
        drinkModify = Drink.query.filter(
            Drink.id == drinkId).one_or_none()

        if (drinkModify is None):
            abort(404)
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)
        if new_title:
            drinkModify.title = new_title
        if new_recipe:
            if isinstance(new_recipe, dict):
                new_recipe = [new_recipe]
            new_recipe = json.dumps(new_recipe)
            drinkModify.recipe = new_recipe
        
        drinkModify.update()
        return jsonify({
            'success': True,
            'drinks': drinkModify.long()
        })

    except BaseException:
        abort(400)

@app.route('/drinks/<int:drinkId>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink_by_id(token, drinkId):
    drink = Drink.query.filter(Drink.id == drinkId).one_or_none()
    if (drink is None):
        abort(404)

    try:
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink.id
        })

    except Exception:
        abort(422)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def resource_not_found_error_handler(error):
    return jsonify({
        'success': False,
        'message': 'resource not found'
    }), 404

@app.errorhandler(404)
def resource_not_found_error_handler(error):
    return jsonify({
        'success': False,
        'message': 'Auth error'
    }), 401