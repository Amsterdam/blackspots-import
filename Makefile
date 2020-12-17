# This Makefile is based on the Makefile defined in the Python Best Practices repository:
# https://git.datapunt.amsterdam.nl/Datapunt/python-best-practices/blob/master/dependency_management/
.PHONY: app
dc = docker-compose
run = $(dc) run

help:                               ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

pip-tools:
	pip install pip-tools

install: pip-tools                  ## Install requirements and sync venv with expected state as defined in requirements.txt
	pip-sync requirements_dev.txt

requirements: pip-tools             ## Upgrade requirements (in requirements.in) to latest versions and compile requirements.txt
	pip-compile --upgrade --output-file requirements.txt requirements.in
	pip-compile --upgrade --output-file requirements_dev.txt requirements_dev.in

upgrade: requirements install       ## Run 'requirements' and 'install' targets

migrations:
	$(dc) run --rm app python manage.py makemigrations

migrate:
	$(dc) run --rm app python manage.py migrate

build:
	$(dc) build

push: build
	$(dc) push

push_semver:
	VERSION=$${VERSION} $(MAKE) push
	VERSION=$${VERSION%\.*} $(MAKE) push
	VERSION=$${VERSION%%\.*} $(MAKE) push

app:
	$(dc) up app

dev:
	$(run) --service-ports dev

test:
	$(run) --rm test pytest $(ARGS)

pdb:
	$(run) test pytest --pdb $(ARGS)

clean:
	$(dc) down -v

bash:
	$(run) --rm dev bash

update_stadsdeel_errors:
	$(dc) run --rm app /deploy/docker-update-stadsdelen.sh
