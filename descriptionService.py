#
############################## By Jayro Alvarez #######################################
#
import flask
import json
from flask import request, jsonify, g, make_response, render_template 
import sqlite3

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
############################## Description Related Routes ######################################
#

############################## Post Description ####################################
@app.route('/api/v1/resources/musicService/descriptions', methods=['POST'])
def set_user_description():
    #get request json data
    input = request.get_json()

    #required fields list to check if all input was correctly inputted
    required_fields = ['username', 'track_id', 'description_text']
    # if not all required fields inputted 
    if not all([field in input for field in required_fields]):
        return constraint_violation(409)

    #Assigning all inputs to fields
    username = input['username']
    track_id = input['track_id']
    description_text = input['description_text']

    with open('description_log.txt', 'a') as f:
        f.write('username = ' + username + '\n')
        f.write('track_id = ' + track_id + '\n')
        f.write('description_text = ' + description_text + '\n')
    
    params = (username, track_id, description_text)

    #be ready to catch foreign key constraint
    try: 
        g.db.execute("INSERT INTO Description VALUES(?,?,?)", params)
        g.db.commit()
        with open('description_log.txt', 'a') as f:
            f.write('inserted into description with great success\n')
    except:
        with open('description_log.txt', 'a') as f:
            f.write('FAILED TO insert into description\n')
        return constraint_violation(409)

    #set up location to be returned in response header
    location = 'http://127.0.0.1:5002/api/v1/resources/musicService/descriptions?username=' + username + '&track_id=' + str(track_id)

    #create response
    response = make_response(jsonify('New Description Created!'), 201)
    response.headers['Location'] = location
    return response


############################## Get Description ####################################
@app.route('/api/v1/resources/musicService/descriptions', methods=['GET'])
def get_user_description():
    #get query params from URL
    query_parameters = request.args

    #get username
    username = query_parameters.get('username')
    track_id = query_parameters.get('track_id')

    #check is username is empty
    if username is None or track_id is None:
        return page_not_found(404)

    #run query in db
    params = (username, track_id)
    result = g.db.execute("SELECT * FROM Description WHERE username = ? AND track_id = ?", params)

    #return first row from query, returns None of nothing found
    found = result.fetchone()

    #If no *description* is found
    if not found:
        return page_not_found(404)

    #get song referred to
    # params = (track_id)
    # song = g.db.execute("SELECT * FROM Track WHERE track_id = ?", params).fetchone()

    #add song to found 
    # found['song'] = song

    #put the *description* in the response, default return is 200
    return make_response(jsonify(found))

#
############################## END OF DESCRIPTION MICROSERVICE CODE ######################################
#
