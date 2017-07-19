FROM gliderlabs/alpine:3.3
MAINTAINER morenod

RUN apk add --no-cache python python-dev py-pip build-base \
  && pip install PyTelegramBotAPI==3.1.0

ADD punsbot.py /

CMD ["python", "-u", "/punsbot.py"]
