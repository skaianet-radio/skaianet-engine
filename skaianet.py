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

import config
import datetime
import mysql.connector
from mutagen.easyid3 import EasyID3

global db

def _dprint(msg):
    if config.debug is True:
        print (datetime.datetime.now().strftime("[%H:%M:%S] ") + msg)

def initdb():
    global db
    _dprint('Initializing database connector...')
    db = mysql.connector.connect(config.dbuser,
                                 config.dbpass,
                                 config.dbname)

def _addsongtodb(path):
    _dprint('Importing: ' + path)
    songid3 = EasyID3(path)
    songmeta = {'title': songid3["title"][0].encode('utf-8'),
                'artist': songid3["artist"][0].encode('utf-8'),
                'album': songid3["album"][0].encode('utf-8')}
    _dprint('    Title: ' + songmeta['title'])
    _dprint('   Artist: ' + songmeta['artist'])
    _dprint('    Album: ' + songmeta['album'])
