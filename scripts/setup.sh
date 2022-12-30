#setup.sh - run this after pulling from develop

#import our IP ($ELIP)
source ~/.env

#shutdown the old rasa and the rasa-action server
pkill screen

#train rasa + run the rasa and the rasa action server
#the rasa server puts its logs into /home/ubuntu/chat-team-11/rasa/out.log
cd ~/chat-team-11/rasa
conda activate rasaenv
rasa train
screen -S rasa -d -m rasa run --cors "*" --enable-api --log-file out.log --debug
screen -S rasa-actions -d -m rasa run actions

#copy everything [*], including directorys [-r] to the apache2 server
cd ~/chat-team-11/frontend
sudo cp -r * /var/www/html/

#replace 'localhost' in the 'index.html' and 'scripts.html' with our server-IP
cd /var/www/html/
sudo sed -i -e "s/localhost/$ELIP/g" index.html
sudo sed -i -e "s/localhost/$ELIP/g" scripts.js

#restart html server
sudo systemctl restart apache2
