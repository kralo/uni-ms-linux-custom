#!/bin/sh

# this file is licensed under the mit license. see file LICENSE for details

# ----- README
# script to add bookmarks to nautilus from command line

# designed for ubuntu linux 14.04, tested to work.
# this script adds a bookmark that will appear in nautilus file manager
# under the network section

#the bookmarks-file is easily readyble, have a look at it.

read -p "ZIV-Nutzerkennung? (s_tudi01): " kennung
echo "davs://zivdav.uni-muenster.de/pp/$kennung zivdav uni-ms" >> ~/.config/gtk-3.0/bookmarks
