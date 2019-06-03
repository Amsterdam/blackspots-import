# Blackspots
Backend for Blackspots/WBAkaart.


# Run


## Docker
To start just the database use

```
docker-compose up --build database
```

To get everything up use:

```
source .gatekeeper_env
docker-compose up --build
```

Note that in order to access the API through Gatekeeper you will need access to the Keycloack credentials.

* The API is available on: `<docker-host>:8001`.
* Gatekeeper is available on `<docker-host>:8000`.


## Testing

Execute the test using:

```bash
python manage.py test
```
