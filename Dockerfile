FROM alpine:latest
MAINTAINER morenod

RUN apk add --no-cache sqlite tzdata python python-dev py-pip build-base \
  && pip install PyTelegramBotAPI==3.1.0

ENV TZ="Europe/Madrid"

ADD punsbot.py /
ADD defaultpuns /defaultpuns

CMD ["python", "-u", "/punsbot.py"]
