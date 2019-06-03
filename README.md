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

Note that you'll need access to the credentials used by Gatekeeper.


## Testing

Execute the test using:

```bash
python manage.py test
```
