#!/bin/sh

# skript, um von uns für gut beachtete Pakete nachzuinstallieren :-)


if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

apt-get install \
	gimp \
	network-manager-openconnect
