FROM gliderlabs/alpine:3.3
MAINTAINER morenod

RUN apk add --no-cache python python-dev py-pip build-base \
  && pip install PyTelegramBotAPI==2.2.3

ADD punsbot.py /

CMD ["python", "/punsbot.py"]
