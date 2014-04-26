#!/bin/sh

# this file is licensed under the mit license. see file LICENSE for details

# ----- README
# script to fully automatically add vpn connection to network-manager on command line
# tested with ubuntu 14.04

# we need root for copying files to /etc/NetworkMa...
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

#install cisco easyconnect compatible client
apt-get install network-manager-openconnect network-manager-openconnect-gnome

destination_fn="uni-ms-vpn"
destfile=/etc/NetworkManager/system-connections/$destination_fn

cp -v template_vpn.txt "$destfile"

echo " "
read -p "ZIV-Nutzerkennung? (s_tudi01): " kennung

# nutzerkennung vorausfuellen
sed -i 's/_zivusername_/'$kennung'/g' "$destfile"

# lokalen benutzernamen einfuegen
# denn nur dann speichert das Verbindungsformular z.B. den Benutzernamen für VPN
sed -i 's/_username_/'$(logname)'/g' "$destfile"

# important! Network-manager monitors files and only adds them to menu if they absolutely have the right permissions
chmod 600 "$destfile"

echo "now waiting 2sec for nm to detect new file"
sleep 2
echo "now starting connection, please wait"

#start applet as normal user so it can show dialogue
sudo -u $(logname) nmcli con up id uni-ms-vpn


