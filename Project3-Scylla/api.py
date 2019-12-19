# Music Microservices APIs Project
# CPSC 449- Backend Engineering
#This file initializes our scylla db

import flask
from flask import g, request, make_response, jsonify
from cassandra.cluster import Cluster
from flask_cassandra import CassandraCluster
from cassandra.query import SimpleStatement

app = flask.Flask(__name__)
app.config['CASSANDRA_NODES'] = ['172.17.0.2']

@app.errorhandler(404)
def page_not_found(e):
    return jsonify('HTTP 404 Not Found'), 404


@app.errorhandler(409)
def constraint_violation(e):
    return jsonify('HTTP 409 Conflict'), 409

@app.cli.command('init')
def init_db():
    cassandra = CassandraCluster()
    session = cassandra.connect()
    session.set_keyspace('musicservice')

    #drop tables if exist:
    session.execute('DROP TABLE IF EXISTS user;')
    session.execute('DROP TABLE IF EXISTS track;')
    session.execute('DROP TABLE IF EXISTS playlist;')

    #create tables:
    #user table:
    session.execute(
        """
        CREATE TABLE user (
            username varchar,
            password varchar,
            display_name varchar,
            email varchar,
            homepage_url varchar,
            PRIMARY KEY (username)
            );
        """
    )

    #track table: Stores all inddividu
    session.execute(
        """
        CREATE TABLE track (
            track_id uuid,
            track_title varchar,
            album_title varchar,
            artist varchar,
            length_seconds int,
            url_media varchar,
            url_art varchar,
            descriptions map<varchar, varchar>,
            PRIMARY KEY (track_id)
            );
        """
    )

    #playlist table:
    session.execute(
        """
        CREATE TABLE playlist (
            playlist_id int,
            playlist_title varchar,
            description varchar,
            tracks set<uuid>,
            PRIMARY KEY (playlist_id)
            );
        """
    )
