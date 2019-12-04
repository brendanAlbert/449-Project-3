PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS Track (
    track_id GUID primary key,
    track_title VARCHAR,
    album_title VARCHAR,
    artist VARCHAR,
    length_seconds INTEGER,
    url_media VARCHAR,
    url_art VARCHAR,
    UNIQUE(track_title, artist)
);

---------------------------------------------------------------
--SECTION TO INSERT SAMPLE DATA TO START DB WITH--
---------------------------------------------------------------

--Inserting sample tracks

-- We can't insert Tracks this way anymore because we have sharded the Tracks database.
-- If we try to do it this way, the track never gets a Shard Key ID which means we can insert duplicate copies into different shards
-- INSERT INTO Track(track_title, album_title, artist, length_seconds, url_media, url_art) VALUES('Under Pressure', 'Hot Space', 'Queen', 191, 'www.soundcloud.com/songExample1', 'www.www.flickr.com/img1');
-- INSERT INTO Track(track_title, album_title, artist, length_seconds, url_media, url_art) VALUES('Stan', 'The Marshall Mathers LP','Eminem', 180, 'www.soundcloud.com/songExample2', 'www.www.flickr.com/img2');
-- INSERT INTO Track(track_title, album_title, artist, length_seconds, url_media, url_art) VALUES('Sunflower', 'Spiderman:Spiderverse', 'Post Malone', 187, 'www.soundcloud.com/songExample3', 'www.www.flickr.com/img3');

COMMIT;
