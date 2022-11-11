# ein einfacher Chatbot
<img width="374" alt="image" src="https://user-images.githubusercontent.com/14870896/197331342-5fc573e2-c31b-4576-bc55-449a3ff89e04.png">

1. Rasa installieren (siehe https://github.com/michaeleggers/RasaIntro)

2. im Terminal folgende Befehle ausführen:
```
git clone https://github.com/ID-Start-Winter22/einfacherChatbot.git
```
```
cd einfacherChatbot
```
```
conda activate rasaenv
```
```
rasa train
```
```
rasa run --cors "*" --debug
```
3. in einem zweiten Terminal:

```
rasa run actions
```

4. (optional in einem dritten Terminal:)

```
python -m http.server
```

5. im Browser http://localhost:8000/ oder im Browser [./index.html](./index.html) öffnen

# MacOS (M1/2)
Falls die obigen Befehle so nicht funktionieren, ein
```
python -m
```
davorstellen, also zB:
```
python -m rasa train
```

