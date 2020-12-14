# Blackspots
The blackspots/wbakaart service exposes spots in Amsterdam which have been identified as being (potentially) accident prone.

During an import process a remote XLS file is imported to the Postgres database.
Through a Django rest framework API these spots are exposed in HAL json and geojson.
Finally the API acts as an authorization proxy for report documents belonging to a particular spot.

Authentication is done using Keycloak.
ADW users or Datapunt identity provider users can login with the Keycloak JS library (see [blackspots-frontend](https://github.com/Amsterdam/blackspots-frontend/)).
Authorization is done by passing requests through **Gatekeeper**.
The API itself is only accessible through Gatekeeper.  

# Project architecture
This project follows the setup used in multiple projects and is described here: https://github.com/Amsterdam/opdrachten_team_dev.  

# Deployments

Deployments are triggered automatically after pushing considering the following rules:

## Acceptance deployments
Jenkins will deploy to acceptance in these situations:
- Any push to master
- Any push to a release/* (pre-release branches used for final testing)
- Any pushed tag with semver formatting (x.y.z)

## Production deployments
Jenkins will deploy to production in the following situation:
- Any pushed tag with semver formatting (x.y.z) 

Note that given these rules, any semver tag that is pushed will first be deployed to ACC,
and immediately after to PROD.


# Install

```
pip install -r requirements.txt
```

Bump dependencies with:

```
pip install -r requirements-root.txt
pip freeze > requirements.txt
```

Possibly, perform the bump process in the docker container and copy out the result.
This will prevent your local workspace from introducing unrelated dependencies.


# Run

To start the database use

```
docker-compose up --build database
```

Create the Django Database structure:

```
python manage.py migrate
```

Optionally import actual data from the objectstore:

```
OBJECTSTORE_PASSWORD=foo python manage.py import_spots
``` 

Then start the Django server

```
python manage.py runserver
```

If you want to proxy file downloads also set the `OBJECTSTORE_PASSWORD` variable for the server. 

## Endpoints

The following endpoints (and more) are available:
* /health, for Consul health check
* /blackspots/spots/
* /blackspots/spots/?format=geojson
* /blackspots/documents/
* /blackspots/documents/1/, document detail view
* /blackspots/documents/1/file/, document download
* /blackspots/redoc/, rest API documentation
* /blackspots/swagger.yaml, OpenAPI specification

## Docker

Alternatively everything can be started through Docker using:

```
source .gatekeeper_env
docker-compose up --build
```

Note that in order to access the API through Gatekeeper you will need access to the Keycloak credentials.

* The API is available on: `<docker-host>:8001`.
* Gatekeeper is available on `<docker-host>:8000`.


# Testing

Execute the test using:

```bash
python manage.py test
```
