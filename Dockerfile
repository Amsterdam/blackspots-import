FROM amsterdam/python:3.8-buster as app
MAINTAINER datapunt@amsterdam.nl

RUN apt-get update \
	&& apt-get install -y gdal-bin libgeos-dev netcat \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN adduser --system datapunt

RUN mkdir -p /static && chown datapunt /static
RUN mkdir -p /src && chown datapunt /src
RUN mkdir -p /deploy && chown datapunt /deploy
RUN mkdir -p /var/log/gatekeeper && chown datapunt /var/log/gatekeeper
RUN mkdir -p /var/log/uwsgi && chown datapunt /var/log/uwsgi

# ADD "https://nexus.data.amsterdam.nl/repository/keycloak/bin/keycloak-gatekeeper.latest" /app/keycloak-gatekeeper
COPY src/lib/keycloak-gatekeeper.latest /src/keycloak-gatekeeper
RUN chmod 755 /src/keycloak-gatekeeper

WORKDIR /install
ADD requirements.txt .
RUN pip install -r requirements.txt
RUN chmod -R a+r /install

WORKDIR /src

COPY src .
COPY deploy /deploy

USER datapunt

CMD ["/deploy/docker-run.sh"]

# devserver
FROM app as dev

USER root
WORKDIR /install
ADD requirements_dev.txt .
RUN pip install -r requirements_dev.txt

WORKDIR /src
USER datapunt

# Any process that requires to write in the home dir
# we write to /tmp since we have no home dir
ENV HOME /tmp

CMD ["python manage.py runserver 0.0.0.0"]

# tests
FROM dev as tests

USER datapunt
WORKDIR /tests
ADD tests .

ENV COVERAGE_FILE=/tmp/.coverage
ENV PYTHONPATH=/src

CMD ["pytest"]
