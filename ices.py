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
import datetime
import config
import skaianet
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

intervalcount = 0


def ices_init():
    skaianet.initdb()
    skaianet.checkdb()
    return 1


def ices_shutdown():
    skaianet.closedb()
    return 1


def ices_get_next():
    global intervalcount
    global currentmp3
    intervalcount += 1
    print intervalcount
    if intervalcount >= 5:
        intervalcount = 0
        currentmp3 = {
            "title": ["Skaianet Ad Hatorade"],
            "artist": ["Advertisement"]}
        return '/home/kitty/ices/jingles/Skaianet Ad Hatorade.mp3'
    if skaianet.requestqueued():
        currentmp3 = skaianet.getrequest()
    else:
        currentmp3 = skaianet.getrandomsong()
    skaianet.setplaying(
        currentmp3["id"],
        currentmp3["title"],
        currentmp3["artist"],
        currentmp3["album"],
        currentmp3["length"],
        currentmp3["reqname"],
        currentmp3["reqsrc"])
    return '{}'.format(currentmp3["path"])


def ices_get_metadata():
    mdstring = currentmp3["artist"] + ' - ' + currentmp3["title"]
    skaianet._dprint('Title: ' + mdstring)
    return mdstring
