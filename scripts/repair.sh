#get IP from commandline argument
#if there's no argument, abort
IP=$1
if [ -z "$IP" ]
then
  echo "IP param is unset! Aborting..."
  exit
else
  echo "IP is set to '$1'"
fi

#replace an arbitrary IP with the IP provided from the commandline ($1)
cd /var/www/html/
sudo sed -i -r 's/(\b[0-9]{1,3}\.){3}[0-9]{1,3}\b'/"$1"/ index.html
sudo sed -i -r 's/(\b[0-9]{1,3}\.){3}[0-9]{1,3}\b'/"$1"/ scripts.js

#restart the html server
sudo systemctl restart apache2
