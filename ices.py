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

from string import *
import sys
import os
os.chdir(os.path.dirname(sys.argv[0]))
import datetime
import mysql.connector
import config
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

# - Kitty's Radio Script -
#
# You're about to embark on an amazing-- oh who cares.
# If it works, it works, no guarantees.

library = "/home/kitty/ices/library/"
db = mysql.connector.connect(
        user=config.dbUser,
        password=config.dbPass,
        database=config.dbName)
intervalcount = 0

def dprint (msg):
    print '{} '.format(datetime.datetime.now().strftime("[%H:%M:%S]")) + msg

def ices_init ():
    dprint('Initializing...')
    dprint('Checking Songs against DB')
    for root,dirs,files in os.walk(library):
        for file in files:
            if file.endswith(".mp3"):
                mp3file = os.path.join(root, file)
                mp3cursor = db.cursor()
                mp3query = ("SELECT id FROM library WHERE filepath=%(path)s")
                mp3cursor.execute(mp3query, {'path': mp3file})
                if not mp3cursor.fetchall():
                    print '{} Importing: {}'.format(datetime.datetime.now().strftime("[%H:%M:%S]"), mp3file)
                    mp3meta = EasyID3(mp3file)
                    print '     Title:  {}'.format(mp3meta["title"][0].encode('utf-8'))
                    print '     Artist: {}'.format(mp3meta["artist"][0].encode('utf-8'))
                    print '     Album:  {}'.format(mp3meta["album"][0].encode('utf-8'))
                    mp3update = db.cursor()
                    mp3updateq = ("INSERT INTO library "
                                  "(title, artist, album, filepath) "
                                  "VALUES (%(title)s, %(artist)s, %(album)s, %(filepath)s)")
                    mp3data = {'title': mp3meta["title"][0].encode('utf-8'),
                               'artist': mp3meta["artist"][0].encode('utf-8'),
                               'album': mp3meta["album"][0].encode('utf-8'),
                               'filepath': mp3file }
                    mp3update.execute(mp3updateq, mp3data)
                    mp3update.close()
                mp3cursor.close()
    print '{} Checking DB against Songs'.format(datetime.datetime.now().strftime("[%H:%M:%S]"))
    mp3libcursor = db.cursor()
    mp3libcursor.execute("SELECT id,filepath FROM library")
    mp3library = mp3libcursor.fetchall()
    mp3libcursor.close()
    for id,filepath in mp3library:
        if not os.path.isfile(filepath):
            print '{} Deleting: {}'.format(datetime.datetime.now().strftime("[%H:%M:%S]"), filepath)
            mp3remove = db.cursor()
            mp3remove.execute("DELETE FROM library WHERE id=%s", {id})
            mp3remove.close()
    db.commit()
    print '{} Initialization complete.'.format(datetime.datetime.now().strftime("[%H:%M:%S]"))
    return 1

# Function called to shutdown your python enviroment.
# Return 1 if ok, 0 if something went wrong.
def ices_shutdown ():
	dprint('Shutting Down...')
	db.close()
	return 1

# Function called to get the next filename to stream.
# Should return a string.
def ices_get_next ():
	global intervalcount
	global currentMp3
	intervalcount += 1
	print intervalcount;
	if intervalcount >= 5:
		intervalcount = 0
		currentMp3 = {
			"title": ["Skaianet Ad Hatorade"],
			"artist": ["Advertisement"] }
		return '/home/kitty/ices/jingles/Skaianet Ad Hatorade.mp3'
	dprint('Next Song')
	reqCountC = db.cursor()
	reqCountC.execute('SELECT * FROM requests LIMIT 1')
	reqPotato = reqCountC.fetchall()
	reqCount = reqCountC.rowcount
	reqCountC.close()
	nextmp3 = db.cursor()
	reqname = ""
	reqsrc = ""
	if reqCount > 0:
		print 'REQUEST THERE, NEED TO PROCESS'
		nextmp3q = ("SELECT id,filepath FROM library WHERE id=%(song)s")
		nextmp3.execute(nextmp3q, {'song': reqPotato[0][1]})
		reqname = reqPotato[0][2]
		reqsrc = reqPotato[0][3]
	else:
		print 'NO REQUEST, MOVING ON'
		nextmp3q = ("SELECT id,filepath FROM library WHERE autoplay=1 ORDER BY RAND() LIMIT 1")
		nextmp3.execute(nextmp3q)
	nextmp3p = nextmp3.fetchall()[0]
	nextmp3.close()
	if reqCount > 0:
		reqRemove = db.cursor()
		reqRemove.execute("DELETE FROM requests WHERE id=%(reqid)s", {'reqid': reqPotato[0][0]})
		reqRemove.close()
		db.commit()
	currentMp3 = MP3(nextmp3p[1], ID3=EasyID3)
	recentC = db.cursor()
	recentQ = ("INSERT INTO recent "
		   "(songid, title, artist, album, length, reqname, reqsrc, time) "
		   "VALUES (%(songid)s, %(title)s, %(artist)s, %(album)s, %(length)s, %(reqname)s, %(reqsrc)s, CURRENT_TIMESTAMP())")
	recentD = {
		'songid':  nextmp3p[0],
		'title':   currentMp3["title"][0].encode('utf-8'),
		'artist':  currentMp3["artist"][0].encode('utf-8'),
		'album':   currentMp3["album"][0].encode('utf-8'),
		'length':  round(currentMp3.info.length),
		'reqname': reqname,
		'reqsrc':  reqsrc }
	recentC.execute(recentQ, recentD)
	recentC.close()
	db.commit()
	return '{}'.format(nextmp3p[1])

# This function, if defined, returns the string you'd like used
# as metadata (ie for title streaming) for the current song. You may
# return null to indicate that the file comment should be used.
def ices_get_metadata ():
	print '{} Title: {} - {}'.format(datetime.datetime.now().strftime("[%H:%M:%S]"), currentMp3["artist"][0].encode('utf-8'), currentMp3["title"][0].encode('utf-8'))
	return "{0} - {1}".format(currentMp3["artist"][0].encode('utf-8'), currentMp3["title"][0].encode('utf-8'))
