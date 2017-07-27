# PunsBot

A very extended Spanish tradition is about to make puns when talking to a friend using the last word of a sentence.

For example (Spanish):

-- He quedado con Carlos

-- ¿Que Carlos?

-- ¡¡El de los cojones largos!!


PunsBot is a telegram Bot to automatically make this kind of puns on Telegram Group Chats.

It has a default database of puns (English & Spanish) and any other can be added on your channel using commands.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

This bot uses the python library [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)

It can be easily installed using pip

```
$ pip install pyTelegramBotAPI
```

Or obtaining it from source

```
$ git clone https://github.com/eternnoir/pyTelegramBotAPI.git
$ cd pyTelegramBotAPI
$ python setup.py install
```

Telegram token and sqlite database has to be exported as shell vars:

```
$ export DBLOCATION=/Users/david/punsdb.db
$ export TOKEN=<<telegram token>>
```

For information about how to create a Telegram Bot and obtain a token, enter on https://core.telegram.org/bots


### Installing

For installing punsBot, just download the [punsBot.py](https://github.com/morenod/punsBot/blob/master/punsbot.py) and the defaultpuns directory [defaultpuns](https://github.com/morenod/defaultpuns) and place them in the same directory.

```
$ find .
.
./defaultpuns
./defaultpuns/englishpuns
./defaultpuns/spanishpuns
./punsbot.py
```

SQLite database will be created on the first run if it does not exists.

```
$ export TOKEN=360...4TJHQ
$ export DBLOCATION=./punsdb.db
$ python punsbot.py
PunsBot 0.4.0 ready for puns!
```

## Deployment

PunsBot can be deployed as shell script or using cointainers. a Dockerfile is included in the repository to deploy it on a docker host.

## Built With

* [DockerHub](https://hub.docker.com/r/gotrunks/punsbot/) - Automated builts are created with each commit on the develop and master branches, and manual builts are created with each production-ready release.

To deploy PunsBot using docker:

```
docker run --name=punsBot -v /var/punsdb:/var/punsdb -e TOKEN=$TOKEN -e DBLOCATION=/var/punsdb/punsdb.db -d  gotrunks/punsbot
```

## Usage


## Authors

* **David Sanz** - *Initial work* - [morenod github](https://github.com/morenod)
* **Karim Boumedhel** - *Default puns & database initial load* - [karmab github](https://github.com/karmab)

See also the list of [contributors](https://github.com/morenod/punsBot/graphs/contributors) who participated in this project.

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE.md](LICENSE.md) file for details
