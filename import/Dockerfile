FROM amsterdam/python
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1
ARG BLACKSPOTS_OBJECTSTORE_PASSWORD
ENV BLACKSPOTS_OBJECTSTORE_PASSWORD=$BLACKSPOTS_OBJECTSTORE_PASSWORD

RUN apt-get install -y \
		gdal-bin \
		libgeos-dev \
		netcat \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
	&& adduser --system datapunt \
	&& mkdir -p /static \
	&& chown datapunt /static \
	&& pip install uwsgi

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
USER datapunt

COPY . /app/
COPY deploy /deploy/

CMD ["/deploy/docker-run.sh"]

