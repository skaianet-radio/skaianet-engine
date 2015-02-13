###
# Copyright (c) 2015, George Burfeind (Kitty)
# All rights reserved.
#
# This file is part of skaianet-engine.
#
# skaianet-engine is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# skaianet-engine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with skaianet-engine.  If not, see <http://www.gnu.org/licenses/>.
###

import os
import config
import datetime
import mysql.connector
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

global db


def _dprint(msg):
    """ Print a debug line.
    This is a simple function.  If I got any more meta, I'd be telling
    you about how this is a docstring.
    """
    if config.debug is True:
        print(datetime.datetime.now().strftime("[%H:%M:%S] ") + msg)


def initdb():
    """ Initializes the database used for radio control.
    Must be called on it's own at least once before anything that
    calls the database is used.
    ** SHOULD check for proper schema, but does not.
    """
    global db
    _dprint('Initializing database connector...')
    db = mysql.connector.connect(user=config.dbuser,
                                 password=config.dbpass,
                                 database=config.dbname)
    _dprint('NOT Checking schema... (Fix me!)')


def closedb():
    """ Ensures all changes are saved before closing the database.
    Should be called only when all DB actions are done.
    """
    _dprint('Saving changes to database...')
    db.commit()
    _dprint('Closing database...')
    db.close()


def checkdb():
    """ Check the database against the song library for consistency.
    Ensures that all songs in the database match a file and also that
    all files have a database entry.
    """
    _dprint('Checking Songs against DB')
    for root, dirs, files in os.walk(config.librarypath):
        for file in files:
            if file.endswith(".mp3"):
                mp3file = os.path.join(root, file)
                mp3cursor = db.cursor()
                mp3query = ("SELECT id FROM library WHERE filepath=%(path)s")
                mp3cursor.execute(mp3query, {'path': mp3file})
                if not mp3cursor.fetchall():
                    _addsongtodb(mp3file)
                mp3cursor.close()
    _dprint('Checking DB against Songs')
    mp3libcursor = db.cursor()
    mp3libcursor.execute("SELECT id,filepath FROM library")
    mp3library = mp3libcursor.fetchall()
    mp3libcursor.close()
    for id, filepath in mp3library:
        if not os.path.isfile(filepath):
            _rmsongfromdb(id)
    db.commit()


def _addsongtodb(path):
    """ Add a song to the library.
    Takes the path of an MP3 file, and then adds the path and metadata
    to the library database for use in circulation or requests.
    """
    _dprint('Importing: ' + path)
    songid3 = EasyID3(path)
    songmeta = {'title': songid3["title"][0].encode('utf-8'),
                'artist': songid3["artist"][0].encode('utf-8'),
                'album': songid3["album"][0].encode('utf-8')}
    _dprint('    Title: ' + songmeta['title'])
    _dprint('   Artist: ' + songmeta['artist'])
    _dprint('    Album: ' + songmeta['album'])
    insertcursor = db.cursor()
    insertdata = {
        'query': "INSERT INTO library "
                 "(title, artist, album, filepath) "
                 "VALUES (%(title)s, %(artist)s, %(album)s, %(filepath)s)",
        'data': {'title': songmeta['title'],
                 'artist': songmeta['artist'],
                 'album': songmeta['album'],
                 'filepath': path}}
    insertcursor.execute(insertdata['query'], insertdata['data'])
    insertcursor.close()
    db.commit()


def _rmsongfromdb(id):
    """ Remove a song from the library.
    Takes the ID number assigned to a song's database entry and removes
    it from the database.
    """
    _dprint('Removing song ID #' + str(id))
    removecursor = db.cursor()
    removecursor.execute("DELETE FROM library WHERE id=%(id)s", {'id': id})
    removecursor.close()
    db.commit()


def _checkifrecent(id, range):
    """ Checks if a song was recently played.
    Takes the song ID number and a range of how many historic plays to
    compare the specified song against as arguments.
    """
    recentcursor = db.cursor()
    recentcursor.execute(
        "SELECT songid FROM recent ORDER BY id DESC LIMIT %(range)s",
        {'range': range})
    recents = recentcursor.fetchall()
    recentcursor.close()
    for songid in recents:
        if songid[0] == id:
            return True
    return False


def setplaying(songid, title, artist, album, length,
               reqname='', reqsrc=''):
    """ Adds a song to the recently played database.
    This is assuming that this function is called when the song starts
    playing so that the timing can be accurate for linked functions.
    Takes arguments of the songs DB number, title, album, artist,
    length in seconds, and optionally, the person requesting the song.
    """
    setcursor = db.cursor()
    setdata = {
        'query': "INSERT INTO recent "
                 "(songid, title, artist, album, length, "
                 "reqname, reqsrc, time) "
                 "VALUES (%(songid)s, %(title)s, %(artist)s,"
                 "%(album)s, %(length)s, "
                 "%(reqname)s, %(reqsrc)s, CURRENT_TIMESTAMP())",
        'data': {'songid': songid,
                 'title': title,
                 'artist': artist,
                 'album': album,
                 'length': length,
                 'reqname': reqname,
                 'reqsrc': reqsrc}}
    setcursor.execute(setdata['query'], setdata['data'])
    setcursor.close()
    db.commit()


def requestqueued():
    """ Checks if there is a request waiting to be processed.
    Takes no arguments, returns True or False.
    """
    _dprint('Checking for requests...')
    reqcheckcursor = db.cursor()
    reqcheckcursor.execute('SELECT * FROM requests LIMIT 1')
    reqcheckcursor.fetchall()
    reqcount = reqcheckcursor.rowcount
    reqcheckcursor.close()
    db.commit()
    if reqcount > 0:
        _dprint('Request has been found.')
        return True
    else:
        _dprint('No request is present.')
        return False


def _getmp3meta(path):
    mp3meta = MP3(path, ID3=EasyID3)
    return {
        'title': mp3meta['title'][0].encode('utf-8'),
        'artist': mp3meta['artist'][0].encode('utf-8'),
        'album': mp3meta['album'][0].encode('utf-8'),
        'length': round(mp3meta.info.length)}


def getrandomsong():
    while True:
        randcursor = db.cursor()
        randcursor.execute("SELECT id,filepath FROM library WHERE autoplay=1"
                           " ORDER BY RAND() LIMIT 1")
        randresult = randcursor.fetchall()[0]
        randcursor.close()
        db.commit()
        if _checkifrecent(randresult[0], 10):
            _dprint('Repeat track found, re-randomizing...')
        else:
            break
    randmeta = _getmp3meta(randresult[1])
    return {
        'id': randresult[0],
        'path': randresult[1],
        'title': randmeta['title'],
        'artist': randmeta['artist'],
        'album': randmeta['album'],
        'length': randmeta['length']}
