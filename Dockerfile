FROM python:3.8

RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean
RUN apt-get -y install postgresql-client

RUN mkdir /app
COPY . /app/
WORKDIR /app

ENV EMAIL="EpicTeamSite@gmail.com"
ENV PASSWORD="Hgm87nDc9"
ENV ADMIN_EMAIL="Morkovo4ka513@yandex.ru"
ENV ADMIN_PASSWORD="admin54321"
ENV URL_SAFE="jdskUewn"
ENV SECRET_KEY="Lkiew98n"
ENV FLASK_APP=start.py

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "start.py"]


