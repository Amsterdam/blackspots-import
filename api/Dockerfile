FROM amsterdam/python
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1
ENV CONSUL_HOST=${CONSUL_HOST:-notset}
ENV CONSUL_PORT=${CONSUL_PORT:-8500}
ENV DATAPUNT_API_URL=${DATAPUNT_API_URL:-https://api.data.amsterdam.nl/}
ARG BLACKSPOTS_OBJECTSTORE_PASSWORD
ENV BLACKSPOTS_OBJECTSTORE_PASSWORD=$BLACKSPOTS_OBJECTSTORE_PASSWORD

RUN apt-get update \
	&& apt-get install -y gdal-bin libgeos-dev netcat \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN adduser --system datapunt

RUN mkdir -p /static && chown datapunt /static
RUN mkdir -p /app && chown datapunt /app
RUN mkdir -p /deploy && chown datapunt /deploy
RUN mkdir -p /var/log/gatekeeper && chown datapunt /var/log/gatekeeper
RUN mkdir -p /var/log/uwsgi && chown datapunt /var/log/uwsgi

# ADD "https://nexus.data.amsterdam.nl/repository/keycloak/bin/keycloak-gatekeeper.latest" /app/keycloak-gatekeeper
COPY ./lib/keycloak-gatekeeper.latest /app/keycloak-gatekeeper
RUN chmod 755 /app/keycloak-gatekeeper

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
USER datapunt

COPY . /app/
COPY deploy /deploy/

CMD ["/deploy/docker-run.sh"]

