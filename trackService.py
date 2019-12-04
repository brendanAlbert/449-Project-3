# Music Microservices APIs
# Ian Michael Jesu Alvarez
# Brendan Albert
# CPSC 449- Backend Engineering

import flask
import json
import uuid
from flask import request, jsonify, g, make_response, render_template
import sqlite3

app = flask.Flask(__name__)
app.config.from_envvar('APP_CONFIG')

track_shard_db_names = ['TRACKS_SHARD1','TRACKS_SHARD2','TRACKS_SHARD3']
db_context_names = ['_trackshard1', '_trackshard2', '_trackshard3', '_database']

sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))

#called right before any request to establish db connection
#connection saved globally in 'g'
@app.before_request
def connect_to_db():
    g._trackshard1 = get_db(track_shard_db_names[0])
    g._trackshard2 = get_db(track_shard_db_names[1])
    g._trackshard3 = get_db(track_shard_db_names[2])
    g.db = get_db('users_playlists_descriptions')

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))


def get_db(db_name):
    if db_name == track_shard_db_names[0]:
        db = getattr(g, db_context_names[0], None)
        if db is None:
            db = g._trackshard1 = sqlite3.connect(app.config[db_name], detect_types=sqlite3.PARSE_DECLTYPES)
            db.row_factory = make_dicts
    elif db_name == track_shard_db_names[1]:
        db = getattr(g, db_context_names[1], None)
        if db is None:
            db = g._trackshard2 = sqlite3.connect(app.config[db_name], detect_types=sqlite3.PARSE_DECLTYPES)
            db.row_factory = make_dicts
    elif db_name == track_shard_db_names[2]:
        db = getattr(g, db_context_names[2], None)
        if db is None:
            db = g._trackshard3 = sqlite3.connect(app.config[db_name], detect_types=sqlite3.PARSE_DECLTYPES)
            db.row_factory = make_dicts
    elif db_name == 'users_playlists_descriptions':
        db = getattr(g, db_context_names[3], None)
        if db is None:
            db = g._database = sqlite3.connect(app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
            db.execute('PRAGMA foreign_keys = ON')
            db.row_factory = make_dicts
    return db


@app.teardown_appcontext
def close_connection(exception):
    for dbname in db_context_names:
        db = getattr(g, dbname, None)
        if db is not None:
            db.close()


@app.errorhandler(404)
def page_not_found(e):
    return jsonify('HTTP 404 Not Found'), 404


@app.errorhandler(409)
def constraint_violation(e):
    return jsonify('HTTP 409 Conflict'), 409




# Just some welcome page
@app.route('/', methods=['GET'])
def home():
    return render_template('user_guide.html')

#
############################## TRACKS MICROSERVICE CODE ########################################
#

# Gets all the tracks from the Track Table and turns it into json
@app.route('/api/v1/resources/musicService/tracks/all', methods=['GET'])
def track_all():

    query = "SELECT * FROM Track"
    result = g._trackshard1.execute(query)
    found = result.fetchall()

    result = g._trackshard2.execute(query)
    found += result.fetchall()

    result = g._trackshard3.execute(query)
    found += result.fetchall()

    return make_response(jsonify(found))

# This retrieves a track. This filters the Track table depending on the query
@app.route('/api/v1/resources/musicService/tracks', methods=['GET'])
def api_filter():
    query_parameters = request.args

    track_title = query_parameters.get('track_title')
    track_id = query_parameters.get('track_id')
    found1 = None
    found2 = None
    found3 = None


    if track_title is None and track_id is None:
        return page_not_found(404)

    elif track_title is not None:

        query = """SELECT * FROM Track WHERE track_title = ?;"""
        shard1_result = g._trackshard1.execute(query, (track_title,))
        found1 = shard1_result.fetchone()

        shard2_result = g._trackshard2.execute(query, (track_title,))
        found2 = shard2_result.fetchone()

        shard3_result = g._trackshard3.execute(query, (track_title,))
        found3 = shard3_result.fetchone()
    
    elif track_id is not None:
        
        #convert the track_id from string to UUID object
        track_id = uuid.UUID(track_id)
        query = """SELECT * FROM Track WHERE track_id = ?;"""

        # convert the track_id object to an int so we can perform modulus for shard key
        shard_key = track_id.int % 3

        if shard_key == 0:
            shard1_result = g._trackshard1.execute(query, (track_id.bytes_le,))
            found1 = shard1_result.fetchone()

        elif shard_key == 1:
            shard2_result = g._trackshard2.execute(query, (track_id.bytes_le,))
            found2 = shard2_result.fetchone()

        elif shard_key == 2:
            shard3_result = g._trackshard3.execute(query, (track_id.bytes_le,))
            found3 = shard3_result.fetchone()

    # we will need to check all 3 database shards
    # shard1_result = g._trackshard1.execute(query, track_title)
    # found1 = shard1_result.fetchone()

    # shard2_result = g._trackshard2.execute(query, track_title)
    # found2 = shard2_result.fetchone()

    # shard3_result = g._trackshard3.execute(query, track_title)
    # found3 = shard3_result.fetchone()

    if not found1 and not found2 and not found3:
        return page_not_found(404)

    found = None

    if found1:
        found = found1
    elif found2:
        found = found2
    elif found3:
        found = found3

    return make_response(jsonify(found))

# This allows the user to create a track and POST it to the database
@app.route('/api/v1/resources/musicService/tracks', methods=['POST'])
def create_track():
    #takes in request (sent in with curl as JSON data)
    # and turn it into python dict. with 'get_json()' function
    input = request.get_json()

    required_fields = ['track_title', 'album_title', 'artist', 'length_seconds', 'url_media']

    if not all([field in input for field in required_fields]):
        return constraint_violation(409)

    track_title = input['track_title']
    album_title = input['album_title']
    artist = input['artist']
    length_seconds = input['length_seconds']
    url_media = input['url_media']
    url_art = None

    #check if optional data was sent in, if not, already set to None
    if 'url_art' in input:
        url_art = input['url_art']

    result = g._trackshard1.execute("""SELECT * FROM Track WHERE track_title = ? and artist = ?;""", (track_title,artist,))
    found = result.fetchone()

    result = g._trackshard2.execute("""SELECT * FROM Track WHERE track_title = ? and artist = ?;""", (track_title,artist,))
    found2 = result.fetchone()

    result = g._trackshard3.execute("""SELECT * FROM Track WHERE track_title = ? and artist = ?;""", (track_title,artist,))
    found3 = result.fetchone()

    if found or found2 or found3:
        return constraint_violation(409)


    track_id = uuid.uuid4()
    # first_char_of_track_id = ord(track_id[0])
    shard = track_id.int % 3
    file = open('textfile.txt', 'a')
    file.write('shard # [')
    file.write(str(shard))
    file.write(']\n')
    file.close()

    params = (track_id.bytes_le, track_title, album_title, artist, length_seconds, url_media, url_art)

    try:

        if shard == 0:
            g._trackshard1.execute("INSERT INTO Track VALUES(?, ?, ?, ?, ?, ?, ?)", params)
            g._trackshard1.commit()
            
        elif shard == 1:
            g._trackshard2.execute("INSERT INTO Track VALUES(?, ?, ?, ?, ?, ?, ?)", params)
            g._trackshard2.commit()
            
        elif shard == 2:
            g._trackshard3.execute("INSERT INTO Track VALUES(?, ?, ?, ?, ?, ?, ?)", params)
            g._trackshard3.commit()

    except:
        file = open('errorlog.txt', 'a')
        file.write('something went wrong while adding track' + '\n')
        file.close()

    location = 'http://127.0.0.1:5001/api/v1/resources/musicService/tracks?track_title='+track_title
    #create response to return
    response = make_response(jsonify('New Track Created!'), 201)
    response.headers['Location'] = location
    return response

@app.route('/api/v1/resources/musicService/tracks', methods=['DELETE'])
def delete_track():
    input = request.get_json()

    if not 'track_title' in input.keys() or not 'artist' in input.keys():
        return constraint_violation(409)

    track_title = input['track_title']
    artist = input ['artist']


    # Get track_id where the track_title = to the track_title in the input
    query_for_track_id = "SELECT track_id FROM Track WHERE track_title = \"" + track_title + "\" AND artist = \"" + artist+  "\";"
    result1 = g._trackshard1.execute(query_for_track_id)
    found1 = result1.fetchone() # this now holds the track_id to be checked on the Tracks_List table
    
    result2 = g._trackshard2.execute(query_for_track_id)
    found2 = result2.fetchone() # this now holds the track_id to be checked on the Tracks_List table

    result3 = g._trackshard3.execute(query_for_track_id)
    found3 = result3.fetchone() # this now holds the track_id to be checked on the Tracks_List table

    if not found1 and not found2 and not found3:
        return page_not_found(404)

    found = None

    if found1:
        found = found1
    elif found2:
        found = found2
    elif found3:
        found = found3

    # search if the track_id of this track_title exist in Track_List if it does delete the rows that has this track_id first Track_List table THEN delete the track from the Track table

    file = open('deleted.txt', 'a')
    file.write("str(found['track_id'])")
    file.write(str(found['track_id']))
    file.write("\n")
    file.close()
    # query_for_TrackList = "SELECT track_id FROM Tracks_List WHERE track_id = " + str(found['track_id']) + ";"
    result = g.db.execute("""SELECT track_id FROM Tracks_List WHERE track_id = ?;""", ( str(found['track_id']), ) )
    found_inTrackList = result.fetchone()

    # Delete the rows that has this track_id from Tracks_List
    if found_inTrackList:
        g.db.execute("""DELETE FROM Tracks_List WHERE track_id = ?;""" , (str(found['track_id']),))
        # delete_from_TrackList = "DELETE FROM Tracks_List WHERE track_id= " + str(found['track_id']) +  ";"


    # Delete row from Description table
    # query_for_Description = "SELECT track_id FROM Description WHERE track_id = " + str(found['track_id']) +  ";"
    # result = g.db.execute(query_for_Description)
    # found_inDescription = result.fetchone()

    # if found_inDescription:
    #     delete_from_Description = "DELETE FROM Description WHERE track_id= " + str(found['track_id']) +  ";"
    #     g.db.execute(delete_from_Description)


    # delete_user_query = "DELETE FROM Track WHERE track_title= \"" + track_title + "\" AND artist = \"" + artist+  "\";"
    #setting up response data

    # we need to know which Tracks db shard to delete from
    # first_char_of_track_id = ord(track_id[0])
    # shard = first_char_of_track_id % 3
    if found1:
        g._trackshard1.execute("""DELETE FROM Track WHERE track_title = ? AND artist = ? ;""", ( track_title , artist,))
        g._trackshard1.commit()
        file = open('deleted.txt', 'a')
        file.write('deleted from shard 1')
        file.close()
    elif found2:
        # g._trackshard2.execute(delete_user_query)
        g._trackshard2.execute("""DELETE FROM Track WHERE track_title = ? AND artist = ? ;""", ( track_title , artist,))
        g._trackshard2.commit()
        file = open('deleted.txt', 'a')
        file.write('deleted from shard 2')
        file.close()
    elif found3:
        # g._trackshard3.execute(delete_user_query)
        g._trackshard3.execute("""DELETE FROM Track WHERE track_title = ? AND artist = ? ;""", ( track_title , artist,))
        g._trackshard3.commit()
        file = open('deleted.txt', 'a')
        file.write('deleted from shard 3')
        file.close()



    #create response to return
    response = make_response(jsonify('Track deleted'), 200)
    return response

@app.route('/api/v1/resources/musicService/tracks/edit-track', methods=['PUT'])
def edit_track():

    input = request.get_json()

    if not 'track_title' in input.keys() or not 'artist' or not 'newTrackTitle' or not 'newAlbumTitle' or not 'newArtist' or not 'newLength' or not 'newUrlMedia' or not 'newUrlArt' in input.keys():
        return constraint_violation(409)

    track_title_toUpdate = input['track_title']
    artist_toUpdate = input['artist']
    newTrackTitle = input['newTrackTitle']
    newAlbumTitle = input['newAlbumTitle']
    newArtist = input['newArtist']
    newLength = input['newLength']
    newUrlMedia = input['newUrlMedia']
    newUrlArt = input['newUrlArt']

    # we will need to check all 3 database shards
    shard1_result = g._trackshard1.execute("""SELECT track_id FROM Track WHERE track_title = ? AND artist = ?;""", (track_title_toUpdate, artist_toUpdate,))
    found1 = shard1_result.fetchone()

    shard2_result = g._trackshard2.execute("""SELECT track_id FROM Track WHERE track_title = ? AND artist = ?;""", (track_title_toUpdate, artist_toUpdate,))
    found2 = shard2_result.fetchone()

    shard3_result = g._trackshard3.execute("""SELECT track_id FROM Track WHERE track_title = ? AND artist = ?;""", (track_title_toUpdate, artist_toUpdate,))
    found3 = shard3_result.fetchone()

    if not found1 and not found2 and not found3:
        return page_not_found(404)

    if found1:
        file = open('textfile.txt', 'a')
        file.write('updating track in shard 1, id = ' + str(found1))
        file.close()
        g._trackshard1.execute("""UPDATE Track SET track_title = ?, 
        album_title = ?, artist = ?, length_seconds = ?, url_media = ?, url_art = ? 
        WHERE track_title = ? AND artist = ?;""", (newTrackTitle,newAlbumTitle,newArtist,newLength,newUrlMedia,newUrlArt,track_title_toUpdate,artist_toUpdate ))
        g._trackshard1.commit()
    elif found2:
        file = open('textfile.txt', 'a')
        file.write('updating track in shard 2, id = ' + str(found2))
        file.close()
        g._trackshard2.execute("""UPDATE Track SET track_title = ?, 
        album_title = ?, artist = ?, length_seconds = ?, url_media = ?, url_art = ? 
        WHERE track_title = ? AND artist = ?;""", (newTrackTitle,newAlbumTitle,newArtist,newLength,newUrlMedia,newUrlArt,track_title_toUpdate,artist_toUpdate ))
        g._trackshard2.commit()
    elif found3:
        file = open('textfile.txt', 'a')
        file.write('updating track in shard 3, id = ' + str(found3))
        file.close()
        g._trackshard3.execute("""UPDATE Track SET track_title = ?, 
        album_title = ?, artist = ?, length_seconds = ?, url_media = ?, url_art = ? 
        WHERE track_title = ? AND artist = ?;""", (newTrackTitle,newAlbumTitle,newArtist,newLength,newUrlMedia,newUrlArt,track_title_toUpdate,artist_toUpdate ))
        g._trackshard3.commit()

    
    return make_response(jsonify(track_title_toUpdate + '\'s information was changed!'))