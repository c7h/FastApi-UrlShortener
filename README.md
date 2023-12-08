# finn_shorturl

ShortLink is a URL shortening service where you enter a URL such as https://codesubmit.io/library/react and it returns a short URL such as http://short.est/GeAi9KZZ. The api consists of 2 endpoints:

- `POST /api/encode`  
-> ```{"url": "http://gerneth.info"}```  
<- ```{"url": "http://gerneth.info"  
       "short": "http://localhost/api/Abc123XY"
}```


- `GET /api/decode/Abc123XY`  
<- ```{"url": "http://gerneth.info"  
       "short": "http://localhost/api/Abc123XY"
}```

The third route is the ressouce itself (`http://localhost/api/Abc123XY`). If the short url ressource is called and the url could be resolved in redis, a `307` redirect will be initiated.

- `GET http://localhost/api/Abc123XY`
-> `TEMPORARY REDIRECT http://gerneth.info/`


## Poetry

This project uses poetry. It's a modern dependency management
tool.

To run the project use this set of commands:

```bash
poetry install
poetry run python -m finn_shorturl
```

This will start the server on the configured host.

You can find OpenAPI documentation at http://localhost:8000/api/docs.

Also, If you are looking for redoc, take a look here: 
http://127.0.0.1:8000/api/redoc.

You can read more about poetry here: https://python-poetry.org/

## Docker

You can start the project with docker using this command:

```bash
docker-compose -f deploy/docker-compose.yml --project-directory . up --build
```

But you have to rebuild image every time you modify `poetry.lock` or `pyproject.toml` with this command:

```bash
docker-compose -f deploy/docker-compose.yml --project-directory . build
```

## Configuration

This application can be configured with environment variables.

**You can create `.env` file in the root directory and place all
environment variables here.**

All environment variables should start with "FINN_SHORTURL_" prefix.

For example if you see in your "finn_shorturl/settings.py" a variable named like
`random_parameter`, you should provide the "FINN_SHORTURL_RANDOM_PARAMETER"
variable to configure the value. This behaviour can be changed by overriding `env_prefix` property
in `finn_shorturl.settings.Settings.Config`.

An example of .env file:
```bash
FINN_SHORTURL_RELOAD="True"
FINN_SHORTURL_PORT="8000"
FINN_SHORTURL_ENVIRONMENT="dev"
FINN_SHORTURL_REDIS_HOST="localhost"
```

You can read more about BaseSettings class here: https://pydantic-docs.helpmanual.io/usage/settings/
## OpenTelemetry

If you want to start your project with OpenTelemetry collector
you can add `-f ./deploy/docker-compose.otlp.yml` to your docker command.

Like this:

```bash
docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.otlp.yml --project-directory . up
```

This command will start OpenTelemetry collector and jaeger.
After sending a requests you can see traces in jaeger's UI
at http://localhost:16686/.

This docker configuration is not supposed to be used in production.
It's only for demo purpose.

You can read more about OpenTelemetry here: https://opentelemetry.io/

## Pre-commit

Pre-commit hooks are optional, but can make developing a lot easier! You don't need to do this if you are not planning to commit anything.
To install pre-commit simply run inside the shell:
```bash
pre-commit install
```

pre-commit is very useful to check your code before publishing it.
It's configured using .pre-commit-config.yaml file.

By default it runs:
* black (formats your code);
* mypy (validates types);
* isort (sorts imports in all files);
* flake8 (spots possible bugs);


You can read more about pre-commit here: https://pre-commit.com/


## Running tests

For running tests on your local machine, first make sure you have created the `.env` file in the project root. In order to run the url shortener locally, you need to add the redis host url env vars `FINN_SHORTURL_REDIS_HOST=localhost` to a valid redis instance.

2. Run the pytest.
```bash
pytest -vv .
```
