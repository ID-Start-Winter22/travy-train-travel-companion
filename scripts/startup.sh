conda activate rasaenv
cd /home/ubuntu/chat-team-11/rasa/
screen -S rasa -d -m rasa run --cors "*" --enable-api --log-file out.log --debug
screen -S rasa-actions -d -m rasa run actions
