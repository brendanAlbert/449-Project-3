# Music Microservices APIs
# Ian Michael Jesu Alvarez
# CPSC 449- Backend Engineering

import xspf
import flask
from flask import request, jsonify, g, make_response, render_template, Response, send_file
import os
import sqlite3
import requests
import json
import uuid

# Create XSPF Playlist
# this will hold the xspf playlist
x = xspf.Xspf()


app = flask.Flask(__name__)
app.config.from_envvar('APP_CONFIG')

sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))

#called right before any request to establish db connection
#connection saved globally in 'g'
@app.before_request
def connect_to_db():
    g.db = get_db()


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
        db.execute('PRAGMA foreign_keys = ON')
        db.row_factory = sqlite3.Row
        #db.row_factory = make_dicts
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.commit()
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


@app.route('/api/v2/resources/musicService/spiff.xspf', methods=['GET'])
def create_spiff():
    query_parameters = request.args
    playlist_id = query_parameters.get('playlist_id')


    if playlist_id is None:
        return page_not_found(404)

    #payload = {'playlist_id':playlist_id}

    # GET INFO OF PLAYLIST INTO THE XSPF PLAYLIST
    # This will hold the json containing playlist_id, playlist_title, description, username_id
    #playlist = requests.get("http://localhost:8000/playlists?playlist_id=", params=payload)
    playlist = requests.get("http://localhost:8000/playlists?playlist_id=" + playlist_id)
    #playlist.json()
    #fetched_playlist_data = json.loads(playlist.json())

    #fetched_playlist_data = playlist.json()

    # Set the xspf playlist params with data from requests
    x.title = playlist.json()[0]['playlist_title']
    x.annotation = playlist.json()[0]['description']
    x.creator = playlist.json()[0]['username_id']
    x.identifier = str(playlist.json()[0]['playlist_id'])
    # x.title = fetched_playlist_data.playlist_title
    # x.annotation = fetched_playlist_data.description
    # x.creator = fetched_playlist_data.username_id

    #x.identifier = fetched_playlist_data['playlist_id']
    # x.title = fetched_playlist_data.playlist_title
    # x.annotation = fetched_playlist_data.description
    # x.creator = fetched_playlist_data.username_id
    # x.identifier = playlist["playlist_id"]
    # x.title = playlist["playlist_title"]
    # x.annotation = playlist["description"]
    # x.creator = playlist["username_id"]
    #
    # ADD TRACKS TO THE PLAYLIST
    # Look for track_ids that has the same playlist_id from the query
    query = "SELECT track_id FROM Tracks_List WHERE"
    to_filter = []

    if playlist_id:
        query += ' playlist_id=? AND'
        to_filter.append(playlist_id)

    if playlist_id is None:
        return page_not_found(404)

    # This holds the sql command to query for all of the track_ids in the Tracks_List
    query = query[:-4] + ';'

    # results now has all of the track_ids(songs) in this playlist
    #results = query_db(query, to_filter)

    response = query_db(query, to_filter)
    with open('debugging.txt', 'a') as f:
        f.write('\nresponse:\n')
        f.write(str(response))

    # Put all of these tracks in the xspf playlist
    for tracks in query_db(query, to_filter):
        # query the tracks service for the info of the track which returns a json
        trackidizzle = tracks['track_id']
        # trackidizzle = uuid.UUID(tracks['track_id'])
        with open('debugging.txt', 'a') as f:
            f.write('\ntrackidizzle:\n')
            f.write(str(trackidizzle))
        track_fetched = requests.get("http://localhost:8000/tracks?track_id=" + str(trackidizzle)).json()

        with open('debugging.txt', 'a') as f:
            f.write('tracks:\n')
            f.write(str(tracks))
            f.write('\ntracks_fetched:\n')
            f.write(str(track_fetched))
            f.write('\n')
        # Create a new track object
        track = xspf.Track()
        track.identifier = str(trackidizzle)
        track.title = str(track_fetched['track_title'])
        track.album = str(track_fetched['album_title'])
        track.creator = str(track_fetched['artist'])
        track.duration = str(track_fetched['length_seconds'])
        track.location = str(track_fetched['url_media'])
        track.image = str(track_fetched['url_art'])
        x.add_track(track)


        # track.identifier = track_fetched.track_id
        # track.title = track_fetched.track_title
        # track.album = track_fetched.album_title
        # track.creator = track_fetched.artist
        # track.duration = track_fetched.length_seconds
        # track.link = track_fetched.url_media
        # track.image = track_fetched.url_art
    # query = "SELECT track_id FROM Tracks_List WHERE playlist_id=" + playlist_id
    # result = g.db.execute(query)
    # found = result.fetchall()
    #
    # for track in found:
    #     track_fetched = requests.get("http://localhost:8000/tracks?track_id=" + track[0])
    #     track.identifier = track_fetched.track_id
    #     track.title = track_fetched.track_title
    #     track.album = track_fetched.album_title
    #     track.creator = track_fetched.artist
    #     track.duration = track_fetched.length_seconds
    #     track.location = track_fetched.url_media
    #     track.image = track_fetched.url_art
        # track.identifier = track_fetched["track_id"]
        # track.title = track_fetched["track_title"]
        # track.album = track_fetched["album_title"]
        # track.creator = track_fetched["artist"]
        # track.duration = track_fetched["length_seconds"]
        # track.location = track_fetched["url_media"]
        # track.image = track_fetched["url_art"]

    # This is if you want to do both
    # with open('myPlaylist.xspf', 'a') as f:
    #     f.write(str(x.toXml()))



    #return make_response(jsonify(playlist.json()))
    #return make_response(playlist.tostring())
    #return make_response(jsonify(playlist))
    #return make_response(x.toXml(pretty_print=true))


    # This is when you just want to display the xml spiff file on the browser
    #return make_response(jsonify(x.toXml()))

    # This is when you want an xspf(html) file downloaded
    return Response(x.toXml(), mimetype='application/xspf+xml')



    # results now has all of the track_ids(songs) in this playlist
    #results = query_db(query, to_filter)

    # # This will hold the track_id from the Tracks_List table which will be then queried on the tracks Table
    # track_ids = []
    #
    # # This will hold the tracks on this playlist which will then be converted to a xspf playlist
    # tracks_in_list = []

    # users = requests.get(http://127.0.0.1:8000/users)
    # descriptions = requests.get(http://127.0.0.1:8000/descriptions)
    # media = requests.get(http://127.0.0.1:8000/media)





    # Query Tracks_List table for the track_ids with that corresponding playlist_id
    #playlist = requests.get("http://127.0.0.1:8000/playlists?playlist_id=" + playlist_id)



    # query = "SELECT * FROM Playlist WHERE playlist_id = \"" + playlist_id + "\";"
    # result = g.db.execute(query)
    #
    # # This variable now has the result of the query
    # found = result.fetchall()
    #
    # if not found:
    #     return page_not_found(404)
    #
    # # Convert into xspf format
    # # Create xspf playlist_filter
    # # return xml as response?
    #
    # # return make_response(jsonify(found))
