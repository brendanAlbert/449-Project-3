#
############################## By Jayro Alvarez #######################################
#
import flask
import json
from flask import request, jsonify, g, make_response, render_template 
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = flask.Flask(__name__)
app.config.from_envvar('APP_CONFIG')

#Functions to setup db: 
###########################################################

#called right before any request to establish db connection
#connection saved globally in 'g'
@app.before_request
def connect_to_db():
    g.db = get_db()


#called right after any request to commit changes to db and close db connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.commit()
        db.close()


#establishes connection to db, called in @app.before_request
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.execute('PRAGMA foreign_keys = ON')
        db.row_factory = make_dicts
    return db


#return a dictionary for everything in db
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
        for idx, value in enumerate(row))


#ERROR HANDLERS: 
###########################################################
# What is shown if there is an error
@app.errorhandler(404)
def page_not_found(e):
    return jsonify('HTTP 404 Not Found'), 404


@app.errorhandler(409)
def constraint_violation(e):
    return jsonify('HTTP 409 Conflict'), 409


# Home Page/User Documentation Route
###########################################################
@app.route('/', methods=['GET'])
def home():
    return render_template('user_guide.html')

#
############################## User Related Routes ######################################
#

############################## Create User ######################################
@app.route('/api/v1/resources/musicService/users', methods=['POST'])
def create_user():
    #get request json data
    input = request.get_json()

    #required fields list to check if all input was correctly inputted
    required_fields = ['username', 'password', 'display_name', 'email']
    # if not all required fields inputted 
    if not all([field in input for field in required_fields]):
        return constraint_violation(409)

    #Assigning all inputs to fields
    username = input['username']
    password = input['password']
    display_name = input['display_name']
    email = input['email']
    #initialize optional field to None
    #None turns to NULL when inserted into db
    homepage_url = None

    #check if optional data was sent in, if not, already set to None
    if 'homepage_url' in input:
        homepage_url = input['homepage_url']

    #query to see if username already exists
    query = "SELECT * FROM User WHERE username = \"" + username + "\";"
    result = g.db.execute(query)

    #return first row from query, returns None of nothing found
    found = result.fetchone() 

    #if username already exists
    if found:
        return constraint_violation(409)

    #hash inputted password:
    hashed_pw = generate_password_hash(password)

    #insert user into db after all checks passed
    params = (username, hashed_pw, display_name, email, homepage_url)
    g.db.execute("INSERT INTO User VALUES(?,?,?,?,?)", params)

    #set up location to be returned in response header
    location = 'http://127.0.0.1:5000/api/v1/resources/musicService/users?username=' + username

    #create response
    response = make_response(jsonify('New User Created!'), 201)
    response.headers['Location'] = location
    return response


############################## Get User ######################################
@app.route('/api/v1/resources/musicService/users', methods=['GET'])
def retrieve_profile():
    #get query params from URL
    query_parameters = request.args

    #get username
    username = query_parameters.get('username')

    #check is username is empty
    if username is None:
        return page_not_found(404)

    #setup query
    query = "SELECT * FROM User WHERE username = \"" + username + "\";"

    #run query in db
    result = g.db.execute(query)

    #return first row from query, returns None of nothing found
    found = result.fetchone()

    #If no user is found
    if not found:
        return page_not_found(404)

    #found contains username from db
    #get rid of password prior to returning found
    del found['password']

    #put the user profile in the response, default return is 200
    return make_response(jsonify(found))


############################## Delete User ######################################
@app.route('/api/v1/resources/musicService/users', methods=['DELETE'])
def delete_user():
    #get request json data
    input = request.get_json()

    #if no username is passed in/'username' spelled incorrectly
    if not 'username' in input.keys():
        return constraint_violation(409)

    #save username
    username = input['username']

    #query to see if username already exists
    query = "SELECT username FROM User WHERE username = \"" + username + "\";"
    result = g.db.execute(query)

    #return first row from query, returns None of nothing found
    found = result.fetchone() 

    #user name found, delete from db
    if found:
        #delete user query
        delete_user_query = "DELETE FROM User WHERE username = \"" + username + "\";"
        g.db.execute(delete_user_query)

        #user deleted, return is 200
        response = make_response(jsonify('User deleted'), 200)
        return response

    #if no user found
    return page_not_found(404)


########################## Change User Password ##################################
@app.route('/api/v1/resources/musicService/users/change-password', methods=['PUT'])
def change_password():
    #get request json data
    input = request.get_json()

    #if username or password not inputted
    if not 'username' in input.keys() or not 'newpassword' in input.keys():
        return constraint_violation(409)

    #save username in var
    username = input['username']

    #hash new password
    new_password = generate_password_hash(input['newpassword'])

    #query to see if username already exists
    query = "SELECT username FROM User WHERE username = \"" + username + "\";"
    result = g.db.execute(query)

    #return first row from query, returns None of nothing found
    found = result.fetchone() 

    #user name found, change password
    if found:
        update_query = "UPDATE User SET password = \"" + new_password + "\" WHERE username = \"" + username + "\";"
        g.db.execute(update_query)
        #create response to return, default return is 200
        response = make_response(jsonify(username + '\'s password was changed!'), 200)
        return response

    #if no user found
    return page_not_found(404)


############################## Authenticate User #####################################
@app.route('/api/v1/resources/musicService/users/authenticate-user', methods=['POST'])
def authenticate_user():
    #get request json data
    input = request.get_json()

    #required fields list to check if all input was correctly inputted
    required_fields = ['username', 'password']
    #if not all required fields inputted 
    if not all([field in input for field in required_fields]):
        return page_not_found(404)

    #save input in vars
    username = input['username']
    password = input['password']

    #first see if username is found and return username and password
    query = "SELECT username, password FROM User WHERE username = \"" + username + "\";"
    result = g.db.execute(query)

    #return first row from query, returns None of nothing found
    found = result.fetchone() 

    #If no user is found, return 409
    if not found:
        return page_not_found(404)

    #found contains username and hashed pw from db 
    #check the stored, hashed value in db with passed in parameter
    password_check = check_password_hash(found['password'], password)

    #if check came back true:
    if password_check == True:
        #create response to return, default return is 200
        location = 'http://127.0.0.1:5000/api/v1/resources/musicService/users?username=' + username
        response = make_response(jsonify(username + '\'s username and password are correct.'), 200)
        response.headers['Authenticated'] = True
        response.headers['Location of Authenticated User'] = location
        return response

    return page_not_found(404)

#
############################## END OF User MICROSERVICE CODE ######################################
#
