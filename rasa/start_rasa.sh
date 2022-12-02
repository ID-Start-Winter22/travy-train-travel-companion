# rasa run --cors "*" --enable-api & rasa run actions &
screen -S rasa -d -m rasa run --cors "*" --enable-api
screen -S rasa-actions -d -m rasa run actions
