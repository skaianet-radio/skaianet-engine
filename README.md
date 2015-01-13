# skaianet-engine

This is a set of python2 scripts designed to back an ices 0.4 streaming client for a customized radio setup, handling requests and playing jingles and commercials at given intervals.

## Setup

* Install [ices 0.4](http://downloads.us.xiph.org/releases/ices/ices-0.4.tar.gz).  It's deprecated, but it does what we need it to do better than ices 2.x.
* Copy config.py.dist to config.py and edit the file appropriately.
* Copy radio.conf.dist to radio.conf and edit the file appropriately.
* Make a MySQL database and populate it with extra/schema.sql  (This should be done automatically further down the developmental road.)
* Execute $ ices -c radio.conf
* Have a look at [skaianet-web](https://github.com/skaianet-radio/skaianet-web) if you're interested in using our web interface.

## Disclaimer
This software is currently in heavy amateur development, so we hereby go above and beyond the GPL 3.0 license's limitation of liability and warranty to warn you that this project may not be fit for whatever you would like to use it for, and that it may just make whatever you run it on immediately self destruct.  Use it at your own risk.
