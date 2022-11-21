# 🚆 Train Travel Companion 🤖

# 📑 About:
## Description:
The Train Travel Companion is a chatbot which provides you with information to about your train, gives you live updates on your train journey  and answers questions.

## How does it work?
The chatbot is built using the [Rasa](https://rasa.com/) framework.<br/>
To get live data about the trains, the backend makes requests to the public [bahn.expert](https://docs.bahn.expert/) API.

## Who is it for?
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.

---

# 👨‍👨‍👧 Team:
| name | email |
| :------------- |:------------- |
| Lynn Starke | lstarke@hm.edu | 
| Markus Schnugg | schnugg@hm.edu |
| Theodor Peifer | theodor.peifer@hm.edu |

---

# 🦾 Abilities:

## Intents:
| intent | description |
| :------------- |:------------- |
| find_train | Extracts the train number and requests data about it from the API | 
| get_platform | Requests the platform number from the API |
| get_times | Requests the arrival, departure and delay from the API |
| get_platform_plan | Gets an image of the platform plan of the arrival/departure station |

lynn test