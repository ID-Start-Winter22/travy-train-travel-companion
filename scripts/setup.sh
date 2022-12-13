pkill screen
cd ~/chat-team-11/rasa
conda activate rasaenv
rasa train
screen -S rasa -d -m rasa run --cors "*" --enable-api --log-file out.log --debug
screen -S rasa-actions -d -m rasa run actions
cd ~/chat-team-11/frontend
sudo cp -r * /var/www/html/
cd /var/www/html/
sudo sed -i -e "s/localhost/34.251.35.212/g" index.html
sudo sed -i -e "s/localhost/34.251.35.212/g" scripts.js
sudo systemctl restart apache2
