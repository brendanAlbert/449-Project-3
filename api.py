# Music Microservices APIs Project
# CPSC 449- Backend Engineering
#This file initializes our DB from our .sql schema file

import flask
from flask import g
import sqlite3
import uuid

app = flask.Flask(__name__)
app.config.from_envvar('APP_CONFIG')

track_shard_db_names = ['TRACKS_SHARD1','TRACKS_SHARD2','TRACKS_SHARD3']
db_context_names = ['_trackshard1', '_trackshard2', '_trackshard3', '_database']

sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))

@app.cli.command('init')
def init_db():
    with app.app_context():

        # need to init 3 track shards before running the user/descriptions/playlists
        for shard in track_shard_db_names:
            db = get_db(shard)
            with app.open_resource('trackService.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()

        db = get_db('user_desc_playlist')
        with app.open_resource('musicService.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


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
    else:
        db = getattr(g, db_context_names[3], None)
        if db is None:
            db = g._database = sqlite3.connect(app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
            db.row_factory = make_dicts

    return db


@app.teardown_appcontext
def close_connection(exception):
    for dbname in db_context_names:
        db = getattr(g, dbname, None)
        if db is not None:
            db.close()
