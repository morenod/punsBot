###### GitHub Repo
[![GitHub release](https://img.shields.io/github/release/morenod/punsbot.svg)]()
[![license](https://img.shields.io/github/license/morenod/punsbot.svg)]()
###### Docker Image
[![](https://images.microbadger.com/badges/image/gotrunks/punsbot:0.4.0.svg)](https://microbadger.com/images/gotrunks/punsbot:0.4.0 "Get your own image badge on microbadger.com")
[![](https://images.microbadger.com/badges/version/gotrunks/punsbot:0.4.0.svg)](https://microbadger.com/images/gotrunks/punsbot:0.4.0 "Get your own version badge on microbadger.com")
[![Docker Automated buil](https://img.shields.io/docker/automated/gotrunks/punsbot.svg)]()
[![Docker Build Statu](https://img.shields.io/docker/build/gotrunks/punsbot.svg)]()
[![Docker Stars](https://img.shields.io/docker/stars/gotrunks/punsbot.svg)]()
[![Docker Pulls](https://img.shields.io/docker/pulls/gotrunks/punsbot.svg)]()
###### Travis CI
Master: [![Build Status](https://travis-ci.org/morenod/punsBot.svg?branch=master)](https://travis-ci.org/morenod/punsBot)

Develop: [![Build Status](https://travis-ci.org/morenod/punsBot.svg?branch=develop)](https://travis-ci.org/morenod/punsBot)
# PunsBot

A very extended Spanish tradition is about to make puns when talking to a somebody using the last word of a sentence.

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

### Default Puns Submodule

Default puns are obtained from a [secondary repo](https://github.com/morenod/defaultpuns). It can be used or not to deploy a new instance. It is referenced from the bot repo pointing to the last existinng commit when release is created. If you want to use the last version of it, remember to update the submodule when clonning the repo.

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

- To start bot on a chat, add **@puns2bot** contact on it
- To list available puns, execute **/list** or **/punslist**, it will list default puns, available for all chats, and specific puns, added on your channel.
- To add a new pun, execute **/punadd** followed by the trigger used to detect the pun, a "|" char as separator and the pun, for example:
  - **/punadd carlos|el de los cojones largos**
- Regex are valid on triggers, for example:
  - **/punadd ^.\*ado$|el que tengo aqui colgado**

    This trigger will detect all words ended on **ado**, like Abogado, Certificado, etc...

- Added puns are created disabled, they have to be validated by people of the chat. Minimun karma required to enable a pun can be configured with the parameter **required_validations**

- To add +1 to the karma of a pun, execute **/punapprove UUID**

- To add -1 to the karma of a pun, execute **/punban UUID**

- To delete a pun, execute **/pundel** followed by the **UUID** of the pun. UUID can be obtained from the **/list** command. Only channel puns can be deleted.

## Production Deployment

A running instance of punsBot can be found opening a chat to the Telegram contact @puns2bot or entering on https://telegram.me/puns2bot

## Authors

* **David Sanz** - *Initial work* - [morenod github](https://github.com/morenod)
* **Karim Boumedhel** - *Default puns & database initial load* - [karmab github](https://github.com/karmab)
* **Raul Sevilla** - *Default puns & randomize puns* - [rsevilla87 github](https://github.com/rsevilla87)

See also the list of [contributors](https://github.com/morenod/punsBot/graphs/contributors) who participated in this project.

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE.md](LICENSE.md) file for details
