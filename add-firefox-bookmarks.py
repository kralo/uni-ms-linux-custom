#!/usr/bin/python
# -*- coding: utf-8 -*-

# this file is licensed under the mit license. see file LICENSE for details

# ----- README
# script to add bookmarks to nautilus from command line automatically
# tested in ubuntu 14.04
# CAUTION! its an ugly hack. Make sure you ran firefox once before so that every file is in place.

# Do only use after fresh install. If there are already user defined bookmarks and tags
# I don't know what might happen.

import sqlite3 as lite
import sys
import os
import subprocess
from os.path import expanduser
firefoxdir = expanduser("~/.mozilla/firefox/")

con = None
# define bookmarks to insert
# (url, title, placement, [tags]) where placement is one of (menu,toolbar), 'places' not currently supported
bookmarks = [     ['http://www.uni-muenster.de/de/', 'Uni Muenster', 'toolbar', ['uni','wwu']],
	          ['https://sso.uni-muenster.de/perMail/cgi/permail?ssoredirect=1&cset=utf-8', 'perMail', 'toolbar', ['uni','wwu','permail','mail']],
	          ['https://sso.uni-muenster.de/mywwu/', 'myWWU', 'toolbar', ['uni','wwu','mywwu']],
	          ['https://sso.uni-muenster.de/LearnWeb/learnweb2/', 'learnWeb', 'toolbar', ['uni','wwu','learnweb']],
	          ['http://lugunimuenster.de', 'LUG Uni Muenster', 'toolbar', ['uni','wwu','lug','linux','gruppe']]]
tags = []

#open firefox once, so that every data-folder ok etc..
#os.system['firefox && killall firefox')

#make sure to close firefox
sub = subprocess.call(['killall','firefox'])

#try finding the firefox profile folder

for line in open(firefoxdir + "profiles.ini"):
 if "Path" in line:
   profile = line.replace('Path=','')

placesdb = firefoxdir + profile.strip() + "/places.sqlite"



## modify localstore to display bookmarks menu bar
## you have to set
# <RDF:Description RDF:about="chrome://browser/content/browser.xul#PersonalToolbar" collapsed="false" />
# and add a
#     <NC:persist RDF:resource="chrome://browser/content/browser.xul#PersonalToolbar"/>
# to the <RDF:Description RDF:about="chrome://browser/content/browser.xul"> - Block
localstore = firefoxdir + profile.strip() + "/localstore.rdf"

#if you have modified once the menu toolbar, we will have to overwrite the value to make it Collapsed="false"
# \\n is pearl escaped to produce \n command for sed
sub = subprocess.call(['sed','-i',":a;N;$!ba;s/\\n/ /g", localstore] )
sub = subprocess.call(['sed','-i',"s/#PersonalToolbar\".*collapsed=\".\{1,5\}\"/#PersonalToolbar\" collapsed=\"false\"/g", localstore] )

#make setting persistent, add a line
sub = subprocess.call(['sed','-i','s$</RDF:Description>$<NC:persist RDF:resource="chrome://browser/content/browser.xul#PersonalToolbar"/></RDF:Description>$g', localstore] )

#never changed the toolbar, value is not present at all, so append
sub = subprocess.call(['sed','-i',"s$</RDF:RDF>$$g", localstore] )
with open(localstore, "a") as myfile:
    myfile.write('<RDF:Description RDF:about="chrome://browser/content/browser.xul#PersonalToolbar" collapsed="false" /></RDF:RDF>')

print "Arbeite in %s" % placesdb

try:
    con = lite.connect(placesdb)
  
    cur = con.cursor()    

    ## Fill 'parents'
    cur.execute("SELECT rowid FROM moz_bookmarks_roots where root_name = 'toolbar'")
    toolbarRoot = int(cur.fetchone()[0])

    cur.execute("SELECT rowid FROM moz_bookmarks_roots where root_name = 'places'")
    placesRoot = int(cur.fetchone()[0])

    cur.execute("SELECT rowid FROM moz_bookmarks_roots where root_name = 'menu'")
    menuRoot = cur.fetchone()

    cur.execute("SELECT rowid FROM moz_bookmarks_roots where root_name = 'tags'")
    tagsRoot = int(cur.fetchone()[0])

    #-- handle Tags, insert them --
    #make complete list
    for pla in bookmarks:
      for tag in pla[3]:
	tags.append(tag)
    #make unique list of tags
    tags = list(set(tags))
    print "Alle tags:"
    print tags
    
    for tag in tags:
      cur.execute('INSERT INTO "main"."moz_bookmarks" ("type","parent","title") VALUES (?1,?2,?3)',(2,tagsRoot,tag))
    
    con.commit()
    
    #-- insert Bookmarks --
    for bookmark in bookmarks:
      #insert place: fixme, check if already exists 
      cur.execute('INSERT INTO moz_places ("url","title") VALUES (?1,?2)',(bookmark[0],bookmark[1]))
      con.commit()
      place = cur.lastrowid
      cur.execute('INSERT INTO "main"."moz_bookmarks" ("type","fk","parent","title","position") VALUES (?1,?2,?3,?4,3)',(1,place, menuRoot if bookmark[2]=='menu' else toolbarRoot,bookmark[1]))
      con.commit()
      
      
      ##for each tag: parent is tag, fk is place
      for tag in bookmark[3]:
	cur.execute('SELECT id FROM moz_bookmarks where title="' + tag + '"')
	tagid = int(cur.fetchone()[0])#
	cur.execute('INSERT INTO "main"."moz_bookmarks" ("type","fk","parent","title","position") VALUES (?1,?2,?3,?4,?5)',(1,place, tagid,bookmark[1],0))
      
      print(bookmark[1] + " erledigt")

    
    con.commit()
       
except lite.Error, e:
    
    print "Error %s:" % e.args[0]
    sys.exit(1)
    
finally:
    
    if con:
        con.close()

